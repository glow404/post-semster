"""按手指身份划分数据集，并构造指纹验证图像对。

脚本作用：
1. 读取 `labels.csv`；
2. 按 `finger_id` 划分训练集、验证集和测试集；
3. 在每个划分内部构造正负样本对；
4. 输出 `labels_train/val/test.csv` 和 `pairs_train/val/test.csv`。

关键约束：必须按 `finger_id` 划分，而不是按图像随机划分，避免同一根手指泄露到不同数据集。
"""

from __future__ import annotations

import argparse
import csv
import itertools
import random
import sys
from pathlib import Path


LABEL_FIELDS = ["image_path", "finger_id"]
PAIR_FIELDS = ["img1", "img2", "label", "finger_id1", "finger_id2"]


def read_labels(label_csv: Path) -> list[dict[str, str]]:
    """读取标签 CSV，并检查是否包含必须字段。"""
    if not label_csv.exists():
        raise FileNotFoundError(f"Label CSV does not exist: {label_csv}")

    with label_csv.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError(f"Empty CSV: {label_csv}")
        missing = [field for field in LABEL_FIELDS if field not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing columns in {label_csv}: {missing}")
        rows = [
            {"image_path": row["image_path"], "finger_id": row["finger_id"]}
            for row in reader
            if row.get("image_path") and row.get("finger_id")
        ]

    if not rows:
        raise ValueError(f"No valid label rows found in {label_csv}")
    return rows


def group_by_finger(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    """按照 finger_id 将图像路径分组。"""
    grouped: dict[str, list[str]] = {}
    for row in rows:
        grouped.setdefault(row["finger_id"], []).append(row["image_path"])
    for finger_id in grouped:
        grouped[finger_id] = sorted(set(grouped[finger_id]))
    return dict(sorted(grouped.items(), key=lambda item: item[0].lower()))


def split_finger_ids(
    finger_ids: list[str],
    train_ratio: float,
    val_ratio: float,
    test_ratio: float,
    seed: int,
) -> dict[str, list[str]]:
    """按 finger_id 划分训练、验证和测试集合。"""
    if not finger_ids:
        raise ValueError("No finger_id values available for splitting.")
    if min(train_ratio, val_ratio, test_ratio) < 0:
        raise ValueError("Split ratios must be non-negative.")
    ratio_sum = train_ratio + val_ratio + test_ratio
    if ratio_sum <= 0:
        raise ValueError("At least one split ratio must be positive.")

    normalized_train = train_ratio / ratio_sum
    normalized_val = val_ratio / ratio_sum

    # 固定随机种子，保证课程报告中的实验划分可以复现。
    shuffled = finger_ids[:]
    random.Random(seed).shuffle(shuffled)

    train_count = int(len(shuffled) * normalized_train)
    val_count = int(len(shuffled) * normalized_val)
    test_count = len(shuffled) - train_count - val_count

    for name, count, ratio in [
        ("train", train_count, train_ratio),
        ("val", val_count, val_ratio),
        ("test", test_count, test_ratio),
    ]:
        if ratio > 0 and count == 0:
            print(
                f"Warning: split '{name}' has 0 finger_id values because the dataset is small.",
                file=sys.stderr,
            )

    return {
        "train": sorted(shuffled[:train_count]),
        "val": sorted(shuffled[train_count : train_count + val_count]),
        "test": sorted(shuffled[train_count + val_count :]),
    }


def rows_for_ids(grouped: dict[str, list[str]], finger_ids: list[str]) -> list[dict[str, str]]:
    """根据选中的 finger_id 生成对应划分的标签行。"""
    rows: list[dict[str, str]] = []
    for finger_id in finger_ids:
        for image_path in grouped[finger_id]:
            rows.append({"image_path": image_path, "finger_id": finger_id})
    return rows


def write_csv(rows: list[dict[str, str]], output_csv: Path, fieldnames: list[str]) -> None:
    """使用固定表头写入 CSV，保证后续脚本读取字段一致。"""
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sample_positive_pairs(
    grouped: dict[str, list[str]],
    rng: random.Random,
    max_pos_pairs_per_finger: int,
) -> list[dict[str, str]]:
    """在同一个 finger_id 内采样正样本对。"""
    pairs: list[dict[str, str]] = []
    for finger_id, images in grouped.items():
        if len(images) < 2:
            print(
                f"Warning: finger_id '{finger_id}' has fewer than 2 images; no positive pair is created.",
                file=sys.stderr,
            )
            continue

        # 正样本来自同一根手指；组合数可能很大，因此支持上限采样。
        combinations = list(itertools.combinations(images, 2))
        if max_pos_pairs_per_finger > 0 and len(combinations) > max_pos_pairs_per_finger:
            combinations = rng.sample(combinations, max_pos_pairs_per_finger)

        for img1, img2 in combinations:
            pairs.append(
                {
                    "img1": img1,
                    "img2": img2,
                    "label": "1",
                    "finger_id1": finger_id,
                    "finger_id2": finger_id,
                }
            )
    return pairs


def sample_negative_pairs(
    grouped: dict[str, list[str]],
    rng: random.Random,
    target_count: int,
) -> list[dict[str, str]]:
    """从不同 finger_id 之间采样负样本对。"""
    finger_ids = [finger_id for finger_id, images in grouped.items() if images]
    if len(finger_ids) < 2 or target_count <= 0:
        if len(finger_ids) < 2:
            print("Warning: fewer than 2 finger_id values; no negative pairs can be created.", file=sys.stderr)
        return []

    total_possible = 0
    for idx, finger_id1 in enumerate(finger_ids):
        for finger_id2 in finger_ids[idx + 1 :]:
            total_possible += len(grouped[finger_id1]) * len(grouped[finger_id2])

    if target_count > total_possible:
        print(
            f"Warning: requested {target_count} negative pairs but only {total_possible} are possible.",
            file=sys.stderr,
        )
        target_count = total_possible

    pairs: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    max_attempts = max(target_count * 20, 1000)
    attempts = 0

    # 随机采样负样本，同时用 seen 避免重复图像对。
    while len(pairs) < target_count and attempts < max_attempts:
        attempts += 1
        finger_id1, finger_id2 = rng.sample(finger_ids, 2)
        img1 = rng.choice(grouped[finger_id1])
        img2 = rng.choice(grouped[finger_id2])
        key = tuple(sorted((img1, img2)))
        if key in seen:
            continue
        seen.add(key)
        pairs.append(
            {
                "img1": img1,
                "img2": img2,
                "label": "0",
                "finger_id1": finger_id1,
                "finger_id2": finger_id2,
            }
        )

    if len(pairs) < target_count:
        print(
            f"Warning: sampled {len(pairs)} negative pairs, fewer than requested {target_count}.",
            file=sys.stderr,
        )
    return pairs


def make_pairs_for_split(
    rows: list[dict[str, str]],
    pos_neg_ratio: float,
    seed: int,
    max_pos_pairs_per_finger: int,
) -> list[dict[str, str]]:
    """为单个划分构造正负比例接近指定值的图像对。"""
    if pos_neg_ratio < 0:
        raise ValueError("--pos_neg_ratio must be non-negative.")

    rng = random.Random(seed)
    grouped = group_by_finger(rows)
    # 先确定正样本数量，再按比例采样负样本，尽量保持 1:1。
    positive_pairs = sample_positive_pairs(grouped, rng, max_pos_pairs_per_finger)
    negative_target = int(round(len(positive_pairs) * pos_neg_ratio))
    negative_pairs = sample_negative_pairs(grouped, rng, negative_target)

    pairs = positive_pairs + negative_pairs
    rng.shuffle(pairs)
    return pairs


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="Split labels by finger_id and create verification pairs."
    )
    parser.add_argument("--label_csv", type=Path, required=True, help="Input labels.csv path.")
    parser.add_argument("--output_dir", type=Path, required=True, help="Output directory.")
    parser.add_argument("--train_ratio", type=float, default=0.7, help="Train finger_id ratio.")
    parser.add_argument("--val_ratio", type=float, default=0.15, help="Validation finger_id ratio.")
    parser.add_argument("--test_ratio", type=float, default=0.15, help="Test finger_id ratio.")
    parser.add_argument(
        "--pos_neg_ratio",
        type=float,
        default=1.0,
        help="Number of negative pairs per positive pair. Default: 1.0.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--max_pos_pairs_per_finger",
        type=int,
        default=200,
        help="Maximum positive pairs sampled per finger_id. Use 0 to keep all pairs.",
    )
    return parser.parse_args()


def main() -> None:
    """脚本入口：完成身份划分，并为每个划分生成图像对。"""
    args = parse_args()
    rows = read_labels(args.label_csv)
    grouped = group_by_finger(rows)
    splits = split_finger_ids(
        list(grouped.keys()),
        args.train_ratio,
        args.val_ratio,
        args.test_ratio,
        args.seed,
    )

    print(f"Total finger_id values: {len(grouped)}")
    for split_name, finger_ids in splits.items():
        split_rows = rows_for_ids(grouped, finger_ids)
        write_csv(split_rows, args.output_dir / f"labels_{split_name}.csv", LABEL_FIELDS)

        split_pairs = make_pairs_for_split(
            split_rows,
            pos_neg_ratio=args.pos_neg_ratio,
            seed=args.seed + {"train": 0, "val": 1, "test": 2}[split_name],
            max_pos_pairs_per_finger=args.max_pos_pairs_per_finger,
        )
        write_csv(split_pairs, args.output_dir / f"pairs_{split_name}.csv", PAIR_FIELDS)

        pos_count = sum(1 for pair in split_pairs if pair["label"] == "1")
        neg_count = sum(1 for pair in split_pairs if pair["label"] == "0")
        print(
            f"{split_name}: finger_ids={len(finger_ids)}, images={len(split_rows)}, "
            f"positive_pairs={pos_count}, negative_pairs={neg_count}"
        )


if __name__ == "__main__":
    main()
