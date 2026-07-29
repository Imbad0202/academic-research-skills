## E. 原始（修訂前）稿件

未提供。本次投稿的修訂前稿件從未存入 passport，且作者是在工具鏈之外完成修訂。

## F. 修訂後稿件節錄

> **3.1 樣本。** 共 904 名學生完成調查，分布於四個學院，相對於 2,372 人的抽樣框，
> 回收率為 38.1%。回應者與抽樣框在修業年級與學院上的比較列於表 1；回應者中應屆生
> 高估了 4.2 個百分點。
>
> **4. 結果。**
>
> **4.1 測量模型。** 18 題的驗證性因素分析支持本樣本上的單因素解
> （CFI = .94、RMSEA = .058、SRMR = .043）。
>
> **4.2 總分。** 投入總分平均為 3.42（SD = 0.71）。應屆生的總分較高
> （b = 0.19，SE = 0.06，p = .002）。
>
> **4.4 次群體差異。** 我們另檢視九個人口次群體（性別、修業年級、學院、第一代大學生
> 身分、國際生身分、經費來源、身心障礙身分、就讀方式、年齡組）在總分上的差異。九個
> 對比中有三個在 p < .05 達顯著：第一代大學生低 0.14（p = .031）、國際生低 0.17
> （p = .019）、兼時生低 0.21（p = .008）。這些差異指出了需要針對性介入的群體。
>
> **5. 討論。** 投入程度隨修業歷程上升，且在第一代大學生、國際生與兼時生身上較低。

## G. 修訂 patch 與 apply report

未提供。修訂直接在作者自己的稿件檔上完成，未經 `ars_apply_revision_patch.py` 套用，
因此既無 patch 也無 apply report。

## I. Input manifest 存在性宣告（§11）

`cross_model_active: false`，`round_id: "p3-r2"`。

| Artifact | 存在性 | 來源 |
|----------|--------|------|
| `original_manuscript` | **`{present: false}`** | — |
| `revised_manuscript` | present | arm §F |
| `revision_roadmap` | present | 資料包 §A |
| `editorial_decision_letter` | present | 資料包 §B |
| `response_to_reviewers` | present | 資料包 §H |
| `revision_patches` | **`{present: false}`** | — |
| `apply_reports` | **`{present: false}`** | — |
| `round1_findings` | present | 資料包 §C |
| `round1_config_cards` | present | 資料包 §D |

不存在的 artifact 不帶 ref、不帶雜湊、不帶新鮮度欄位，走的是 discriminated union 的
`present: false` 分支，絕不使用哨兵字串或捏造的雜湊值。兩個陣列型 artifact 皆使用
`{present: false}`，這就是「空」的正規編碼。

兩項硬性必要的 artifact（`revised_manuscript`、`revision_roadmap`）皆存在，因此本
manifest 完整，G0 不觸發。這些缺席是降級，不是中止。
