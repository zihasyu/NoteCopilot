# LoRA: Low-Rank Adaptation of Large Language Models

## 基本信息

- **标题**: LoRA: Low-Rank Adaptation of Large Language Models
- **作者**: Edward J. Hu, Yelong Shen, Phillip Wallis, et al.
- **发表**: ICLR 2022
- **机构**: Microsoft Corporation
- **链接**: [arXiv:2106.09685](https://arxiv.org/abs/2106.09685)

## 核心思想

### 问题背景

大模型微调面临的挑战：
1. **存储成本高**: GPT-3 175B参数的完整微调需要存储175B参数
2. **部署困难**: 每个下游任务都需要部署一个完整模型副本
3. **硬件要求**: 消费级GPU难以承受大模型训练

### LoRA解决方案

**核心假设**: 在适应特定任务时，权重更新的内在维度较低

$$W = W_0 + \Delta W = W_0 + BA$$

其中：
- $W_0 \in \mathbb{R}^{d \times k}$: 预训练权重（冻结）
- $B \in \mathbb{R}^{d \times r}$: 可训练低秩矩阵
- $A \in \mathbb{R}^{r \times k}$: 可训练低秩矩阵
- $r \ll \min(d, k)$: 低秩（通常r=4,8,16）

## 方法细节

### 实现要点

```python
# 原始前向传播
h = W_0 @ x

# LoRA前向传播
h = W_0 @ x + (B @ A) @ x
    = W_0 @ x + B @ (A @ x)
```

**初始化策略**:
- $A$ 使用随机高斯初始化
- $B$ 初始化为零，保证训练开始时 $\Delta W = 0$

### 应用位置

在Transformer中，LoRA主要应用于：
1. **Query/Value投影矩阵**（推荐，效果最好）
2. Key投影矩阵
3. 输出投影矩阵
4. FFN层（效果有限，不推荐）

## 实验结果

### 参数效率

| 方法 | 可训练参数量 | GPT-3 175B存储 |
|------|-------------|----------------|
| Full Fine-tuning | 175B | 350GB (FP16) |
| BitFit | 0.1% | 0.35GB |
| Adapter | 0.6% | 2.1GB |
| **LoRA (r=4)** | **0.01%** | **35MB** |
| **LoRA (r=16)** | **0.04%** | **140MB** |

### 性能对比 (RoBERTa base on GLUE)

| 方法 | MNLI | SST-2 | CoLA | Avg |
|------|------|-------|------|-----|
| Fine-tune | 90.2 | 94.8 | 62.4 | 82.5 |
| Adapter | 90.2 | 94.8 | 61.9 | 82.3 |
| **LoRA** | **90.6** | **95.1** | **63.4** | **83.0** |

### GPT-3实验 (E2E NLG Challenge)

| 方法 | BLEU | NIST | METEOR | ROUGE-L |
|------|------|------|--------|---------|
| Fine-tune | 68.2 | 8.62 | 46.2 | 71.0 |
| Adapter | 68.9 | 8.68 | 46.1 | 71.3 |
| **LoRA** | **70.4** | **8.85** | **46.6** | **71.6** |

## 优势分析

### 1. 训练效率

| 指标 | Full FT | LoRA (r=16) |
|------|---------|-------------|
| 可训练参数 | 100% | 0.04% |
| 训练时间 | 4.5h | 2.1h |
| 显存占用 | 28GB | 14GB |
| 检查点大小 | 350GB | 140MB |

### 2. 部署灵活性

- **多任务部署**: 存储1个基础模型 + N个LoRA适配器
- **快速切换**: 运行时切换不同适配器
- **组合使用**: 多个LoRA可以线性组合

## 关键发现

### 低秩假设验证

实验发现：
- r=4 就能达到接近最优的效果
- r增大到16、32效果提升有限
- 说明权重更新的内在维度确实很低

### 与全量微调对比

```
秩r | 参数量 | 相对性能
----|--------|----------
1   | 0.002% | 95%
2   | 0.005% | 98%
4   | 0.01%  | 99%
8   | 0.02%  | 99.5%
16  | 0.04%  | 100% (与FT相当)
```

## 最佳实践

### 参数选择

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| rank r | 4-16 | 小数据集用4，大数据集用16 |
| alpha | 2*r | 经验最优比例 |
| dropout | 0.05-0.1 | 防止过拟合 |
| learning rate | 1e-4 ~ 3e-4 | 比全量微调大一点 |
| batch size | 根据显存调整 | 越大越好 |

### 应用建议

1. **优先应用位置**: Q, V投影矩阵
2. **数据集小** (<10k): r=4, alpha=8
3. **数据集大** (>100k): r=16, alpha=32
4. **多任务场景**: 每个任务一个LoRA适配器

## 后续发展

基于LoRA的改进方法：

- **QLoRA** (2023): 4-bit量化 + LoRA，单卡微调65B模型
- **DoRA** (2024): 权重分解低秩适应，效果更好
- **LoRA-FA**: 冻结A矩阵只训练B，进一步减少参数
- **Multi-LoRA**: 多适配器联合训练

## 关键引用

```bibtex
@inproceedings{hu2022lora,
  title={LoRA: Low-Rank Adaptation of Large Language Models},
  author={Hu, Edward J and Shen, Yelong and Wallis, Phillip and others},
  booktitle={ICLR},
  year={2022}
}
```

## 相关论文

- [Parameter-Efficient Transfer Learning for NLP (Adapter)](https://arxiv.org/abs/1902.00751)
- [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314)
- [DoRA: Weight-Decomposed Low-Rank Adaptation](https://arxiv.org/abs/2402.09353)

## 个人思考

LoRA的优雅之处在于它抓住了大模型适应的本质：**真正需要学习的只是很小的一部分**。这不仅是计算效率的提升，更是对神经网络本质的深刻洞察。实际使用中，LoRA+QLoRA的组合让个人研究者也能微调大模型，极大地降低了大模型应用的门槛。
