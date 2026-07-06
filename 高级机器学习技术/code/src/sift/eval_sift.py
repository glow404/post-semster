"""评估 Baseline 1：SIFT + Matching。

脚本作用：
1. 读取验证集和测试集图像对；
2. 对每个图像对计算 SIFT 匹配相似度分数；
3. 在验证集上选择 F1 最高的阈值；
4. 使用该阈值在测试集上计算指标；
5. 保存分数 CSV、指标 JSON、ROC 曲线和配置文件。
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

# 允许直接运行 `python src/sift/eval_sift.py`，同时还能导入 src 下的公共工具。
SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sift.sift_match import compute_sift_score, create_sift, str_to_bool
from utils_metrics import choose_best_threshold, compute_metrics, predictions_from_scores, save_roc_curve


PAIR_FIELDS = ["img1", "img2", "label", "finger_id1", "finger_id2"]
SCORE_FIELDS = ["img1", "img2", "label", "score", "pred", "finger_id1", "finger_id2"]


def read_pairs(pair_csv: Path) -> list[dict[str, str]]:
    """读取图像对 CSV，并检查字段是否完整。"""
    if not pair_csv.exists():
        raise FileNotFoundError(f"Pair CSV does not exist: {pair_csv}")

    with pair_csv.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError(f"Empty CSV: {pair_csv}")
        missing = [field for field in PAIR_FIELDS if field not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing columns in {pair_csv}: {missing}")
        rows = [
            {field: row[field] for field in PAIR_FIELDS}
            for row in reader
            if row.get("img1") and row.get("img2") and row.get("label")
        ]

    if not rows:
        raise ValueError(f"No valid pair rows found in {pair_csv}")
    return rows


def resolve_image_path(image_root: Path, image_path: str) -> Path:
    """将 CSV 中的相对图像路径拼接到 image_root 下。"""
    path = Path(image_path)
    if path.is_absolute():
        return path
    return image_root / path


def write_scores(rows: list[dict[str, object]], output_csv: Path) -> None:
    """将每个图像对的分数和预测结果写入 CSV。"""
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=SCORE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def score_pairs(
    pair_rows: list[dict[str, str]],
    image_root: Path,
    use_clahe: bool,
    use_ransac: bool,
    ratio: float,
    ransac_reproj_threshold: float,
) -> list[dict[str, object]]:
    """批量计算图像对的 SIFT 相似度分数。"""
    # SIFT 提取器创建一次即可复用，避免每个图像对重复初始化。
    sift = create_sift()
    scored_rows: list[dict[str, object]] = []
    read_failures = 0
    zero_keypoint_pairs = 0

    for index, row in enumerate(pair_rows, start=1):
        img1_path = resolve_image_path(image_root, row["img1"])
        img2_path = resolve_image_path(image_root, row["img2"])
        try:
            # 任一图像读取失败时，该图像对分数置 0，并继续处理后续样本。
            result = compute_sift_score(
                img1_path,
                img2_path,
                use_clahe=use_clahe,
                use_ransac=use_ransac,
                ratio=ratio,
                ransac_reproj_threshold=ransac_reproj_threshold,
                sift=sift,
            )
            score = result.score
            if result.num_keypoints_img1 == 0 or result.num_keypoints_img2 == 0:
                zero_keypoint_pairs += 1
        except ValueError as exc:
            read_failures += 1
            score = 0.0
            print(f"Warning: {exc}. Pair score is set to 0.", file=sys.stderr)

        scored_rows.append(
            {
                "img1": row["img1"],
                "img2": row["img2"],
                "label": int(row["label"]),
                "score": float(score),
                "pred": -1,
                "finger_id1": row["finger_id1"],
                "finger_id2": row["finger_id2"],
            }
        )

        if index % 500 == 0:
            print(f"Scored {index}/{len(pair_rows)} pairs.")

    if read_failures > 0:
        print(f"Warning: {read_failures} pairs had unreadable images.", file=sys.stderr)
    if zero_keypoint_pairs > 0:
        print(f"Info: {zero_keypoint_pairs} pairs had at least one image with zero SIFT keypoints.")
    return scored_rows


def attach_predictions(rows: list[dict[str, object]], threshold: float) -> None:
    """根据验证集选出的阈值，为分数行补充预测标签。"""
    scores = [float(row["score"]) for row in rows]
    preds = predictions_from_scores(scores, threshold)
    for row, pred in zip(rows, preds.tolist()):
        row["pred"] = int(pred)


def save_json(data: dict[str, object], output_path: Path) -> None:
    """保存格式化 JSON，便于课程报告读取结果。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def parse_args() -> argparse.Namespace:
    """解析 SIFT 评估所需的命令行参数。"""
    parser = argparse.ArgumentParser(description="Evaluate SIFT + Matching baseline.")
    parser.add_argument("--val_pairs", type=Path, required=True, help="Validation pairs CSV.")
    parser.add_argument("--test_pairs", type=Path, required=True, help="Test pairs CSV.")
    parser.add_argument("--image_root", type=Path, default=Path("."), help="Base path for relative image paths.")
    parser.add_argument("--output_dir", type=Path, required=True, help="Output directory.")
    parser.add_argument("--use_clahe", type=str_to_bool, default=True, help="Apply CLAHE. Default: true.")
    parser.add_argument("--use_ransac", type=str_to_bool, default=True, help="Apply RANSAC. Default: true.")
    parser.add_argument("--ratio", type=float, default=0.75, help="Lowe ratio threshold.")
    parser.add_argument(
        "--ransac_reproj_threshold",
        type=float,
        default=5.0,
        help="RANSAC reprojection threshold.",
    )
    parser.add_argument(
        "--threshold_grid",
        type=int,
        default=101,
        help="Number of grid thresholds between 0 and 1.",
    )
    return parser.parse_args()


