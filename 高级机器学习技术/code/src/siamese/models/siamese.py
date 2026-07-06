"""轻量级孪生网络模型。

脚本作用：
1. 定义适合 100x110 小面积指纹图像的 CNN 编码器；
2. 输出 128 维 L2 归一化 embedding；
3. 定义共享编码器的孪生网络；
4. 返回两张图像的 embedding 和欧氏距离。
"""

from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F


class FingerprintEncoder(nn.Module):
    """将单通道指纹图像编码为 embedding 的轻量 CNN。"""

    def __init__(self, embedding_dim: int = 128) -> None:
        super().__init__()
        # 卷积部分逐步提取局部纹线特征，并通过池化降低空间分辨率。
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        # 投影头将 256 维全局特征映射到最终 embedding 维度。
        self.projection = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2),
            nn.Linear(128, embedding_dim),
        )

    def forward(self, image: torch.Tensor) -> torch.Tensor:
        """编码图像批次，并对 embedding 做 L2 归一化。"""
        features = self.features(image)
        embedding = self.projection(features)
        return F.normalize(embedding, p=2, dim=1)


class SiameseNetwork(nn.Module):
    """两个分支共享同一个编码器的孪生网络。"""

    def __init__(self, embedding_dim: int = 128, eps: float = 1e-8) -> None:
        super().__init__()
        self.encoder = FingerprintEncoder(embedding_dim=embedding_dim)
        self.eps = eps

    def forward(self, img1: torch.Tensor, img2: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """返回两张图的 embedding 以及二者的欧氏距离。"""
        emb1 = self.encoder(img1)
        emb2 = self.encoder(img2)
        distance = torch.sqrt(torch.sum((emb1 - emb2) ** 2, dim=1) + self.eps)
        return emb1, emb2, distance
