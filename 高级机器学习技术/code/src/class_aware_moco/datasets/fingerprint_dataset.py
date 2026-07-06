"""Class-aware MoCo 训练用单图像数据集。

脚本作用：
1. 读取 `labels_train.csv`；
2. 将字符串 `finger_id` 映射为整数标签；
3. 为同一张指纹图像生成两个随机增强视图；
4. 返回 `view1`、`view2` 和整数标签，供 MoCo 对比学习训练使用。
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


LABEL_FIELDS = ["image_path", "finger_id"]
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def read_label_rows(label_csv: Path) -> list[dict[str, str]]:
    """读取标签 CSV，并校验 `image_path,finger_id` 字段。"""
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


def build_label_map(rows: list[dict[str, str]]) -> dict[str, int]:
    """构建稳定的 finger_id 到整数标签映射。"""
    finger_ids = sorted({row["finger_id"] for row in rows})
    return {finger_id: index for index, finger_id in enumerate(finger_ids)}


def save_label_map(label_map: dict[str, int], output_json: Path) -> None:
    """将标签映射保存为 JSON，供训练、测试和报告复用。"""
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open("w", encoding="utf-8") as file:
        json.dump(label_map, file, ensure_ascii=False, indent=2)


def load_label_map(label_map_json: Path) -> dict[str, int]:
    """从 JSON 读取标签映射。"""
    if not label_map_json.exists():
        raise FileNotFoundError(f"Label map does not exist: {label_map_json}")
    with label_map_json.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid label map format: {label_map_json}")
    return {str(key): int(value) for key, value in data.items()}


class MoCoFingerprintDataset(Dataset):
    """加载单张指纹图像，并为 MoCo 训练生成两个增强视图。"""

    def __init__(
        self,
        label_csv: Path,
        image_root: Path,
        label_map: dict[str, int],
        height: int = 100,
        width: int = 110,
        random_horizontal_flip: bool = False,
        blur_prob: float = 0.2,
    ) -> None:
        self.label_csv = Path(label_csv)
        self.image_root = Path(image_root)
        self.label_map = label_map
        self.height = height
        self.width = width
        self.rows = read_label_rows(self.label_csv)
        self.transform = self._build_train_transform(random_horizontal_flip, blur_prob)

        missing_labels = sorted({row["finger_id"] for row in self.rows if row["finger_id"] not in label_map})
        if missing_labels:
            raise ValueError(f"finger_id values missing from label_map: {missing_labels}")

    def __len__(self) -> int:
        """返回训练图像数量。"""
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, object]:
        """返回同一图像的两个增强视图和对应整数标签。"""
        row = self.rows[index]
        image_path = self._resolve_path(row["image_path"])
        image = self._load_gray_image(image_path)
        label = self.label_map[row["finger_id"]]

        return {
            "view1": self.transform(image),
            "view2": self.transform(image),
            "label": torch.tensor(label, dtype=torch.long),
            "image_path": row["image_path"],
            "finger_id": row["finger_id"],
        }

    @staticmethod
    def _build_train_transform(random_horizontal_flip: bool, blur_prob: float) -> transforms.Compose:
        """构建轻量训练增强流程。"""
        # 小面积指纹纹线结构敏感，只使用小角度旋转、轻微平移和低概率模糊。
        steps: list[object] = [
            transforms.RandomRotation(degrees=8),
            transforms.RandomAffine(degrees=0, translate=(0.03, 0.03)),
        ]
        if blur_prob > 0:
            steps.append(
                transforms.RandomApply(
                    [transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 0.8))],
                    p=blur_prob,
                )
            )
        if random_horizontal_flip:
            steps.append(transforms.RandomHorizontalFlip(p=0.5))

        steps.extend(
            [
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5], std=[0.5]),
            ]
        )
        return transforms.Compose(steps)

    def _resolve_path(self, image_path: str) -> Path:
        """将 CSV 中的相对路径解析到 image_root 下。"""
        path = Path(image_path)
        if path.is_absolute():
            return path
        return self.image_root / path

    def _load_gray_image(self, image_path: Path) -> Image.Image:
        """读取灰度图，并统一到指定输入尺寸。"""
        if not image_path.exists():
            raise FileNotFoundError(f"Image does not exist: {image_path}")
        if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            raise ValueError(f"Unsupported image extension: {image_path}")

        try:
            image = Image.open(image_path).convert("L")
        except Exception as exc:
            raise ValueError(f"Failed to read image: {image_path}") from exc

        expected_size = (self.width, self.height)
        if image.size != expected_size:
            image = image.resize(expected_size, Image.Resampling.BILINEAR)
        return image
