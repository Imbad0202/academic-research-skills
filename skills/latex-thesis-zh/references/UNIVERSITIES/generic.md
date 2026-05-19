# 通用中文论文模板


## 目录

- [适用场景](#适用场景)
- [基础配置](#基础配置)
- [章节设置](#章节设置)
- [图表编号](#图表编号)
- [字体配置](#字体配置)
- [编译方式](#编译方式)
- [注意事项](#注意事项)

---

## 适用场景
- 没有学校专用模板时使用
- 符合国家标准 GB/T 7713.1-2006

## 基础配置

```latex
\documentclass[12pt, a4paper]{ctexbook}

% 页面设置
\usepackage[
  top=3cm,
  bottom=2.5cm,
  left=3cm,
  right=2.5cm,
]{geometry}

% 参考文献
\usepackage[backend=biber, style=gb7714-2015]{biblatex}

% 图表标题
\usepackage{caption}
\captionsetup{
  font=small,
  labelsep=space,
  format=hang,
}

% 页眉页脚
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\leftmark}
\fancyfoot[C]{\thepage}
```

## 章节设置

```latex
% 章节标题格式
\ctexset{
  chapter = {
    format = \centering\heiti\zihao{3},
    nameformat = {},
    titleformat = {},
    number = \chinese{chapter},
    name = {第,章},
    aftername = \quad,
    beforeskip = 20pt,
    afterskip = 20pt,
  },
  section = {
    format = \heiti\zihao{4},
    aftername = \quad,
    beforeskip = 10pt,
    afterskip = 10pt,
  },
  subsection = {
    format = \heiti\zihao{-4},
    aftername = \quad,
    beforeskip = 8pt,
    afterskip = 8pt,
  },
}
```

## 图表编号

```latex
% 按章编号
\usepackage{amsmath}
\numberwithin{equation}{chapter}
\numberwithin{figure}{chapter}
\numberwithin{table}{chapter}

% 编号格式：3.1
\renewcommand{\thefigure}{\thechapter.\arabic{figure}}
\renewcommand{\thetable}{\thechapter.\arabic{table}}
\renewcommand{\theequation}{\thechapter.\arabic{equation}}
```

## 字体配置

```latex
% 确保系统有这些字体
\setCJKmainfont{SimSun}[
  BoldFont=SimHei,
  ItalicFont=KaiTi,
]
\setCJKsansfont{SimHei}
\setCJKmonofont{FangSong}

% 英文字体
\setmainfont{Times New Roman}
\setsansfont{Arial}
\setmonofont{Courier New}
```

## 编译方式

```bash
xelatex main
biber main
xelatex main
xelatex main
```

## 注意事项

1. 必须使用 XeLaTeX
2. 确保安装所需字体
3. 参考文献使用 biblatex + biber
4. 根据具体学校要求调整格式