def main() -> None:
    """脚本入口：完成验证集选阈值和测试集评价。"""
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("Scoring validation pairs...")
    val_pairs = read_pairs(args.val_pairs)
    val_rows = score_pairs(
        val_pairs,
        image_root=args.image_root,
        use_clahe=args.use_clahe,
        use_ransac=args.use_ransac,
        ratio=args.ratio,
        ransac_reproj_threshold=args.ransac_reproj_threshold,
    )
    val_labels = [int(row["label"]) for row in val_rows]
    val_scores = [float(row["score"]) for row in val_rows]
    best_threshold, best_val_f1 = choose_best_threshold(
        val_labels,
        val_scores,
        num_grid=args.threshold_grid,
    )
    attach_predictions(val_rows, best_threshold)
    write_scores(val_rows, args.output_dir / "val_scores.csv")

    print(f"Best threshold from validation set: {best_threshold:.6f}")
    print(f"Best validation F1: {best_val_f1:.6f}")

    print("Scoring test pairs...")
    test_pairs = read_pairs(args.test_pairs)
    test_rows = score_pairs(
        test_pairs,
        image_root=args.image_root,
        use_clahe=args.use_clahe,
        use_ransac=args.use_ransac,
        ratio=args.ratio,
        ransac_reproj_threshold=args.ransac_reproj_threshold,
    )
    attach_predictions(test_rows, best_threshold)
    write_scores(test_rows, args.output_dir / "test_scores.csv")

    test_labels = [int(row["label"]) for row in test_rows]
    test_scores = [float(row["score"]) for row in test_rows]
    metrics = compute_metrics(test_labels, test_scores, best_threshold)
    metrics_json = {
        "method": "SIFT + Matching",
        "best_threshold": float(best_threshold),
        **metrics,
    }
    save_json(metrics_json, args.output_dir / "metrics.json")
    save_roc_curve(test_labels, test_scores, args.output_dir / "roc_curve.png")

    config = {
        "method": "SIFT + Matching",
        "val_pairs": str(args.val_pairs),
        "test_pairs": str(args.test_pairs),
        "image_root": str(args.image_root),
        "output_dir": str(args.output_dir),
        "use_clahe": bool(args.use_clahe),
        "use_ransac": bool(args.use_ransac),
        "ratio": float(args.ratio),
        "ransac_reproj_threshold": float(args.ransac_reproj_threshold),
        "threshold_grid": int(args.threshold_grid),
    }
    save_json(config, args.output_dir / "config.json")

    print("Test metrics:")
    for key in ["accuracy", "precision", "recall", "f1", "roc_auc", "eer"]:
        print(f"{key}: {metrics_json[key]:.6f}")
    print(f"confusion_matrix: {metrics_json['confusion_matrix']}")
    print(f"Saved results to {args.output_dir}")


if __name__ == "__main__":
    main()
