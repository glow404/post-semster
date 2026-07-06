"""孪生网络使用的图像对数据集。

脚本作用：
1. 读取 `pairs_train/val/test.csv`；
2. 根据 CSV 中的相对路径加载两张灰度指纹图像；
3. 将图像统一为 `[1,100,110]` 张量；
4. 训练阶段可使用轻量几何增强，验证和测试阶段不使用随机增强。
"""

from __future__ import annotations

import csv
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


PAIR_FIELDS = ["img1", "img2", "label", "finger_id1", "finger_id2"]
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


class FingerprintPairDataset(Dataset):
    """从 CSV 文件加载指纹图像对。"""

    def __init__(
        self,
        pairs_csv: Path,
        image_root: Path,
        height: int = 100,
        width: int = 110,
        train: bool = False,
        random_horizontal_flip: bool = False,
    ) -> None:
        self.pairs_csv = Path(pairs_csv)
        self.image_root = Path(image_root)
        self.height = height
        self.width = width
        self.train = train
        self.rows = self._read_pairs(self.pairs_csv)
        self.transform = self._build_transform(train, random_horizontal_flip)

    def __len__(self) -> int:
        """返回图像对数量。"""
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, object]:
        """读取并返回一个图像对样本。"""
        row = self.rows[index]
        img1_path = self._resolve_path(row["img1"])
        img2_path = self._resolve_path(row["img2"])

        img1 = self._load_gray_image(img1_path)
        img2 = self._load_gray_image(img2_path)

        return {
            "img1": self.transform(img1),
            "img2": self.transform(img2),
            "label": torch.tensor(float(row["label"]), dtype=torch.float32),
            "img1_path": row["img1"],
            "img2_path": row["img2"],
            "finger_id1": row["finger_id1"],
            "finger_id2": row["finger_id2"],
        }

    @staticmethod
    def _read_pairs(pairs_csv: Path) -> list[dict[str, str]]:
        """读取并校验图像对 CSV。"""
        if not pairs_csv.exists():
            raise FileNotFoundError(f"Pair CSV does not exist: {pairs_csv}")

        with pairs_csv.open("r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                raise ValueError(f"Empty CSV: {pairs_csv}")
            missing = [field for field in PAIR_FIELDS if field not in reader.fieldnames]
            if missing:
                raise ValueError(f"Missing columns in {pairs_csv}: {missing}")

            rows = []
            for row in reader:
                if not all(row.get(field) for field in PAIR_FIELDS):
                    continue
                label = row["label"]
                if label not in {"0", "1"}:
                    raise ValueError(f"Invalid label '{label}' in {pairs_csv}; expected 0 or 1.")
                rows.append({field: row[field] for field in PAIR_FIELDS})

        if not rows:
            raise ValueError(f"No valid pair rows found in {pairs_csv}")
        return rows

    @staticmethod
    def _build_transform(train: bool, random_horizontal_flip: bool) -> transforms.Compose:
        """构建图像预处理和训练增强流程。"""
        steps: list[object] = []
        if train:
            # 只使用轻量几何增强，避免破坏小面积指纹纹线结构。
            steps.extend(
                [
                    transforms.RandomRotation(degrees=8),
                    transforms.RandomAffine(degrees=0, translate=(0.03, 0.03)),
                ]
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
        """读取灰度图，并统一到命令行指定尺寸。"""
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
            # 统一输入尺寸，避免通用图像管线意外改成 96x96 等非实验设定尺寸。
            image = image.resize(expected_size, Image.Resampling.BILINEAR)
        return image
