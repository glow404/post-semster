"""从文件夹名自动生成指纹图像标签文件。

脚本作用：
1. 扫描 `--data_root` 下的 finger_id 文件夹；
2. 将每个 finger_id 文件夹名作为标签；
3. 递归收集该文件夹下所有支持格式的图像；
4. 生成 `image_path,finger_id` 两列的 `labels.csv`。

目录支持：
- 扁平结构：`data_root/dy_L0/*.bmp`
- 嵌套结构：`data_root/butieping/dy_R0/Rgd1245/*.bmp`

注意：输出路径默认保存为相对路径，便于在 Windows 和 Linux 上复现实验。
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
IGNORED_NAMES = {"__MACOSX", ".DS_Store"}


def str_to_bool(value: str) -> bool:
    """将命令行传入的字符串解析为布尔值。"""
    lowered = value.strip().lower()
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def is_ignored_path(path: Path) -> bool:
    """判断某个路径是否应被忽略，如隐藏文件、`.DS_Store` 或 `__MACOSX`。"""
    return path.name in IGNORED_NAMES or path.name.startswith(".")


def to_posix_relative(path: Path, base: Path) -> str:
    """将图像路径转换成 POSIX 风格相对路径，避免 Windows 反斜杠影响 CSV 复用。"""
    try:
        rel_path = path.resolve().relative_to(base.resolve())
    except ValueError:
        rel_path = path.resolve()
    return rel_path.as_posix()


def is_image_file(path: Path) -> bool:
    """判断路径是否为支持的图像文件。"""
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS and not is_ignored_path(path)


def iter_images(finger_dir: Path) -> list[Path]:
    """递归收集某个 finger_id 目录下的所有图像文件。"""
    images = [path for path in finger_dir.rglob("*") if is_image_file(path)]
    return sorted(images, key=lambda p: p.as_posix().lower())


def has_images(finger_dir: Path) -> bool:
    """判断某个目录下是否存在支持的图像文件。"""
    return any(is_image_file(path) for path in finger_dir.rglob("*"))


def resolve_finger_dirs(data_root: Path) -> list[tuple[str, Path]]:
    """解析 finger_id 目录。

    支持两种常见结构：
    1. data_root/finger_id/*.bmp
    2. data_root/dataset_name/finger_id/**/**/*.bmp
    """
    finger_entries: list[tuple[str, Path]] = []
    top_dirs = [
        item
        for item in sorted(data_root.iterdir(), key=lambda p: p.name.lower())
        if item.is_dir() and not is_ignored_path(item)
    ]

    if not top_dirs:
        print(f"Warning: no folders found under {data_root}", file=sys.stderr)

    for top_dir in top_dirs:
        if not has_images(top_dir):
            print(
                f"Warning: folder '{top_dir.name}' has no supported images and will be skipped.",
                file=sys.stderr,
            )
            continue

        child_dirs = [
            child
            for child in sorted(top_dir.iterdir(), key=lambda p: p.name.lower())
            if child.is_dir() and not is_ignored_path(child)
        ]
        child_dirs_with_images = [child for child in child_dirs if has_images(child)]
        images_at_top_level = [path for path in top_dir.iterdir() if is_image_file(path)]

        # 若一级目录本身没有图像，但子目录里有图像，则把子目录当作 finger_id。
        if child_dirs_with_images and not images_at_top_level:
            for child_dir in child_dirs_with_images:
                finger_entries.append((child_dir.name, child_dir))
            continue

        finger_entries.append((top_dir.name, top_dir))

    return finger_entries


def collect_labels(data_root: Path, relative_to: Path) -> list[dict[str, str]]:
    """从“一个文件夹一个手指身份”的目录结构中收集标签行。"""
    if not data_root.exists():
        raise FileNotFoundError(f"Data root does not exist: {data_root}")
    if not data_root.is_dir():
        raise NotADirectoryError(f"Data root is not a directory: {data_root}")

    rows: list[dict[str, str]] = []
    finger_entries = resolve_finger_dirs(data_root)

    if not finger_entries:
        print(f"Warning: no finger_id folders with images found under {data_root}", file=sys.stderr)

    for finger_id, finger_dir in finger_entries:
        images = iter_images(finger_dir)
        if not images:
            print(
                f"Warning: finger_id '{finger_id}' has no supported images.",
                file=sys.stderr,
            )
            continue

        for image_path in images:
            rows.append(
                {
                    "image_path": to_posix_relative(image_path, relative_to),
                    "finger_id": finger_id,
                }
            )

    return rows


def write_labels(rows: list[dict[str, str]], output_csv: Path) -> None:
    """将标签行写入 CSV 文件。"""
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=["image_path", "finger_id"])
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="Generate labels.csv from folder names for fingerprint data."
    )
    parser.add_argument("--data_root", type=Path, required=True, help="Dataset root directory.")
    parser.add_argument("--output_csv", type=Path, required=True, help="Output labels CSV path.")
    parser.add_argument(
        "--relative_to",
        type=Path,
        default=Path("."),
        help="Base directory used to store relative image paths. Default: project root.",
    )
    parser.add_argument(
        "--print_summary",
        type=str_to_bool,
        default=True,
        help="Whether to print per-finger image counts. Default: true.",
    )
    return parser.parse_args()


def main() -> None:
    """脚本入口：收集标签、写入 CSV，并输出统计信息。"""
    args = parse_args()
    rows = collect_labels(args.data_root, args.relative_to)
    if not rows:
        raise RuntimeError("No supported images found. Please check --data_root.")

    write_labels(rows, args.output_csv)

    print(f"Saved labels to {args.output_csv}")
    print(f"Total images: {len(rows)}")
    if args.print_summary:
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["finger_id"]] = counts.get(row["finger_id"], 0) + 1
        print("finger_id,image_count")
        for finger_id in sorted(counts):
            print(f"{finger_id},{counts[finger_id]}")


if __name__ == "__main__":
    main()
