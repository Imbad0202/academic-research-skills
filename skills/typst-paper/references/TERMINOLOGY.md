# Academic Terminology Reference


## 目录

- [Usage / 使用说明](#usage-使用说明)
- [1. Deep Learning / 深度学习](#1-deep-learning-深度学习)
  - [1.1 Basic Concepts / 基础概念](#11-basic-concepts-基础概念)
  - [1.2 Training / 训练相关](#12-training-训练相关)
  - [1.3 Model Architecture / 模型架构](#13-model-architecture-模型架构)
- [2. Time Series / 时间序列](#2-time-series-时间序列)
  - [2.1 Basic Concepts / 基础概念](#21-basic-concepts-基础概念)
  - [2.2 Analysis Methods / 分析方法](#22-analysis-methods-分析方法)
  - [2.3 Models / 模型](#23-models-模型)
  - [2.4 Evaluation / 评估指标](#24-evaluation-评估指标)
- [3. Industrial Control / 工业控制](#3-industrial-control-工业控制)
  - [3.1 Basic Concepts / 基础概念](#31-basic-concepts-基础概念)
  - [3.2 Control Methods / 控制方法](#32-control-methods-控制方法)
  - [3.3 Industrial Systems / 工业系统](#33-industrial-systems-工业系统)
  - [3.4 Fault & Anomaly / 故障与异常](#34-fault-anomaly-故障与异常)
  - [3.5 Data Characteristics / 数据特性](#35-data-characteristics-数据特性)
- [4. Cross-Domain Terms / 跨领域术语](#4-cross-domain-terms-跨领域术语)
  - [4.1 General Academic / 通用学术](#41-general-academic-通用学术)
  - [4.2 Data & Processing / 数据与处理](#42-data-processing-数据与处理)
- [5. Usage Examples / 使用示例](#5-usage-examples-使用示例)
  - [❌ Chinglish → ✅ Academic English](#chinglish-academic-english)
- [Notes / 备注](#notes-备注)

---

> 学术术语对照表 - 深度学习、时间序列、工业控制领域

## Usage / 使用说明

When translating Chinese academic text to English, refer to this terminology list to ensure:
1. Consistent terminology throughout the paper
2. Domain-appropriate expressions
3. Commonly accepted translations in the field

---

## 1. Deep Learning / 深度学习

### 1.1 Basic Concepts / 基础概念

| 中文 | English | Notes |
|------|---------|-------|
| 深度学习 | deep learning | |
| 神经网络 | neural network | |
| 卷积神经网络 | convolutional neural network (CNN) | |
| 循环神经网络 | recurrent neural network (RNN) | |
| 长短期记忆网络 | long short-term memory (LSTM) | |
| 门控循环单元 | gated recurrent unit (GRU) | |
| Transformer | Transformer | 保持原文，首字母大写 |
| 注意力机制 | attention mechanism | |
| 自注意力 | self-attention | |
| 多头注意力 | multi-head attention | |
| 前馈神经网络 | feed-forward neural network | |
| 残差连接 | residual connection / skip connection | |
| 层归一化 | layer normalization | |
| 批归一化 | batch normalization | |

### 1.2 Training / 训练相关

| 中文 | English | Notes |
|------|---------|-------|
| 损失函数 | loss function | |
| 优化器 | optimizer | |
| 学习率 | learning rate | |
| 梯度下降 | gradient descent | |
| 反向传播 | backpropagation | |
| 过拟合 | overfitting | |
| 欠拟合 | underfitting | |
| 正则化 | regularization | |
| Dropout | dropout | 小写 |
| 早停 | early stopping | |
| 权重衰减 | weight decay | |
| 批大小 | batch size | |
| 轮次/周期 | epoch | |
| 收敛 | convergence | |
| 梯度消失 | vanishing gradient | |
| 梯度爆炸 | exploding gradient | |

### 1.3 Model Architecture / 模型架构

| 中文 | English | Notes |
|------|---------|-------|
| 编码器 | encoder | |
| 解码器 | decoder | |
| 嵌入层 | embedding layer | |
| 隐藏层 | hidden layer | |
| 输出层 | output layer | |
| 激活函数 | activation function | |
| 池化 | pooling | |
| 全连接层 | fully connected layer / dense layer | |
| 特征提取 | feature extraction | |
| 特征融合 | feature fusion | |
| 多尺度 | multi-scale | |
| 端到端 | end-to-end | |

---

## 2. Time Series / 时间序列

### 2.1 Basic Concepts / 基础概念

| 中文 | English | Notes |
|------|---------|-------|
| 时间序列 | time series | |
| 时序数据 | temporal data / time-series data | |
| 时间步 | time step | |
| 滑动窗口 | sliding window | |
| 时间戳 | timestamp | |
| 采样频率 | sampling frequency / sampling rate | |
| 采样间隔 | sampling interval | |

### 2.2 Analysis Methods / 分析方法

| 中文 | English | Notes |
|------|---------|-------|
| 时序预测 | time series forecasting | |
| 单步预测 | single-step prediction | |
| 多步预测 | multi-step prediction | |
| 长期预测 | long-term forecasting | |
| 短期预测 | short-term forecasting | |
| 趋势 | trend | |
| 季节性 | seasonality | |
| 周期性 | periodicity / cyclicity | |
| 平稳性 | stationarity | |
| 自相关 | autocorrelation | |
| 滞后 | lag | |
| 差分 | differencing | |

### 2.3 Models / 模型

| 中文 | English | Notes |
|------|---------|-------|
| 自回归模型 | autoregressive model (AR) | |
| 移动平均 | moving average (MA) | |
| 自回归移动平均 | ARMA | |
| 自回归积分移动平均 | ARIMA | |
| 指数平滑 | exponential smoothing | |
| 时序分解 | time series decomposition | |
| 状态空间模型 | state space model | |
| 时序Transformer | Temporal Transformer | |
| 时序卷积网络 | temporal convolutional network (TCN) | |

### 2.4 Evaluation / 评估指标

| 中文 | English | Notes |
|------|---------|-------|
| 均方误差 | mean squared error (MSE) | |
| 均方根误差 | root mean squared error (RMSE) | |
| 平均绝对误差 | mean absolute error (MAE) | |
| 平均绝对百分比误差 | mean absolute percentage error (MAPE) | |
| 对称平均绝对百分比误差 | symmetric MAPE (sMAPE) | |
| 决定系数 | coefficient of determination (R²) | |

---

## 3. Industrial Control / 工业控制

### 3.1 Basic Concepts / 基础概念

| 中文 | English | Notes |
|------|---------|-------|
| 工业控制系统 | industrial control system (ICS) | |
| 过程控制 | process control | |
| 控制回路 | control loop | |
| 闭环控制 | closed-loop control | |
| 开环控制 | open-loop control | |
| 反馈控制 | feedback control | |
| 前馈控制 | feedforward control | |
| 设定值 | setpoint | |
| 过程变量 | process variable (PV) | |
| 控制变量 | control variable / manipulated variable (MV) | |
| 扰动 | disturbance | |

### 3.2 Control Methods / 控制方法

| 中文 | English | Notes |
|------|---------|-------|
| PID控制 | PID control | |
| 比例控制 | proportional control | |
| 积分控制 | integral control | |
| 微分控制 | derivative control | |
| 模型预测控制 | model predictive control (MPC) | |
| 自适应控制 | adaptive control | |
| 鲁棒控制 | robust control | |
| 最优控制 | optimal control | |
| 智能控制 | intelligent control | |

### 3.3 Industrial Systems / 工业系统

| 中文 | English | Notes |
|------|---------|-------|
| 可编程逻辑控制器 | programmable logic controller (PLC) | |
| 分布式控制系统 | distributed control system (DCS) | |
| 监控与数据采集 | SCADA | Supervisory Control and Data Acquisition |
| 人机界面 | human-machine interface (HMI) | |
| 传感器 | sensor | |
| 执行器 | actuator | |
| 变频器 | variable frequency drive (VFD) | |

### 3.4 Fault & Anomaly / 故障与异常

| 中文 | English | Notes |
|------|---------|-------|
| 故障检测 | fault detection | |
| 故障诊断 | fault diagnosis | |
| 故障预测 | fault prediction / fault prognosis | |
| 异常检测 | anomaly detection | |
| 预测性维护 | predictive maintenance | |
| 剩余使用寿命 | remaining useful life (RUL) | |
| 健康状态 | health state / health condition | |
| 退化 | degradation | |
| 报警 | alarm | |
| 阈值 | threshold | |

### 3.5 Data Characteristics / 数据特性

| 中文 | English | Notes |
|------|---------|-------|
| 工业数据 | industrial data | |
| 传感器数据 | sensor data | |
| 多变量 | multivariate | |
| 高维数据 | high-dimensional data | |
| 噪声 | noise | |
| 缺失值 | missing values | |
| 不平衡数据 | imbalanced data | |
| 标签稀缺 | label scarcity | |

---

## 4. Cross-Domain Terms / 跨领域术语

### 4.1 General Academic / 通用学术

| 中文 | English | Notes |
|------|---------|-------|
| 提出 | propose / present | |
| 方法 | method / approach | |
| 框架 | framework | |
| 模型 | model | |
| 算法 | algorithm | |
| 实验 | experiment | |
| 验证 | validation / verification | |
| 评估 | evaluation / assessment | |
| 基准 | baseline / benchmark | |
| 消融实验 | ablation study | |
| 对比实验 | comparative experiment | |
| 案例研究 | case study | |
| 泛化能力 | generalization capability | |
| 可解释性 | interpretability / explainability | |
| 鲁棒性 | robustness | |
| 可扩展性 | scalability | |

### 4.2 Data & Processing / 数据与处理

| 中文 | English | Notes |
|------|---------|-------|
| 数据集 | dataset | |
| 训练集 | training set | |
| 验证集 | validation set | |
| 测试集 | test set | |
| 数据预处理 | data preprocessing | |
| 数据增强 | data augmentation | |
| 归一化 | normalization | |
| 标准化 | standardization | |
| 特征工程 | feature engineering | |
| 降维 | dimensionality reduction | |

---

## 5. Usage Examples / 使用示例

### ❌ Chinglish → ✅ Academic English

| 中文原文 | ❌ 直译 | ✅ 学术表达 |
|----------|---------|-------------|
| 本文提出了一种新方法 | This paper puts forward a new method | We propose a novel approach |
| 取得了很好的效果 | get good effect | achieves superior performance |
| 和传统方法相比 | Compared with traditional method | Compared with conventional methods |
| 实验结果表明 | Experiment result shows | Experimental results demonstrate that |
| 具有重要意义 | has important meaning | is of significant importance |

---

## Notes / 备注

1. 术语首次出现时使用全称，后续可用缩写
2. 专有名词（如 Transformer, LSTM）保持原文
3. 根据具体会议/期刊要求调整术语使用
4. 本表可根据具体研究方向扩展
