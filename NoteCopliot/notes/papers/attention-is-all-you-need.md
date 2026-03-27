# Attention Is All You Need - 论文笔记

## 基本信息

- **标题**: Attention Is All You Need
- **作者**: Ashish Vaswani, Noam Shazeer, Niki Parmar, et al.
- **发表**: NIPS 2017
- **机构**: Google Brain, Google Research
- **链接**: [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)

## 核心贡献

1. **提出Transformer架构**: 完全基于注意力机制，摒弃RNN和CNN
2. **实现并行计算**: 通过自注意力机制实现序列并行处理
3. **达到SOTA性能**: 在机器翻译任务上超越当时的最优方法

## 关键创新

### 1. Multi-Head Attention (多头注意力)

```python
# 核心思想：将输入投影到多个子空间分别计算注意力
MultiHead(Q, K, V) = Concat(head_1, ..., head_h)W^O
where head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
```

**优势**:
- 不同头可以关注不同特征（语法、语义、指代等）
- 增加模型表达能力
- 计算可并行

### 2. Self-Attention (自注意力)

**核心思想**: 计算序列中每个位置与其他所有位置的关联权重

**复杂度对比**:

| 层类型 | 每层复杂度 | 顺序操作数 | 最大路径长度 |
|--------|------------|------------|--------------|
| Self-Attention | O(n²·d) | O(1) | O(1) |
| Recurrent | O(n·d²) | O(n) | O(n) |
| Convolutional | O(k·n·d²) | O(1) | O(log_k(n)) |

### 3. Positional Encoding (位置编码)

由于Transformer没有递归和卷积，需要显式注入位置信息：

```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

**特点**:
- 可以外推到训练时未见过的长度
- 相对位置可以线性表达

## 模型架构

```
Input Embedding
    ↓
Positional Encoding
    ↓
[Encoder] × N                    [Decoder] × N
  ├─ Multi-Head Attention            ├─ Masked Multi-Head Attention
  ├─ Add & Norm                      ├─ Add & Norm
  ├─ Feed Forward                    ├─ Multi-Head Attention (Encoder-Decoder)
  └─ Add & Norm                      ├─ Add & Norm
                                     ├─ Feed Forward
                                     └─ Add & Norm
                                              ↓
                                         Linear + Softmax
```

## 实验结果

### 机器翻译

| 模型 | EN-DE BLEU | EN-FR BLEU | 训练时间 |
|------|------------|------------|----------|
| GNMT | 24.6 | 39.92 | - |
| ConvS2S | 25.16 | 40.46 | - |
| **Transformer (base)** | **27.3** | **38.1** | 12h (8 P100) |
| **Transformer (big)** | **28.4** | **41.8** | 3.5 days (8 P100) |

### 模型变体对比

| 变体 | N | d_model | d_ff | h | 参数量 | BLEU |
|------|---|---------|------|---|--------|------|
| base | 6 | 512 | 2048 | 8 | 65M | 27.3 |
| big | 6 | 1024 | 4096 | 16 | 213M | 28.4 |

## 个人理解

### 为什么Transformer有效？

1. **全局依赖**: 任意两个位置的距离都是O(1)，长距离依赖建模能力强
2. **可解释性**: 注意力权重可以直接可视化
3. **可扩展性**: 增加层数和参数量效果持续提升

### 局限性

1. **计算复杂度**: 自注意力是O(n²)，长序列成本高
2. **位置信息弱**: 不如RNN的位置建模自然
3. **需要大量数据**: 小数据量下不如LSTM

## 影响与后续工作

Transformer已成为NLP领域的基石架构：

- **BERT** (2018): 基于Transformer Encoder的预训练模型
- **GPT系列** (2018-2023): 基于Transformer Decoder的生成模型
- **ViT** (2020): 将Transformer应用于视觉领域
- **各种变体**: XLNet, RoBERTa, ALBERT, T5, etc.

## 关键引用

```bibtex
@inproceedings{vaswani2017attention,
  title={Attention is all you need},
  author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and others},
  booktitle={NIPS},
  year={2017}
}
```

## 相关论文

- [BERT: Pre-training of Deep Bidirectional Transformers](https://arxiv.org/abs/1810.04805)
- [Improving Language Understanding by Generative Pre-Training (GPT)](https://s3-us-west-2.amazonaws.com/openai-assets/research-covers/language-unsupervised/language_understanding_paper.pdf)
- [Linformer: Self-Attention with Linear Complexity](https://arxiv.org/abs/2006.04768)
