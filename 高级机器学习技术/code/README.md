# 小面积指纹识别实验

本项目主题为：基于类别感知对比学习的小面积指纹识别方法研究。

当前已实现 Baseline 1：SIFT（尺度不变特征变换）+ Matching（特征匹配）。该方法用于指纹验证任务：输入两张小面积指纹图像，判断它们是否来自同一个手指身份。

## 数据目录结构

当前数据实际位于：

```text
ysjz_denoised/
└── ysjz_denoised/
    ├── dy_L0/
    ├── dy_L1/
    ├── dy_L2/
    ├── dy_R0/
    ├── dy_R1/
    ├── dy_R2/
    ├── lwh_R0/
    ├── lwh_R1/
    ├── lwh_R2/
    ├── SSH_L0/
    ├── SSH_L1/
    ├── SSH_L2/
    ├── yjx_R0/
    ├── yjx_R1/
    ├── yjx_R2/
    ├── zyh_L0/
    ├── zyh_L1/
    ├── zyh_L2/
    ├── zyh_R0/
    ├── zyh_R1/
    └── zyh_R2/
```

每个子文件夹名就是 `finger_id`。例如，`SSH_L0`、`SSH_L1` 和 `dy_R0` 分别表示不同手指身份。

图像原始尺度为 `100×110`，SIFT 实验中不会强制缩放图像。脚本会忽略 `__MACOSX`、`.DS_Store`、隐藏文件夹、隐藏文件和非图像文件。

支持图像格式：`.png`、`.jpg`、`.jpeg`、`.bmp`、`.tif`、`.tiff`。

## 代码目录约定

不同方法的代码分开放置，后续新增方法也按独立目录组织：

```text
src/
├── build_labels_from_folders.py
├── make_pairs.py
├── make_pairs/
│   ├── README.md
│   └── config.yaml
├── utils_metrics.py
├── sift/
│   ├── eval_sift.py
│   └── sift_match.py
├── siamese/
    ├── train_siamese.py
    ├── eval_siamese.py
    ├── datasets/
    ├── models/
    └── losses/
└── class_aware_moco/
    ├── train_class_aware_moco.py
    ├── eval_class_aware_moco.py
    ├── datasets/
    └── models/
```

其中，标签生成、样本对构造和指标计算是公共工具；SIFT、孪生网络和 Class-aware MoCo 各自放在自己的目录下。

## 环境依赖

建议安装：

```bash
pip install -r requirements.txt
```

如果运行 SIFT 时报错提示 SIFT 不可用，可额外安装 `opencv-contrib-python`。

## 生成 labels.csv

从文件夹名自动生成标签：

```bash
python src/build_labels_from_folders.py --data_root ysjz_denoised/ysjz_denoised --output_csv data/labels.csv
```

输出文件：

```text
data/labels.csv
```

字段：

```text
image_path,finger_id
```

其中 `image_path` 是相对路径，`finger_id` 是父文件夹名。

## 生成训练集、验证集、测试集和图像对

按 `finger_id` 划分数据，避免同一个手指身份同时出现在不同集合中。

默认参数说明见 `src/make_pairs/config.yaml`，详细说明见 `src/make_pairs/README.md`。

```bash
python src/make_pairs.py --label_csv data/labels.csv --output_dir data --train_ratio 0.7 --val_ratio 0.15 --test_ratio 0.15 --pos_neg_ratio 1.0 --seed 42
```

输出文件：

```text
data/labels_train.csv
data/labels_val.csv
data/labels_test.csv
data/pairs_train.csv
data/pairs_val.csv
data/pairs_test.csv
```

图像对字段：

```text
img1,img2,label,finger_id1,finger_id2
```

正样本对来自同一个 `finger_id`，`label=1`；负样本对来自不同 `finger_id`，`label=0`。默认每个 `finger_id` 最多采样 200 个正样本对，并采样接近相同数量的负样本对。

## 运行 SIFT 实验

在验证集上选择最佳阈值，在测试集上评价：

```bash
python src/sift/eval_sift.py --val_pairs data/pairs_val.csv --test_pairs data/pairs_test.csv --image_root . --output_dir results/sift --use_clahe true --use_ransac true
```

SIFT 匹配流程：

