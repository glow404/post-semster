"""训练 Baseline 2：Siamese Network + Contrastive Loss。

脚本作用：
1. 读取训练/验证图像对；
2. 训练共享编码器的孪生网络；
3. 每个 epoch 后在验证集上选择距离阈值；
4. 记录训练日志并保存验证集最优模型；
5. 输出 `best_siamese.pth`、`train_log.csv` 和 `config.json`。
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
    # Windows + Anaconda 环境中可能出现 OpenMP 运行库重复加载问题。
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

# 允许直接运行 `python src/siamese/train_siamese.py`。
SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from siamese.datasets.pair_dataset import FingerprintPairDataset
from siamese.losses.contrastive_loss import ContrastiveLoss
from siamese.models.siamese import SiameseNetwork
from utils_metrics import choose_best_distance_threshold, compute_distance_metrics


LOG_FIELDS = [
    "epoch",
    "train_loss",
    "val_loss",
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


def make_loader(
    pairs_csv: Path,
    image_root: Path,
    height: int,
    width: int,
    batch_size: int,
    num_workers: int,
    train: bool,
    random_horizontal_flip: bool = False,
) -> DataLoader:
    """创建指纹图像对 DataLoader。"""
    dataset = FingerprintPairDataset(
        pairs_csv=pairs_csv,
        image_root=image_root,
        height=height,
        width=width,
        train=train,
        random_horizontal_flip=random_horizontal_flip,
    )
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=train,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )


def train_one_epoch(
    model: SiameseNetwork,
    loader: DataLoader,
    criterion: ContrastiveLoss,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    epoch: int,
) -> float:
    """训练一个 epoch，并返回样本加权平均损失。"""
    model.train()
    total_loss = 0.0
    total_samples = 0
    progress = tqdm(loader, desc=f"Epoch {epoch} train", leave=False)

    for batch in progress:
        img1 = batch["img1"].to(device, non_blocking=True)
        img2 = batch["img2"].to(device, non_blocking=True)
        labels = batch["label"].to(device, non_blocking=True)

        # 标准训练流程：前向计算距离 -> 对比损失 -> 反向传播 -> 更新参数。
        optimizer.zero_grad(set_to_none=True)
        _, _, distances = model(img1, img2)
        loss = criterion(distances, labels)
        loss.backward()
        optimizer.step()

        batch_size = labels.size(0)
        total_loss += float(loss.item()) * batch_size
        total_samples += batch_size
        progress.set_postfix(loss=loss.item())

    return total_loss / max(total_samples, 1)


@torch.no_grad()
def evaluate(
    model: SiameseNetwork,
    loader: DataLoader,
    criterion: ContrastiveLoss,
    device: torch.device,
    threshold_grid: int,
) -> tuple[float, dict[str, object], float]:
    """在验证集上计算距离、选择最佳阈值并返回指标。"""
    model.eval()
    total_loss = 0.0
    total_samples = 0
    labels_all: list[int] = []
    distances_all: list[float] = []

    for batch in tqdm(loader, desc="Validation", leave=False):
        img1 = batch["img1"].to(device, non_blocking=True)
        img2 = batch["img2"].to(device, non_blocking=True)
        labels = batch["label"].to(device, non_blocking=True)

        _, _, distances = model(img1, img2)
        loss = criterion(distances, labels)

        batch_size = labels.size(0)
        total_loss += float(loss.item()) * batch_size
        total_samples += batch_size
        labels_all.extend(labels.detach().cpu().int().tolist())
        distances_all.extend(distances.detach().cpu().float().tolist())

    best_threshold, _ = choose_best_distance_threshold(
        labels_all,
        distances_all,
        num_grid=threshold_grid,
    )
    metrics = compute_distance_metrics(labels_all, distances_all, best_threshold)
    val_loss = total_loss / max(total_samples, 1)
    return val_loss, metrics, best_threshold


def save_json(data: dict[str, object], output_path: Path) -> None:
    """保存格式化 JSON 配置或指标文件。"""
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


def save_checkpoint(
    model: SiameseNetwork,
    output_path: Path,
    config: dict[str, object],
    epoch: int,
    best_threshold: float,
    metrics: dict[str, object],
) -> None:
    """保存模型权重、配置、最佳阈值和验证集指标。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": config,
            "epoch": epoch,
            "best_threshold": float(best_threshold),
            "val_metrics": metrics,
        },
        output_path,
    )


