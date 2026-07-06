"""指纹验证实验的公共评价指标工具。

脚本作用：
1. 将相似度分数或距离转换为二分类预测；
2. 在验证集上选择最佳阈值；
3. 计算 Accuracy、Precision、Recall、F1、ROC-AUC、EER 和混淆矩阵；
4. 保存 ROC 曲线图。

说明：SIFT 使用“分数越大越相似”，Siamese 和 Class-aware MoCo 使用“距离越小越相似”。
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def predictions_from_scores(scores: list[float] | np.ndarray, threshold: float) -> np.ndarray:
    """将相似度分数转换为预测标签；分数大于等于阈值时预测为正样本。"""
    score_array = np.asarray(scores, dtype=float)
    return (score_array >= threshold).astype(int)


def predictions_from_distances(distances: list[float] | np.ndarray, threshold: float) -> np.ndarray:
    """将距离转换为预测标签；距离小于等于阈值时预测为正样本。"""
    distance_array = np.asarray(distances, dtype=float)
    return (distance_array <= threshold).astype(int)


def choose_best_threshold(
    labels: list[int] | np.ndarray,
    scores: list[float] | np.ndarray,
    num_grid: int = 101,
) -> tuple[float, float]:
    """为“分数越大越相似”的方法选择验证集 F1 最高的阈值。"""
    label_array = np.asarray(labels, dtype=int)
    score_array = np.asarray(scores, dtype=float)
    if label_array.size == 0:
        raise ValueError("Cannot select a threshold from empty labels.")

    # 同时使用均匀网格和真实分数值，避免最佳阈值落在网格之外。
    candidate_thresholds = set(np.linspace(0.0, 1.0, num_grid).tolist())
    candidate_thresholds.update(score_array.tolist())
    candidate_thresholds.add(float(score_array.max()) + 1e-12)

    best_threshold = 0.0
    best_f1 = -1.0
    best_accuracy = -1.0
    for threshold in sorted(candidate_thresholds):
        preds = predictions_from_scores(score_array, threshold)
        current_f1 = f1_score(label_array, preds, zero_division=0)
        current_accuracy = accuracy_score(label_array, preds)
        if (current_f1, current_accuracy) > (best_f1, best_accuracy):
            best_f1 = float(current_f1)
            best_accuracy = float(current_accuracy)
            best_threshold = float(threshold)

    return best_threshold, best_f1


def choose_best_distance_threshold(
    labels: list[int] | np.ndarray,
    distances: list[float] | np.ndarray,
    num_grid: int = 101,
) -> tuple[float, float]:
    """为“距离越小越相似”的方法选择验证集 F1 最高的阈值。"""
    label_array = np.asarray(labels, dtype=int)
    distance_array = np.asarray(distances, dtype=float)
    if label_array.size == 0:
        raise ValueError("Cannot select a threshold from empty labels.")

    min_distance = float(distance_array.min())
    max_distance = float(distance_array.max())
    # 距离的范围由模型输出决定，因此网格根据验证集最小/最大距离自适应生成。
    candidate_thresholds = set(np.linspace(min_distance, max_distance, num_grid).tolist())
    candidate_thresholds.update(distance_array.tolist())
    candidate_thresholds.add(min_distance - 1e-12)
    candidate_thresholds.add(max_distance + 1e-12)

    best_threshold = 0.0
    best_f1 = -1.0
    best_accuracy = -1.0
    for threshold in sorted(candidate_thresholds):
        preds = predictions_from_distances(distance_array, threshold)
        current_f1 = f1_score(label_array, preds, zero_division=0)
        current_accuracy = accuracy_score(label_array, preds)
        if (current_f1, current_accuracy) > (best_f1, best_accuracy):
            best_f1 = float(current_f1)
            best_accuracy = float(current_accuracy)
            best_threshold = float(threshold)

    return best_threshold, best_f1


def compute_metrics(
    labels: list[int] | np.ndarray,
    scores: list[float] | np.ndarray,
    threshold: float,
) -> dict[str, object]:
    """计算相似度分数模式下的二分类验证指标。"""
    label_array = np.asarray(labels, dtype=int)
    score_array = np.asarray(scores, dtype=float)
    preds = predictions_from_scores(score_array, threshold)

    metrics: dict[str, object] = {
        "accuracy": float(accuracy_score(label_array, preds)),
        "precision": float(precision_score(label_array, preds, zero_division=0)),
        "recall": float(recall_score(label_array, preds, zero_division=0)),
        "f1": float(f1_score(label_array, preds, zero_division=0)),
        "confusion_matrix": confusion_matrix(label_array, preds, labels=[0, 1]).astype(int).tolist(),
    }

    if len(np.unique(label_array)) < 2:
        metrics["roc_auc"] = 0.0
        metrics["eer"] = 0.0
    else:
        metrics["roc_auc"] = float(roc_auc_score(label_array, score_array))
        metrics["eer"] = float(compute_eer(label_array, score_array))

    return metrics


def compute_distance_metrics(
    labels: list[int] | np.ndarray,
    distances: list[float] | np.ndarray,
    threshold: float,
) -> dict[str, object]:
    """计算距离模式下的二分类验证指标。"""
    label_array = np.asarray(labels, dtype=int)
    distance_array = np.asarray(distances, dtype=float)
    preds = predictions_from_distances(distance_array, threshold)
    # ROC-AUC 要求分数越大越偏向正样本，因此距离模式需要取负号。
    roc_scores = -distance_array

    metrics: dict[str, object] = {
        "accuracy": float(accuracy_score(label_array, preds)),
        "precision": float(precision_score(label_array, preds, zero_division=0)),
        "recall": float(recall_score(label_array, preds, zero_division=0)),
        "f1": float(f1_score(label_array, preds, zero_division=0)),
        "confusion_matrix": confusion_matrix(label_array, preds, labels=[0, 1]).astype(int).tolist(),
    }

    if len(np.unique(label_array)) < 2:
        metrics["roc_auc"] = 0.0
        metrics["eer"] = 0.0
    else:
        metrics["roc_auc"] = float(roc_auc_score(label_array, roc_scores))
        metrics["eer"] = float(compute_eer(label_array, roc_scores))

    return metrics


def compute_eer(labels: list[int] | np.ndarray, scores: list[float] | np.ndarray) -> float:
    """根据 ROC 曲线计算 EER（等错误率）。"""
    label_array = np.asarray(labels, dtype=int)
    score_array = np.asarray(scores, dtype=float)
    if len(np.unique(label_array)) < 2:
        return 0.0

    fpr, tpr, _ = roc_curve(label_array, score_array)
    fnr = 1.0 - tpr
    index = int(np.nanargmin(np.abs(fpr - fnr)))
    return float((fpr[index] + fnr[index]) / 2.0)


def save_roc_curve(
    labels: list[int] | np.ndarray,
    scores: list[float] | np.ndarray,
    output_png: Path,
    title: str = "SIFT Verification ROC Curve",
) -> None:
    """保存 ROC 曲线图，供课程报告直接引用。"""
    output_png.parent.mkdir(parents=True, exist_ok=True)
    label_array = np.asarray(labels, dtype=int)
    score_array = np.asarray(scores, dtype=float)

    plt.figure(figsize=(6, 5))
    if len(np.unique(label_array)) < 2:
        plt.plot([0, 1], [0, 1], linestyle="--", label="ROC unavailable")
    else:
        fpr, tpr, _ = roc_curve(label_array, score_array)
        auc_value = roc_auc_score(label_array, score_array)
        plt.plot(fpr, tpr, label=f"ROC-AUC = {auc_value:.4f}")
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Random")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(title)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(output_png, dpi=200)
    plt.close()