1. 读取灰度图。
2. 可选使用 CLAHE 增强局部对比度。
3. 使用 SIFT 提取关键点和描述子。
4. 使用 BFMatcher 进行描述子匹配。
5. 使用 Lowe 比率测试过滤弱匹配。
6. 可选使用 RANSAC 过滤几何不一致匹配。
7. 计算相似度分数。

相似度分数为：

```text
score = good_matches / max(num_keypoints_img1, num_keypoints_img2, 1)
```

如果某张图没有检测到关键点或描述子，`score=0`。

## 输出结果

结果保存在：

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

`metrics.json` 包含：

```json
{
  "method": "SIFT + Matching",
  "best_threshold": 0.0,
  "accuracy": 0.0,
  "precision": 0.0,
  "recall": 0.0,
  "f1": 0.0,
  "roc_auc": 0.0,
  "eer": 0.0,
  "confusion_matrix": [[0, 0], [0, 0]]
}
```

## 训练 Siamese Network

Baseline 2 使用 Siamese Network（孪生网络）+ Contrastive Loss（对比损失）。模型输入两张小面积指纹图像，两个分支共享同一个卷积编码器，输出两张图的嵌入向量和欧氏距离。

图像预处理：

- 读取灰度图。
- 保持原始尺度 `100×110`，输入张量为 `[1,100,110]`。
- 脚本会按 `--height` 和 `--width` 统一输出固定张量尺寸，默认是 `100×110`。
- 像素先归一化到 `[0,1]`，再使用 `mean=0.5`、`std=0.5` 标准化。
- 训练阶段默认使用轻量几何增强：小角度随机旋转和轻微平移。
- 验证集和测试集不使用随机增强。

模型输出距离，距离越小表示越像同一根手指。训练命令：

```bash
python src/siamese/train_siamese.py --train_pairs data/pairs_train.csv --val_pairs data/pairs_val.csv --image_root . --output_dir results/siamese --height 100 --width 110 --embedding_dim 128 --batch_size 64 --epochs 50 --lr 0.001 --weight_decay 0.0001 --margin 1.0 --num_workers 4 --seed 42 --device cuda
```

如果没有可用显卡，脚本会自动退回 CPU。Windows 环境中如果多进程读取数据报错，可改用：

```bash
python src/siamese/train_siamese.py --train_pairs data/pairs_train.csv --val_pairs data/pairs_val.csv --image_root . --output_dir results/siamese --num_workers 0 --device cpu
```

训练输出：

```text
results/siamese/
├── best_siamese.pth
├── train_log.csv
└── config.json
```

`train_log.csv` 每轮记录：

```text
epoch,train_loss,val_loss,val_accuracy,val_precision,val_recall,val_f1,val_auc,val_eer,val_threshold,lr
```

验证集阈值选择方式：

```text
distance <= threshold 预测为同一 finger_id
distance > threshold 预测为不同 finger_id
```

脚本遍历多个阈值，以验证集 F1 分数最高的阈值作为 `best_threshold`，并保存到 `results/siamese/config.json`。

## 测试 Siamese Network

测试命令：

```bash
python src/siamese/eval_siamese.py --test_pairs data/pairs_test.csv --image_root . --checkpoint results/siamese/best_siamese.pth --output_dir results/siamese --height 100 --width 110 --batch_size 64 --num_workers 4 --device cuda
```

测试输出：

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

`metrics.json` 格式：

```json
{
  "method": "Siamese Network + Contrastive Loss",
  "best_threshold": 0.0,
  "accuracy": 0.0,
  "precision": 0.0,
  "recall": 0.0,
  "f1": 0.0,
  "roc_auc": 0.0,
  "eer": 0.0,
  "confusion_matrix": [[0, 0], [0, 0]]
}
```

注意：Siamese Network 输出的是距离，距离越小越像正样本。因此计算 ROC-AUC 和 EER 时使用 `-distance` 作为连续分数。

## 训练 Class-aware MoCo

Proposed Method 使用 Class-aware MoCo（类别感知动量对比学习）。相比原始 MoCo 只把同一图像的两个增强视图作为正样本，本方法在队列中额外保存 `finger_id` 标签，并把队列中相同 `finger_id` 的样本作为多正样本。

核心思想：

- `encoder_q` 是查询编码器，正常反向传播更新。
- `encoder_k` 是键编码器，通过动量更新。
- `queue` 保存历史 key embedding。
- `queue_labels` 保存每个 key 对应的 `finger_id` 整数标签。
- 当前 query 的正样本包括当前图像的增强视图 key，以及队列中同 `finger_id` 的 key。
- 队列中不同 `finger_id` 的 key 作为负样本。

