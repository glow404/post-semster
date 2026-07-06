"""评估训练好的 Class-aware MoCo 模型。

脚本作用：
1. 加载 `best_class_aware_moco.pth`；
2. 读取测试集图像对；
3. 使用训练后的 encoder_q 提取图像 embedding；
4. 计算图像对欧氏距离并按验证阈值分类；
5. 保存测试分数、评价指标和 ROC 曲线。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

if sys.platform.startswith("win"):
    # 兼容 Windows + Anaconda 中常见的 OpenMP 重复加载问题。
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

# 允许直接运行 `python src/class_aware_moco/eval_class_aware_moco.py`。
SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from class_aware_moco.datasets.pair_dataset import MoCoPairDataset
from class_aware_moco.models.class_aware_moco import ClassAwareMoCo
from utils_metrics import compute_distance_metrics, predictions_from_distances, save_roc_curve


SCORE_FIELDS = ["img1", "img2", "label", "distance", "pred", "finger_id1", "finger_id2"]


def resolve_device(device_arg: str) -> torch.device:
    """解析评估设备；CUDA 不可用时自动退回 CPU。"""
    if device_arg == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device_arg.startswith("cuda") and not torch.cuda.is_available():
        print("Warning: CUDA is unavailable; falling back to CPU.", file=sys.stderr)
        return torch.device("cpu")
    return torch.device(device_arg)


def load_json(path: Path) -> dict[str, object]:
    """读取 JSON 文件。"""
    if not path.exists():
        raise FileNotFoundError(f"JSON file does not exist: {path}")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data: dict[str, object], path: Path) -> None:
    """保存 JSON 文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_checkpoint(path: Path, device: torch.device) -> dict[str, object]:
    """加载 PyTorch checkpoint，并兼容不同 torch 版本。"""
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint does not exist: {path}")
    try:
        return torch.load(path, map_location=device, weights_only=False)
    except TypeError:
        return torch.load(path, map_location=device)


def write_scores(rows: list[dict[str, object]], output_csv: Path) -> None:
    """将测试距离和预测标签写入 CSV。"""
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=SCORE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


@torch.no_grad()
def predict_distances(model: ClassAwareMoCo, loader: DataLoader, device: torch.device) -> list[dict[str, object]]:
    """批量计算所有测试图像对的 embedding 距离。"""
    model.eval()
    rows: list[dict[str, object]] = []

    for batch in tqdm(loader, desc="Testing", leave=False):
        img1 = batch["img1"].to(device, non_blocking=True)
        img2 = batch["img2"].to(device, non_blocking=True)
        labels = batch["label"].detach().cpu().int().tolist()

        # 使用 encoder_q 提取表示；距离越小，越可能是同一根手指。
        emb1 = model.encode(img1)
        emb2 = model.encode(img2)
        distances = torch.sqrt(torch.sum((emb1 - emb2) ** 2, dim=1) + 1e-8)
        distance_values = distances.detach().cpu().float().tolist()

        for img1_path, img2_path, label, distance, finger_id1, finger_id2 in zip(
            batch["img1_path"],
            batch["img2_path"],
            labels,
            distance_values,
            batch["finger_id1"],
            batch["finger_id2"],
        ):
            rows.append(
                {
                    "img1": img1_path,
                    "img2": img2_path,
                    "label": int(label),
                    "distance": float(distance),
                    "pred": -1,
                    "finger_id1": finger_id1,
                    "finger_id2": finger_id2,
                }
            )

    return rows


def parse_args() -> argparse.Namespace:
    """解析测试脚本命令行参数。"""
    parser = argparse.ArgumentParser(description="Evaluate Class-aware MoCo.")
    parser.add_argument("--test_pairs", type=Path, default=Path("data/pairs_test.csv"))
    parser.add_argument("--image_root", type=Path, default=Path("."))
    parser.add_argument("--checkpoint", type=Path, default=Path("results/class_aware_moco/best_class_aware_moco.pth"))
    parser.add_argument("--output_dir", type=Path, default=Path("results/class_aware_moco"))
    parser.add_argument("--height", type=int, default=100)
    parser.add_argument("--width", type=int, default=110)
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--num_workers", type=int, default=4)
    parser.add_argument("--device", type=str, default="cuda")
    return parser.parse_args()


def main() -> None:
    """脚本入口：加载模型、计算测试距离、保存指标和 ROC 曲线。"""
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    device = resolve_device(args.device)

    checkpoint = load_checkpoint(args.checkpoint, device)
    config_path = args.output_dir / "config.json"
    config = load_json(config_path) if config_path.exists() else checkpoint.get("config", {})
    if not isinstance(config, dict):
        config = {}

    # 阈值必须来自验证集，测试集只做最终评价。
    best_threshold = config.get("best_threshold", checkpoint.get("best_threshold"))
    if best_threshold is None:
        raise ValueError("best_threshold is missing. Please run train_class_aware_moco.py first.")
    best_threshold = float(best_threshold)

    model = ClassAwareMoCo(
        embedding_dim=int(config.get("embedding_dim", 128)),
        queue_size=int(config.get("queue_size", 4096)),
        momentum=float(config.get("momentum", 0.999)),
        temperature=float(config.get("temperature", 0.07)),
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])

    dataset = MoCoPairDataset(
        pairs_csv=args.test_pairs,
        image_root=args.image_root,
        height=args.height,
        width=args.width,
    )
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available(),
    )

    print(f"Evaluating on device: {device}")
    rows = predict_distances(model, loader, device)
    labels = [int(row["label"]) for row in rows]
    distances = [float(row["distance"]) for row in rows]
    preds = predictions_from_distances(distances, best_threshold)
    for row, pred in zip(rows, preds.tolist()):
        row["pred"] = int(pred)

    write_scores(rows, args.output_dir / "test_scores.csv")
    metrics = compute_distance_metrics(labels, distances, best_threshold)
    metrics_json = {
        "method": "Class-aware MoCo",
        "best_threshold": best_threshold,
        **metrics,
    }
    save_json(metrics_json, args.output_dir / "metrics.json")
    save_roc_curve(
        labels,
        [-distance for distance in distances],
        args.output_dir / "roc_curve.png",
        title="Class-aware MoCo ROC Curve",
    )

    config.update(
        {
            "test_pairs": str(args.test_pairs),
            "checkpoint": str(args.checkpoint),
            "eval_device": str(device),
            "best_threshold": best_threshold,
        }
    )
    save_json(config, args.output_dir / "config.json")

    print("Test metrics:")
    for key in ["accuracy", "precision", "recall", "f1", "roc_auc", "eer"]:
        print(f"{key}: {metrics_json[key]:.6f}")
    print(f"confusion_matrix: {metrics_json['confusion_matrix']}")
    print(f"Saved results to {args.output_dir}")


if __name__ == "__main__":
    main()
