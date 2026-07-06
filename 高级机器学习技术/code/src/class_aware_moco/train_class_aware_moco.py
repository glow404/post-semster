"""训练 Proposed Method：Class-aware MoCo。

脚本作用：
1. 读取训练标签文件，生成同一图像的两个增强视图；
2. 使用 query encoder 和 momentum key encoder 训练类别感知 MoCo；
3. 每个 epoch 后在验证图像对上计算距离并选择阈值；
4. 按验证集 AUC/EER 保存最佳模型；
5. 输出模型、训练日志、配置文件和 label_map。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
from pathlib import Path

if sys.platform.startswith("win"):
    # 兼容 Windows + Anaconda 中常见的 OpenMP 重复加载问题。
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

# 允许直接运行 `python src/class_aware_moco/train_class_aware_moco.py`。
SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from class_aware_moco.datasets.fingerprint_dataset import (
    MoCoFingerprintDataset,
    build_label_map,
    read_label_rows,
    save_label_map,
)
from class_aware_moco.datasets.pair_dataset import MoCoPairDataset
from class_aware_moco.models.class_aware_moco import ClassAwareMoCo
from utils_metrics import choose_best_distance_threshold, compute_distance_metrics


LOG_FIELDS = [
    "epoch",
    "train_loss",
    "val_accuracy",
    "val_precision",
    "val_recall",
    "val_f1",
    "val_auc",
    "val_eer",
    "val_threshold",
    "lr",
]


def str_to_bool(value: str) -> bool:
    """将命令行字符串解析为布尔值。"""
    lowered = value.strip().lower()
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def set_seed(seed: int) -> None:
    """设置随机种子，尽量保证实验可复现。"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def resolve_device(device_arg: str) -> torch.device:
    """解析训练设备；请求 CUDA 但不可用时自动退回 CPU。"""
    if device_arg == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device_arg.startswith("cuda") and not torch.cuda.is_available():
        print("Warning: CUDA is unavailable; falling back to CPU.", file=sys.stderr)
        return torch.device("cpu")
    return torch.device(device_arg)