训练使用单图像标签文件：

```text
data/labels_train.csv
```

验证和测试仍使用图像对：

```text
data/pairs_val.csv
data/pairs_test.csv
```

训练命令：

```bash
python src/class_aware_moco/train_class_aware_moco.py --train_labels data/labels_train.csv --val_pairs data/pairs_val.csv --image_root . --output_dir results/class_aware_moco --height 100 --width 110 --embedding_dim 128 --queue_size 4096 --momentum 0.999 --temperature 0.07 --batch_size 64 --epochs 100 --lr 0.001 --weight_decay 0.0001 --num_workers 4 --seed 42 --device cuda
```

小数据或 CPU 环境可使用较小队列：

```bash
python src/class_aware_moco/train_class_aware_moco.py --train_labels data/labels_train.csv --val_pairs data/pairs_val.csv --image_root . --output_dir results/class_aware_moco --queue_size 1024 --epochs 100 --num_workers 0 --device cpu
```

训练输出：

```text
results/class_aware_moco/
├── best_class_aware_moco.pth
├── train_log.csv
├── config.json
└── label_map.json
```

`label_map.json` 保存字符串 `finger_id` 到整数标签的映射，训练、验证和测试共用同一份映射。

## 测试 Class-aware MoCo

训练完成后，使用 `encoder_q` 提取两张图像的 embedding，并计算欧氏距离。距离越小，越像同一根手指。

测试命令：

```bash
python src/class_aware_moco/eval_class_aware_moco.py --test_pairs data/pairs_test.csv --image_root . --checkpoint results/class_aware_moco/best_class_aware_moco.pth --output_dir results/class_aware_moco --height 100 --width 110 --batch_size 64 --num_workers 4 --device cuda
```

测试输出：

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

`metrics.json` 格式：

```json
{
  "method": "Class-aware MoCo",
  "best_threshold": 0.0,
  "accuracy": 0.0,
  "precision": 0.0,
  "recall": 0.0,
  "f1": 0.0,
  "roc_auc": 0.0,
  "eer": 0.0,
  "confusion_matrix": [[0, 0], [0, 0]]
}
```

注意：Class-aware MoCo 输出的是距离，距离越小越像正样本。因此计算 ROC-AUC 和 EER 时使用 `-distance` 作为连续分数。

## 指标说明

- Accuracy：准确率，所有样本对中预测正确的比例。
- Precision：精确率，预测为同一手指的样本对中，真实同一手指的比例。
- Recall：召回率，真实同一手指的样本对中，被正确识别出的比例。
- F1-score：精确率和召回率的综合指标。
- ROC-AUC：使用连续相似度分数计算，数值越高表示整体区分能力越强。
- EER：等错误率，错误接受率和错误拒绝率接近相等时的错误率，数值越低越好。
- Confusion Matrix：混淆矩阵，保存格式为 `[[TN, FP], [FN, TP]]`。

## 方法对比说明

本项目最终包含三类方法：

- Baseline 1：SIFT + Matching，属于传统手工特征方法，不需要训练，输出相似度分数。
- Baseline 2：Siamese Network + Contrastive Loss，属于有监督深度学习方法，需要用正负样本对训练，输出距离。
- Proposed Method：Class-aware MoCo，属于类别感知动量对比学习方法，训练时使用单图像和 `finger_id`，验证和测试时输出距离。

为了公平对比，建议三种方法都使用相同的 `pairs_test.csv`，并统一报告 Accuracy、Precision、Recall、F1-score、ROC-AUC、EER 和 Confusion Matrix。

## 注意事项

- 测试集只用于最终评价，不能参与阈值选择。
- 当前数据共有 21 个 `finger_id`，按身份划分后验证集类别数较少，阈值可能有一定波动。
- 小面积指纹图像可能出现 SIFT 关键点较少的情况，这是传统特征方法在小区域图像上的常见限制。
- Siamese Network 在当前数据规模下可能过拟合，报告中建议同时展示训练日志和验证集最佳阈值。
- Class-aware MoCo 队列初期可能缺少同类正样本，代码会始终把当前图像的增强视图作为正样本，并逐步引入队列中的同类样本。
