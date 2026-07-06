# 数据准备子任务

本目录负责**指纹验证实验的数据准备**，包含两个脚本，按顺序完成从原始图像到训练/验证/测试 CSV 的全流程。

```text
src/make_pairs/
├── build_labels_from_folders.py   # 步骤 1：扫描原始图像目录，生成 labels.csv
├── make_pairs.py                  # 步骤 2：划分 train/val/test，构造正负图像对
├── config.yaml                    # 默认参数配置
└── README.md
```

## 数据流说明

```text
原始指纹图像（你自备，不在 data/ 里）
    │
    │  build_labels_from_folders.py
    ▼
data/labels.csv
    │
    │  make_pairs.py
    ▼
data/labels_train.csv / labels_val.csv / labels_test.csv
data/pairs_train.csv  / pairs_val.csv  / pairs_test.csv
    │
    ▼
SIFT / Siamese / Class-aware MoCo
```

**重要区分：**

| 位置 | 内容 |
|------|------|
| `rawdata/data/` | 原始 `.bmp/.png` 指纹图像，按 `finger_id` 分文件夹存放 |
| `data/` | 脚本生成的 CSV 标签和图像对，**不含原始图像** |

---

## 原始输入在哪里

原始图像目录示例：

```text
rawdata/data/
├── dy_L0/
├── dy_L1/
├── SSH_L0/
├── SSH_L1/
├── zyh_R0/
└── ...
```

规则：

- 每个一级子文件夹名 = 一个 `finger_id`
- 图像原始尺度为 `100×110`
- 支持 `.png`、`.jpg`、`.jpeg`、`.bmp`、`.tif`、`.tiff`
- 自动忽略 `__MACOSX`、`.DS_Store`、隐藏文件和非图像文件

---

## 步骤 1：生成 labels.csv

**脚本：** `src/make_pairs/build_labels_from_folders.py`

**作用：** 扫描 `--data_root` 下的一级子文件夹，将文件夹名作为 `finger_id`，收集所有图像相对路径，写入 `labels.csv`。

**运行命令（在项目根目录执行）：**

```bash
python src/make_pairs/build_labels_from_folders.py --data_root rawdata/data --output_csv data/labels.csv
```

**主要参数：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--data_root` | （必填） | 原始图像根目录 |
| `--output_csv` | （必填） | 输出 `labels.csv` 路径 |
| `--relative_to` | `.` | `image_path` 的相对基准目录，通常为项目根目录 |
| `--print_summary` | `true` | 是否打印每个 `finger_id` 的图像数量 |

**输出示例：** `data/labels.csv`

```text
image_path,finger_id
rawdata/data/dy_L0/pair_1.bmp,dy_L0
rawdata/data/SSH_L0/pair_1.bmp,SSH_L0
```

---

## 步骤 2：划分数据集并构造图像对

**脚本：** `src/make_pairs/make_pairs.py`

**作用：**

1. 读取 `labels.csv`
2. 按 `finger_id` 划分训练集、验证集、测试集（**不按图像随机划分**，避免数据泄露）
3. 在每个划分内部独立采样正样本对和负样本对

**运行命令：**

```bash
python src/make_pairs/make_pairs.py --label_csv data/labels.csv --output_dir data --train_ratio 0.7 --val_ratio 0.15 --test_ratio 0.15 --pos_neg_ratio 1.0 --seed 42
```

**主要参数：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--label_csv` | （必填） | 步骤 1 生成的 `labels.csv` |
| `--output_dir` | （必填） | 输出目录，通常为 `data` |
| `--train_ratio` | `0.7` | 训练集 `finger_id` 比例 |
| `--val_ratio` | `0.15` | 验证集 `finger_id` 比例 |
| `--test_ratio` | `0.15` | 测试集 `finger_id` 比例 |
| `--pos_neg_ratio` | `1.0` | 负样本数 / 正样本数，尽量保持 1:1 |
| `--max_pos_pairs_per_finger` | `200` | 每个 `finger_id` 最多采样正样本对数；`0` 表示保留全部组合 |
| `--seed` | `42` | 随机种子，保证划分可复现 |

**划分与采样规则：**

- 划分单位：`finger_id`，不是单张图像
- 正样本对：同一 `finger_id` 内两张图，`label=1`
- 负样本对：不同 `finger_id` 各取一张图，`label=0`
- 各 split 使用独立随机种子：`train=seed+0`，`val=seed+1`，`test=seed+2`
- 若某 `finger_id` 图像少于 2 张，无法构造正样本对，脚本会警告

**输出文件：**

```text
data/
├── labels.csv           # 步骤 1 生成
├── labels_train.csv
├── labels_val.csv
├── labels_test.csv
├── pairs_train.csv
├── pairs_val.csv
└── pairs_test.csv
```

标签文件字段：

```text
image_path,finger_id
```

图像对文件字段：

```text
img1,img2,label,finger_id1,finger_id2
```

---

## 一键运行完整流程

在项目根目录依次执行：

```bash
# 步骤 1：生成全量标签
python src/make_pairs/build_labels_from_folders.py --data_root rawdata/data --output_csv data/labels.csv

# 步骤 2：划分并构造图像对
python src/make_pairs/make_pairs.py --label_csv data/labels.csv --output_dir data --train_ratio 0.7 --val_ratio 0.15 --test_ratio 0.15 --pos_neg_ratio 1.0 --seed 42
```

---

## 配置文件

默认参数写在：

```text
src/make_pairs/config.yaml
```

其中包含原始数据路径、两个脚本的参数、输出文件说明，以及下游三种方法分别使用哪些 CSV。当前脚本仍通过命令行传参运行，`config.yaml` 用于记录和复现实验。

---

## 下游方法如何使用

后续实验读取 CSV 时，通常指定 `--image_root .`，表示 `image_path` 相对**项目根目录**解析。

| 方法 | 使用的文件 |
|------|-----------|
| SIFT | `pairs_val.csv`、`pairs_test.csv` |
| Siamese | `pairs_train.csv`、`pairs_val.csv`、`pairs_test.csv` |
| Class-aware MoCo | 训练用 `labels_train.csv`；验证/测试用 `pairs_val.csv`、`pairs_test.csv` |

---

## 注意事项

1. `data/` 是**输出目录**，原始图像应放在 `rawdata/data/` 目录，不要混放。
2. 测试集不能参与训练，也不能参与阈值选择。
3. 数据量较小时，某个 split 可能分配到 0 个 `finger_id`，脚本会给出警告。
4. 若负样本目标数量超过理论上限，脚本会自动下调并给出警告。
