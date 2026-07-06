# Baseline 2: Siamese Network + Contrastive Loss

本目录实现孪生网络（Siamese Network）+ 对比损失（Contrastive Loss），用于小面积指纹验证。

## 方法说明

模型输入两张小面积指纹图像，两个分支共享同一个 CNN 编码器，分别输出 128 维 embedding。训练时使用欧氏距离和对比损失，使同一 `finger_id` 的图像距离更小，不同 `finger_id` 的图像距离更大。

标签定义：

```text
label=1 表示同一 finger_id
label=0 表示不同 finger_id
```

对比损失：

```text
loss = label * distance^2 + (1 - label) * max(margin - distance, 0)^2
```

## 配置文件

默认参数写在：

```text
src/siamese/config.yaml
```

当前脚本仍使用命令行参数运行，`config.yaml` 用于记录和复现实验配置。

## 训练命令

```bash
python src/siamese/train_siamese.py --train_pairs data/pairs_train.csv --val_pairs data/pairs_val.csv --image_root . --output_dir results/siamese --height 100 --width 110 --embedding_dim 128 --batch_size 64 --epochs 100 --lr 0.001 --weight_decay 0.0001 --margin 1.0 --num_workers 4 --seed 42 --device cuda
```

如果 Windows 环境多进程读取数据报错，可以使用：

```bash
python src/siamese/train_siamese.py --train_pairs data/pairs_train.csv --val_pairs data/pairs_val.csv --image_root . --output_dir results/siamese --num_workers 0 --device cpu
```

## 测试命令

```bash
python src/siamese/eval_siamese.py --test_pairs data/pairs_test.csv --image_root . --checkpoint results/siamese/best_siamese.pth --output_dir results/siamese --height 100 --width 110 --batch_size 64 --num_workers 4 --device cuda
```

## 输出结果

```text
results/siamese/
├── best_siamese.pth
├── train_log.csv
├── test_scores.csv
├── metrics.json
├── roc_curve.png
└── config.json
```

`test_scores.csv` 字段：

```text
img1,img2,label,distance,pred,finger_id1,finger_id2
```

## 指标

孪生网络输出距离，距离越小越像同一根手指。验证集选择最佳阈值，测试集计算 Accuracy、Precision、Recall、F1-score、ROC-AUC、EER 和 Confusion Matrix。计算 ROC-AUC 和 EER 时使用 `-distance` 作为连续分数。
