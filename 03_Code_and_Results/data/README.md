# Lasso 项目的输入数据

这里已准备真实与合成回归数据，并固定训练与测试划分。所有文件都是输入数据，没有运行优化算法，也没有实验结果。

## 文件与来源

| 文件 | 样本数 | 特征数 | 训练与测试 | 用途 |
| --- | ---: | ---: | --- | --- |
| [diabetes.csv](diabetes.csv) | 442 | 10 | 353 与 89 | 真实回归展示 |
| [synthetic_seed0.csv](synthetic_seed0.csv) | 300 | 50 | 240 与 60 | 合成稀疏回归 |
| [synthetic_seed1.csv](synthetic_seed1.csv) | 300 | 50 | 240 与 60 | 同一规则的另一个实例 |
| [synthetic_seed2.csv](synthetic_seed2.csv) | 300 | 50 | 240 与 60 | 同一规则的另一个实例 |

Diabetes 是连续响应的回归数据，不是糖尿病诊断二分类数据。研究出处为 Efron 等人的 Least Angle Regression，实际分发文件来自 scikit-learn 官方仓库的固定版本 1.9.1：[特征文件](https://github.com/scikit-learn/scikit-learn/blob/1.9.1/sklearn/datasets/data/diabetes_data_raw.csv.gz)、[响应文件](https://github.com/scikit-learn/scikit-learn/blob/1.9.1/sklearn/datasets/data/diabetes_target.csv.gz)、[数据说明](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_diabetes.html)。两份原始压缩文件同时保留在本目录，CSV 使用未标准化特征。

合成数据使用独立标准正态特征、5 个非零系数和标准差为 0.5 的正态噪声。三个实例分别使用种子 0、1、2。真实系数、生成规则、源文件哈希和 NumPy 版本保存在 [manifest.json](manifest.json)。不要将这些人工生成样本或数据集尺寸写成优化性能结果。

## CSV 字段与划分

- `row_id` 是原始行号，从 0 开始，不是输入特征。
- `split` 为 `train` 或 `test`，也不是输入特征。
- 中间各列是特征；Diabetes 使用 `age, sex, bmi, bp, s1, s2, s3, s4, s5, s6`，合成数据使用 `x0` 至 `x49`。
- `target` 是回归响应，不是输入特征。

划分已写入文件，不需要重新随机划分。对每个数据集，用独立的 `numpy.random.default_rng(split_seed)` 置换行号，前 `ceil(0.2 * N)` 行号作为测试集。Diabetes 的划分种子为 0，合成数据的划分种子与生成种子相同。复现时以 CSV 中的 `split` 为准，避免其他库的随机数规则不同。

## 后续训练预处理

先选出训练与测试行，再只用训练集计算特征均值和总体标准差。用这些统计量转换训练与测试特征；删除训练集中零方差的特征。响应减去训练集响应均值，测试预测加回该均值。这样截距不受惩罚。

三个算法必须共享完全相同的转换数据、零初值和正则化参数。主实验使用训练数据计算的 `lambda_max = max(abs(X.T @ y)) / n`，再取 `lambda = 0.1 * lambda_max`，不用测试数据选择参数。

若标准化后的系数为 `w_std`，原始尺度的系数为 `w_std / feature_std`；原始截距为 `target_mean - feature_mean @ w_raw`。合成数据的真实系数在原始尺度，画系数对照图时先做这个换算。

## 数据准备脚本

[prepare_data.py](../scripts/prepare_data.py) 只下载两份公开原始文件、生成合成输入并写入固定划分，需要 Python 和 NumPy。它不包含训练算法。CSV 已准备好，后续实验可以直接读取，无需再次运行下载。