def parse_args() -> argparse.Namespace:
    """解析训练脚本命令行参数。"""
    parser = argparse.ArgumentParser(description="Train Siamese Network baseline.")
    parser.add_argument("--train_pairs", type=Path, default=Path("data/pairs_train.csv"))
    parser.add_argument("--val_pairs", type=Path, default=Path("data/pairs_val.csv"))
    parser.add_argument("--image_root", type=Path, default=Path("."))
    parser.add_argument("--output_dir", type=Path, default=Path("results/siamese"))
    parser.add_argument("--height", type=int, default=100)
    parser.add_argument("--width", type=int, default=110)
    parser.add_argument("--embedding_dim", type=int, default=128)
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--weight_decay", type=float, default=0.0001)
    parser.add_argument("--margin", type=float, default=1.0)
    parser.add_argument("--num_workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--threshold_grid", type=int, default=101)
    parser.add_argument(
        "--random_horizontal_flip",
        type=str_to_bool,
        default=False,
        help="Enable random horizontal flip during training. Default: false.",
    )
    return parser.parse_args()


def main() -> None:
    """脚本入口：组织数据、模型、优化器、训练循环和模型保存。"""
    args = parse_args()
    set_seed(args.seed)
    device = resolve_device(args.device)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    train_loader = make_loader(
        args.train_pairs,
        args.image_root,
        args.height,
        args.width,
        args.batch_size,
        args.num_workers,
        train=True,
        random_horizontal_flip=args.random_horizontal_flip,
    )
    val_loader = make_loader(
        args.val_pairs,
        args.image_root,
        args.height,
        args.width,
        args.batch_size,
        args.num_workers,
        train=False,
    )

    model = SiameseNetwork(embedding_dim=args.embedding_dim).to(device)
    criterion = ContrastiveLoss(margin=args.margin)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="max",
        factor=0.5,
        patience=5,
    )

    config: dict[str, object] = {
        "method": "Siamese Network + Contrastive Loss",
        "train_pairs": str(args.train_pairs),
        "val_pairs": str(args.val_pairs),
        "image_root": str(args.image_root),
        "output_dir": str(args.output_dir),
        "height": args.height,
        "width": args.width,
        "embedding_dim": args.embedding_dim,
        "batch_size": args.batch_size,
        "epochs": args.epochs,
        "lr": args.lr,
        "weight_decay": args.weight_decay,
        "margin": args.margin,
        "num_workers": args.num_workers,
        "seed": args.seed,
        "requested_device": args.device,
        "device": str(device),
        "threshold_grid": args.threshold_grid,
        "random_horizontal_flip": bool(args.random_horizontal_flip),
        "best_threshold": None,
        "best_epoch": None,
        "best_val_auc": None,
        "best_val_eer": None,
    }

    best_auc = -1.0
    best_eer = float("inf")
    best_threshold = 0.0
    log_rows: list[dict[str, object]] = []

    print(f"Training on device: {device}")
    for epoch in range(1, args.epochs + 1):
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, device, epoch)
        val_loss, val_metrics, val_threshold = evaluate(
            model,
            val_loader,
            criterion,
            device,
            threshold_grid=args.threshold_grid,
        )
        scheduler.step(float(val_metrics["roc_auc"]))
        current_lr = optimizer.param_groups[0]["lr"]

        row = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss,
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
        # 优先选择 AUC 更高的模型；AUC 相同时选择 EER 更低的模型。
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
                args.output_dir / "best_siamese.pth",
                config,
                epoch,
                best_threshold,
                val_metrics,
            )
            save_json(config, args.output_dir / "config.json")

        print(
            f"Epoch {epoch:03d}: train_loss={train_loss:.6f}, val_loss={val_loss:.6f}, "
            f"val_f1={float(val_metrics['f1']):.6f}, val_auc={val_auc:.6f}, "
            f"val_eer={val_eer:.6f}, threshold={val_threshold:.6f}"
        )

    if config["best_threshold"] is None:
        config.update(
            {
                "best_threshold": best_threshold,
                "best_epoch": args.epochs,
                "best_val_auc": best_auc,
                "best_val_eer": best_eer,
            }
        )
        save_json(config, args.output_dir / "config.json")

    print(f"Saved best model to {args.output_dir / 'best_siamese.pth'}")
    print(f"Saved training log to {args.output_dir / 'train_log.csv'}")
    print(f"Best threshold: {config['best_threshold']}")


if __name__ == "__main__":
    main()
