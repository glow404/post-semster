# Proposed Method: Class-aware MoCo

本目录实现提出方法：Class-aware MoCo（类别感知动量对比学习），用于小面积指纹验证。

## 方法说明

原始 MoCo 通常只把同一图像的两个增强视图作为正样本，把队列中的其他样本作为负样本。小面积指纹数据中，同一个 `finger_id` 下的多张图像来自同一根手指，因此本方法把 `finger_id` 信息加入 MoCo 队列。

核心改进：

1. `queue` 保存历史 key embedding。
2. `queue_labels` 保存每个 key 对应的 `finger_id` 整数标签。
3. 当前 query 与相同 `finger_id` 的队列样本构成额外正样本。
4. 当前 query 与不同 `finger_id` 的队列样本构成负样本。
5. 使用多正样本对比损失拉近同类特征，推远异类特征。

## 训练流程

训练使用单图像标签：

```text
data/labels_train.csv
```

每张图像生成两个增强视图：

- `view1` 输入 `encoder_q`
- `view2` 输入 `encoder_k`

`encoder_q` 正常反向传播更新，`encoder_k` 通过动量更新。

## 配置文件

默认参数写在：

```text
src/class_aware_moco/config.yaml
```

当前脚本仍使用命令行参数运行，`config.yaml` 用于记录和复现实验配置。

## 训练命令

```bash
python src/class_aware_moco/train_class_aware_moco.py --train_labels data/labels_train.csv --val_pairs data/pairs_val.csv --image_root . --output_dir results/class_aware_moco --height 100 --width 110 --embedding_dim 128 --queue_size 4096 --momentum 0.999 --temperature 0.07 --batch_size 64 --epochs 100 --lr 0.001 --weight_decay 0.0001 --num_workers 4 --seed 42 --device cuda
```

小数据或 CPU 环境可使用较小队列：

```bash
python src/class_aware_moco/train_class_aware_moco.py --train_labels data/labels_train.csv --val_pairs data/pairs_val.csv --image_root . --output_dir results/class_aware_moco --queue_size 1024 --epochs 100 --num_workers 0 --device cpu
```

## 测试命令

```bash
python src/class_aware_moco/eval_class_aware_moco.py --test_pairs data/pairs_test.csv --image_root . --checkpoint results/class_aware_moco/best_class_aware_moco.pth --output_dir results/class_aware_moco --height 100 --width 110 --batch_size 64 --num_workers 4 --device cuda
```

## 输出结果

```text
results/class_aware_moco/
├── best_class_aware_moco.pth
├── train_log.csv
├── test_scores.csv
├── metrics.json
├── roc_curve.png
├── config.json
└── label_map.json
```

`test_scores.csv` 字段：

```text
img1,img2,label,distance,pred,finger_id1,finger_id2
```

## 指标

训练后的 `encoder_q` 用于提取图像 embedding。验证和测试时计算两张图像 embedding 的欧氏距离，距离越小越像同一根手指。计算 ROC-AUC 和 EER 时使用 `-distance` 作为连续分数。

## 对比方式

为保证和 SIFT、Siamese Network 公平对比，本方法使用相同的 `pairs_test.csv`，并报告相同指标：Accuracy、Precision、Recall、F1-score、ROC-AUC、EER 和 Confusion Matrix。
