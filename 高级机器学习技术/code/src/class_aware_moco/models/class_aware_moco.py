"""Class-aware MoCo 模型定义。

脚本作用：
1. 定义与 Siamese 公平对比的轻量 CNN 编码器；
2. 构建 query encoder 和 momentum key encoder；
3. 维护同时保存 embedding 和 finger_id 标签的队列；
4. 实现类别感知多正样本对比损失；
5. 提供训练和指纹验证用的 embedding 提取接口。
"""

from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F


class FingerprintEncoder(nn.Module):
    """输出 L2 归一化 embedding 的轻量 CNN 编码器。"""

    def __init__(self, embedding_dim: int = 128) -> None:
        super().__init__()
        # 卷积主干提取小面积指纹的局部纹线特征。
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
        # 投影头将卷积特征映射到对比学习使用的 embedding 空间。
        self.projection = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2),
            nn.Linear(128, embedding_dim),
        )

    def forward(self, image: torch.Tensor) -> torch.Tensor:
        """编码灰度指纹图像，并输出单位长度 embedding。"""
        embedding = self.projection(self.features(image))
        return F.normalize(embedding, p=2, dim=1)


class ClassAwareMoCo(nn.Module):
    """带标签感知队列的动量对比学习模型。"""

    def __init__(
        self,
        embedding_dim: int = 128,
        queue_size: int = 4096,
        momentum: float = 0.999,
        temperature: float = 0.07,
    ) -> None:
        super().__init__()
        if queue_size <= 0:
            raise ValueError("queue_size must be positive.")
        if temperature <= 0:
            raise ValueError("temperature must be positive.")

        self.embedding_dim = embedding_dim
        self.queue_size = queue_size
        self.momentum = momentum
        self.temperature = temperature

        # encoder_q 参与反向传播；encoder_k 只通过动量更新。
        self.encoder_q = FingerprintEncoder(embedding_dim=embedding_dim)
        self.encoder_k = FingerprintEncoder(embedding_dim=embedding_dim)
        self._initialize_key_encoder()

        # queue 保存历史 key embedding；queue_labels 保存对应 finger_id 整数标签。
        queue = torch.randn(embedding_dim, queue_size)
        queue = F.normalize(queue, p=2, dim=0)
        self.register_buffer("queue", queue)
        self.register_buffer("queue_labels", torch.full((queue_size,), -1, dtype=torch.long))
        self.register_buffer("queue_ptr", torch.zeros(1, dtype=torch.long))

    @torch.no_grad()
    def _initialize_key_encoder(self) -> None:
        """用 query encoder 初始化 key encoder，并冻结 key encoder 梯度。"""
        for param_q, param_k in zip(self.encoder_q.parameters(), self.encoder_k.parameters()):
            param_k.data.copy_(param_q.data)
            param_k.requires_grad = False

    @torch.no_grad()
    def momentum_update_key_encoder(self) -> None:
        """用动量方式更新 key encoder。"""
        for param_q, param_k in zip(self.encoder_q.parameters(), self.encoder_k.parameters()):
            param_k.data.mul_(self.momentum).add_(param_q.data, alpha=1.0 - self.momentum)

    @torch.no_grad()
    def dequeue_and_enqueue(self, keys: torch.Tensor, labels: torch.Tensor) -> None:
        """将当前 batch 的 key embedding 和标签写入循环队列。"""
        keys = keys.detach()
        labels = labels.detach().long()
        if keys.size(0) > self.queue_size:
            keys = keys[-self.queue_size :]
            labels = labels[-self.queue_size :]

        batch_size = keys.size(0)
        ptr = int(self.queue_ptr.item())
        end = ptr + batch_size

        # 队列是环形缓冲区；写到末尾后从开头继续覆盖旧样本。
        if end <= self.queue_size:
            self.queue[:, ptr:end] = keys.T
            self.queue_labels[ptr:end] = labels
        else:
            first = self.queue_size - ptr
            self.queue[:, ptr:] = keys[:first].T
            self.queue_labels[ptr:] = labels[:first]
            remain = batch_size - first
            self.queue[:, :remain] = keys[first:].T
            self.queue_labels[:remain] = labels[first:]

        self.queue_ptr[0] = end % self.queue_size

    def class_aware_contrastive_loss(
        self,
        queries: torch.Tensor,
        keys: torch.Tensor,
        labels: torch.Tensor,
    ) -> torch.Tensor:
        """计算类别感知多正样本对比损失。"""
        labels = labels.long()
        batch_size = queries.size(0)
        valid_queue_mask = self.queue_labels >= 0
        queue_keys = self.queue[:, valid_queue_mask].T
        queue_labels = self.queue_labels[valid_queue_mask]

        # 分母包含当前 batch 的 key 和队列中的所有有效 key。
        all_keys = torch.cat([keys, queue_keys], dim=0)
        logits = torch.matmul(queries, all_keys.T) / self.temperature

        # 当前图像的增强视图 k_i 永远是正样本；队列中同类 key 是额外正样本。
        positive_mask = torch.zeros_like(logits, dtype=torch.bool)
        positive_mask[:, :batch_size] = torch.eye(batch_size, dtype=torch.bool, device=logits.device)
        if queue_keys.numel() > 0:
            positive_mask[:, batch_size:] = labels[:, None].eq(queue_labels[None, :])

        # 使用 logsumexp 计算 log(分子/分母)，避免 exp 后数值溢出。
        log_denominator = torch.logsumexp(logits, dim=1)
        masked_logits = logits.masked_fill(~positive_mask, float("-inf"))
        log_numerator = torch.logsumexp(masked_logits, dim=1)
        return -(log_numerator - log_denominator).mean()

    def forward(self, im_q: torch.Tensor, im_k: torch.Tensor, labels: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """前向训练：计算损失，并把当前 key 写入标签感知队列。"""
        queries = self.encoder_q(im_q)
        with torch.no_grad():
            self.momentum_update_key_encoder()
            keys = self.encoder_k(im_k)

        loss = self.class_aware_contrastive_loss(queries, keys, labels)
        self.dequeue_and_enqueue(keys, labels)
        return loss, queries, keys

    @torch.no_grad()
    def encode(self, image: torch.Tensor) -> torch.Tensor:
        """使用 query encoder 提取验证/测试阶段的图像 embedding。"""
        self.encoder_q.eval()
        return self.encoder_q(image)
