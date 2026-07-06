"""孪生网络的对比损失。

脚本作用：
1. 实现标准 Contrastive Loss；
2. 对正样本拉近 embedding 距离；
3. 对负样本在 margin 内产生惩罚，推动不同手指远离。
"""

from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F


class ContrastiveLoss(nn.Module):
    """标准对比损失，约定 label=1 表示正样本对。"""

    def __init__(self, margin: float = 1.0) -> None:
        super().__init__()
        self.margin = margin

    def forward(self, distance: torch.Tensor, label: torch.Tensor) -> torch.Tensor:
        """根据距离和标签计算 batch 平均损失。"""
        label = label.float()
        # 正样本希望距离尽量小，因此直接惩罚 distance^2。
        positive_loss = label * distance.pow(2)
        # 负样本只有距离小于 margin 时才产生损失。
        negative_loss = (1.0 - label) * F.relu(self.margin - distance).pow(2)
        return torch.mean(positive_loss + negative_loss)