def save_json(data: dict[str, object], output_path: Path) -> None:
    """保存格式化 JSON 文件。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def write_train_log(rows: list[dict[str, object]], output_csv: Path) -> None:
    """将每个 epoch 的训练和验证指标写入 CSV。"""
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=LOG_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def make_label_map(train_labels: Path, all_labels: Path | None) -> dict[str, int]:
    """优先基于全量标签生成 label_map，缺失时回退到训练标签。"""
    source = all_labels if all_labels is not None and all_labels.exists() else train_labels
    return build_label_map(read_label_rows(source))


def make_train_loader(
    train_labels: Path,
    image_root: Path,
    label_map: dict[str, int],
    height: int,
    width: int,
    batch_size: int,
    num_workers: int,
    random_horizontal_flip: bool,
    blur_prob: float,
) -> DataLoader:
    """创建 MoCo 单图像训练 DataLoader。"""
    dataset = MoCoFingerprintDataset(
        label_csv=train_labels,
        image_root=image_root,
        label_map=label_map,
        height=height,
        width=width,
        random_horizontal_flip=random_horizontal_flip,
        blur_prob=blur_prob,
    )
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=False,
    )


def make_pair_loader(
    pairs_csv: Path,
    image_root: Path,
    height: int,
    width: int,
    batch_size: int,
    num_workers: int,
) -> DataLoader:
    """创建验证图像对 DataLoader。"""
    dataset = MoCoPairDataset(
        pairs_csv=pairs_csv,
        image_root=image_root,
        height=height,
        width=width,
    )
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )


def train_one_epoch(
    model: ClassAwareMoCo,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    epoch: int,
) -> float:
    """训练 Class-aware MoCo 一个 epoch，并返回平均损失。"""
    model.train()
    total_loss = 0.0
    total_samples = 0
    progress = tqdm(loader, desc=f"Epoch {epoch} train", leave=False)

    for batch in progress:
        view1 = batch["view1"].to(device, non_blocking=True)
        view2 = batch["view2"].to(device, non_blocking=True)
        labels = batch["label"].to(device, non_blocking=True)

        # view1 作为 query，view2 作为 key；模型内部会动量更新 key encoder 并维护队列。
        optimizer.zero_grad(set_to_none=True)
        loss, _, _ = model(view1, view2, labels)
        loss.backward()
        optimizer.step()

        batch_size = labels.size(0)
        total_loss += float(loss.item()) * batch_size
        total_samples += batch_size
        progress.set_postfix(loss=loss.item())

    return total_loss / max(total_samples, 1)


@torch.no_grad()
def evaluate_pairs(
    model: ClassAwareMoCo,
    loader: DataLoader,
    device: torch.device,
    threshold_grid: int,
) -> tuple[dict[str, object], float]:
    """在验证图像对上计算距离、选择阈值并返回指标。"""
    model.eval()
    labels_all: list[int] = []
    distances_all: list[float] = []

    for batch in tqdm(loader, desc="Validation", leave=False):
        img1 = batch["img1"].to(device, non_blocking=True)
        img2 = batch["img2"].to(device, non_blocking=True)
        labels = batch["label"].detach().cpu().int().tolist()

        # 训练后的 encoder_q 用于提取图像表示，再用欧氏距离进行指纹验证。
        emb1 = model.encode(img1)
        emb2 = model.encode(img2)
        distances = torch.sqrt(torch.sum((emb1 - emb2) ** 2, dim=1) + 1e-8)

        labels_all.extend(labels)
        distances_all.extend(distances.detach().cpu().float().tolist())

    best_threshold, _ = choose_best_distance_threshold(
        labels_all,
        distances_all,
        num_grid=threshold_grid,
    )
    metrics = compute_distance_metrics(labels_all, distances_all, best_threshold)
    return metrics, best_threshold


def save_checkpoint(
    model: ClassAwareMoCo,
    output_path: Path,
    config: dict[str, object],
    label_map: dict[str, int],
    epoch: int,
    best_threshold: float,
    metrics: dict[str, object],
) -> None:
    """保存模型权重、配置、label_map、最佳阈值和验证指标。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": config,
            "label_map": label_map,
            "epoch": epoch,
            "best_threshold": float(best_threshold),
            "val_metrics": metrics,
        },
        output_path,
    )


def parse_args() -> argparse.Namespace:
    """解析训练脚本命令行参数。"""
    parser = argparse.ArgumentParser(description="Train Class-aware MoCo.")
    parser.add_argument("--train_labels", type=Path, default=Path("data/labels_train.csv"))
    parser.add_argument("--val_pairs", type=Path, default=Path("data/pairs_val.csv"))
    parser.add_argument("--all_labels", type=Path, default=Path("data/labels.csv"))
    parser.add_argument("--image_root", type=Path, default=Path("."))
    parser.add_argument("--output_dir", type=Path, default=Path("results/class_aware_moco"))
    parser.add_argument("--height", type=int, default=100)
    parser.add_argument("--width", type=int, default=110)
    parser.add_argument("--embedding_dim", type=int, default=128)
    parser.add_argument("--queue_size", type=int, default=4096)
    parser.add_argument("--momentum", type=float, default=0.999)
    parser.add_argument("--temperature", type=float, default=0.07)
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--weight_decay", type=float, default=0.0001)
    parser.add_argument("--num_workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--threshold_grid", type=int, default=101)
    parser.add_argument("--blur_prob", type=float, default=0.2)
    parser.add_argument(
        "--random_horizontal_flip",
        type=str_to_bool,
        default=False,
        help="Enable random horizontal flip during training. Default: false.",
    )
    return parser.parse_args()


