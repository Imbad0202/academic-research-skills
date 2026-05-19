# 清华大学论文模板 (thuthesis)

## 模板信息
- **模板名称**: thuthesis
- **GitHub**: https://github.com/tuna/thuthesis
- **文档类**: `\documentclass{thuthesis}`

## 特殊格式要求

### 图表编号
- 格式：`图 3-1` / `表 3-1`（章号-序号，用连字符）
- 配置：模板自动处理

### 参考文献
- 样式：`thubib.bst` 或 `biblatex-gb7714-2015`
- 命令：`\bibliography{refs}`

### 公式编号
- 格式：`(3-1)`（章号-序号）

### 页面设置
- 自动由模板处理
- 不要手动修改页边距

## 编译方式

```bash
# 推荐使用 latexmk
latexmk -xelatex main.tex

# 或手动编译
xelatex main
bibtex main
xelatex main
xelatex main
```

## 常用命令

```latex
% 封面信息
\thusetup{
  title = {论文标题},
  title* = {English Title},
  author = {作者姓名},
  supervisor = {导师姓名},
  degree-category = {工学博士},
}

% 摘要
\begin{abstract}
  摘要内容...
\end{abstract}

\begin{abstract*}
  English abstract...
\end{abstract*}

% 关键词
\thusetup{
  keywords = {关键词1, 关键词2, 关键词3},
  keywords* = {keyword1, keyword2, keyword3},
}
```

## 注意事项

1. 必须使用 XeLaTeX 编译
2. 确保系统安装中文字体（SimSun, SimHei, KaiTi）
3. 参考文献使用模板配套样式
4. 提交前检查模板版本是否为最新
