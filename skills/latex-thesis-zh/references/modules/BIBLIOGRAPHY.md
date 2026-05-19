# Bibliography Module Reference

Purpose: Validate references against GB/T 7714-2015 and check BibTeX/BibLaTeX configuration.

## Document Type Identifiers

| Type | Code | Example Format |
|------|------|---------------|
| Book | M | 作者. 书名[M]. 出版地: 出版社, 年份. |
| Journal | J | 作者. 题名[J]. 刊名, 年, 卷(期): 页码. |
| Thesis | D | 作者. 题名[D]. 城市: 学校, 年份. |
| Conference | C | 作者. 题名[C]//会议名. 城市, 年: 页码. |
| Patent | P | 发明人. 专利名[P]. 国别: 专利号, 日期. |
| Electronic | EB/OL | 作者. 题名[EB/OL]. (发布日期)[引用日期]. URL. |

## BibLaTeX Configuration (Recommended)

```latex
\usepackage[backend=biber,style=gb7714-2015]{biblatex}
\addbibresource{refs.bib}
\printbibliography[title=参考文献]
```

## BibTeX Alternative

```latex
\bibliographystyle{gbt7714-numerical}  % or gbt7714-author-year
\bibliography{refs}
```

## Common Issues

- **Author names**: Chinese surname first; English: Surname, Initials.
- **Multiple authors**: 3 or fewer: list all; 4+: first 3 + "等"/"et al."
- **DOI**: Must include when available (`doi = {10.xxxx/xxxxx}`)
- **Page numbers**: Use double dash `1--15` (not single dash or tilde)

> Full details: see [`../GB_STANDARD.md`](../GB_STANDARD.md) (sections 一–四)