def main() -> None:
    """脚本入口：组织数据、模型、训练循环、验证和最佳模型保存。"""
    args = parse_args()
    set_seed(args.seed)
    device = resolve_device(args.device)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # label_map 将字符串 finger_id 映射为整数，队列标签和报告都依赖它。
    label_map = make_label_map(args.train_labels, args.all_labels)
    save_label_map(label_map, args.output_dir / "label_map.json")

    train_loader = make_train_loader(
        args.train_labels,
        args.image_root,
        label_map,
        args.height,
        args.width,
        args.batch_size,
        args.num_workers,
        args.random_horizontal_flip,
        args.blur_prob,
    )
    val_loader = make_pair_loader(
        args.val_pairs,
        args.image_root,
        args.height,
        args.width,
        args.batch_size,
        args.num_workers,
    )

    model = ClassAwareMoCo(
        embedding_dim=args.embedding_dim,
        queue_size=args.queue_size,
        momentum=args.momentum,
        temperature=args.temperature,
    ).to(device)
    optimizer = torch.optim.AdamW(model.encoder_q.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(args.epochs, 1))

    config: dict[str, object] = {
        "method": "Class-aware MoCo",
        "train_labels": str(args.train_labels),
        "val_pairs": str(args.val_pairs),
        "all_labels": str(args.all_labels),
        "image_root": str(args.image_root),
        "output_dir": str(args.output_dir),
        "height": args.height,
        "width": args.width,
        "embedding_dim": args.embedding_dim,
        "queue_size": args.queue_size,
        "momentum": args.momentum,
        "temperature": args.temperature,
        "batch_size": args.batch_size,
        "epochs": args.epochs,
        "lr": args.lr,
        "weight_decay": args.weight_decay,
        "num_workers": args.num_workers,
        "seed": args.seed,
        "requested_device": args.device,
        "device": str(device),
        "threshold_grid": args.threshold_grid,
        "blur_prob": args.blur_prob,
        "random_horizontal_flip": bool(args.random_horizontal_flip),
        "num_classes": len(label_map),
        "best_threshold": None,
        "best_epoch": None,
        "best_val_auc": None,
        "best_val_eer": None,
    }
    save_json(config, args.output_dir / "config.json")

    best_auc = -1.0
    best_eer = float("inf")
    best_threshold = 0.0
    log_rows: list[dict[str, object]] = []

    print(f"Training on device: {device}")
    for epoch in range(1, args.epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, device, epoch)
        val_metrics, val_threshold = evaluate_pairs(model, val_loader, device, args.threshold_grid)
        scheduler.step()
        current_lr = optimizer.param_groups[0]["lr"]

        row = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_accuracy": val_metrics["accuracy"],
            "val_precision": val_metrics["precision"],
            "val_recall": val_metrics["recall"],
            "val_f1": val_metrics["f1"],
            "val_auc": val_metrics["roc_auc"],
            "val_eer": val_metrics["eer"],
            "val_threshold": val_threshold,
            "lr": current_lr,
        }
        log_rows.append(row)
        write_train_log(log_rows, args.output_dir / "train_log.csv")

        val_auc = float(val_metrics["roc_auc"])
        val_eer = float(val_metrics["eer"])
        # 优先保存 AUC 更高的模型；AUC 相同时选择 EER 更低的模型。
        is_better = val_auc > best_auc or (np.isclose(val_auc, best_auc) and val_eer < best_eer)
        if is_better:
            best_auc = val_auc
            best_eer = val_eer
            best_threshold = float(val_threshold)
            config.update(
                {
                    "best_threshold": best_threshold,
                    "best_epoch": epoch,
                    "best_val_auc": best_auc,
                    "best_val_eer": best_eer,
                }
            )
            save_checkpoint(
                model,
                args.output_dir / "best_class_aware_moco.pth",
                config,
                label_map,
                epoch,
                best_threshold,
                val_metrics,
            )
            save_json(config, args.output_dir / "config.json")

        print(
            f"Epoch {epoch:03d}: train_loss={train_loss:.6f}, "
            f"val_f1={float(val_metrics['f1']):.6f}, val_auc={val_auc:.6f}, "
            f"val_eer={val_eer:.6f}, threshold={val_threshold:.6f}"
        )

    print(f"Saved best model to {args.output_dir / 'best_class_aware_moco.pth'}")
    print(f"Saved training log to {args.output_dir / 'train_log.csv'}")
    print(f"Best threshold: {config['best_threshold']}")


if __name__ == "__main__":
    main()
