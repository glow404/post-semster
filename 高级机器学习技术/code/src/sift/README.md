# Baseline 1: SIFT + Matching

本目录实现传统特征方法：SIFT（尺度不变特征变换）+ Matching（特征匹配），用于小面积指纹验证。

## 方法说明

输入两张灰度指纹图像，分别提取 SIFT 关键点和描述子，然后使用特征匹配得到相似度分数。分数越大，越可能来自同一个 `finger_id`。

核心流程：

1. 读取灰度图。
2. 可选使用 CLAHE 增强。
3. 使用 SIFT 提取关键点和描述子。
4. 使用 BFMatcher 做描述子匹配。
5. 使用 Lowe 比率测试过滤弱匹配。
6. 可选使用 RANSAC 过滤几何不一致匹配。
7. 计算相似度分数。

相似度分数：

```text
score = good_matches / max(num_keypoints_img1, num_keypoints_img2, 1)
```

如果某张图没有检测到关键点，`score=0`。

## 配置文件

默认参数写在：

```text
src/sift/config.yaml
```

当前脚本仍使用命令行参数运行，`config.yaml` 用于记录和复现实验配置。

## 运行命令

```bash
python src/sift/eval_sift.py --val_pairs data/pairs_val.csv --test_pairs data/pairs_test.csv --image_root . --output_dir results/sift --use_clahe true --use_ransac true
```

## 输出结果

```text
results/sift/
├── val_scores.csv
├── test_scores.csv
├── metrics.json
├── roc_curve.png
└── config.json
```

`test_scores.csv` 字段：

```text
img1,img2,label,score,pred,finger_id1,finger_id2
```

## 指标

使用验证集选择最佳阈值，测试集计算 Accuracy、Precision、Recall、F1-score、ROC-AUC、EER 和 Confusion Matrix。
