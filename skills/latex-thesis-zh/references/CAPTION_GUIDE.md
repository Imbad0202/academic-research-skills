# 图表标题（Caption）生成与优化指南

当用户要求为图表生成英文标题或中英双语标题时，请遵循以下规范。由于中文学位论文（如各大高校基于国标的模板：thuthesis, pkuthss等）通常要求图表采用**中英双语**形式，因此生成的英文必须精确且符合特定格式。

## 1. 英文格式规范

- 如果翻译结果是名词性短语：使用 **Title Case** 格式，即所有实词的首字母大写，末尾不加句号。
- 如果翻译结果是完整句子：使用 **Sentence case** 格式，即仅第一个单词的首字母大写，其余小写（专有名词除外），末尾必须加句号。

## 2. 写作风格（极简与去AI味）

- 直接描述图表内容：去除“The figure shows”或“This diagram illustrates”这类冗余开头。直接以 `Architecture of...`, `Performance comparison of...`, `Visualization of...` 开头。
- 表格图表常用句式：对于表格，推荐使用 `Comparison with...`, `Ablation study on...`, `Results on...` 等标准学术表达。
- 避免使用复杂的生僻词，如 showcase, depict 等，请直接使用 show, compare, present。

## 3. 双语输出说明（\bicaption）

中文学位论文通常使用 `bicaption` 宏包或其他类似机制来实现双语标题。请提示用户将结果放置入如下格式中：

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\textwidth]{figures/example.pdf}
  \bicaption{中文标题}{English Title in Title Case or Sentence Case}
  \label{fig:example}
\end{figure}
```

注意 LaTeX 的语法转义：必须对特殊字符（如 `%`、`_`、`&`）进行转义。如有数学公式，保持 `$` 包裹。

## 4. 输出示例

**用户输入：**
为这个图生成双语标题：本图展示了不同模型在三个数据集上的准确率对比。

**Agent 回复：**
```latex
% 图表标题 [Severity: Minor] [Priority: P2]: 建议使用双语 caption
% 中文标题：不同模型在三个数据集上的准确率对比
% English Title：Accuracy comparison of different models across three datasets
% 
% 示例用法：
% \bicaption{不同模型在三个数据集上的准确率对比}{Accuracy comparison of different models across three datasets}
```
