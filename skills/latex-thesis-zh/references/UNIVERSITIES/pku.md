# 北京大学论文模板 (pkuthss)

## 模板信息
- **模板名称**: pkuthss
- **GitHub**: https://github.com/CasperVector/pkuthss
- **文档类**: `\documentclass[doctor]{pkuthss}`

## 特殊格式要求

### 图表编号
- 格式：`图3.1` / `表3.1`（章号.序号，用点号）
- 配置：模板自动处理

### 参考文献
- 样式：`biblatex-gb7714-2015`
- 推荐：使用 biblatex

### 特殊章节
- 必须包含"符号说明"章节
- 符号表格式有特定要求

## 编译方式

```bash
# 使用 latexmk
latexmk -xelatex thesis.tex

# 使用 make（如果有 Makefile）
make
```

## 常用命令

```latex
% 文档类选项
\documentclass[
  doctor,           % 博士论文
  % master,         % 硕士论文
  openany,          % 章节可在任意页开始
  oneside,          % 单面打印
]{pkuthss}

% 封面信息
\pkuthssinfo{
  cthesisname = {博士研究生学位论文},
  ethesisname = {Doctor Thesis},
  ctitle = {论文标题},
  etitle = {English Title},
  cauthor = {作者姓名},
  eauthor = {Author Name},
  studentid = {学号},
  date = {\zhdigits{2024}年\zhnumber{6}月},
  school = {信息科学技术学院},
  cmajor = {计算机软件与理论},
  emajor = {Computer Software and Theory},
  direction = {研究方向},
  cmentor = {导师姓名},
  ementor = {Supervisor Name},
  ckeywords = {关键词1，关键词2，关键词3},
  ekeywords = {keyword1, keyword2, keyword3},
}
```

## 注意事项

1. 使用 XeLaTeX 编译
2. 符号说明章节是必需的
3. 注意检查页眉格式
4. 参考文献格式需严格遵循
