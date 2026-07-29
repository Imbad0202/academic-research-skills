## E. 原始（修訂前）稿件節錄

> **2.2 研究倫理。** 本研究經 Northfield 大學研究倫理委員會核准（計畫編號 2019-114），
> 核准日期為 2019 年 3 月 14 日。
>
> **3.1 設計與樣本。** 訪談 26 位行政職員。資料蒐集期間為 2018 年 9 月至 2019 年 6 月。
>
> **4. 研究發現。** 自逐字稿發展出三個主題：工作量位移、界線侵蝕、非正式專業。

## F. 修訂後稿件節錄

> **2.2 研究倫理。** 本研究經 Northfield 大學研究倫理委員會核准（計畫編號 2019-114），
> 核准日期為 2019 年 3 月 14 日。參與者於訪談前至少七天收到書面說明，並於訪談開始時簽署
> 書面同意；兩份文件皆載明退出權利。
>
> **3.1 設計與樣本。** 訪談 26 位行政職員，以跨四個職務族群與三個校區的最大變異立意取樣
> 選出。參與者透過各校區教職員發展辦公室發出的邀請招募，另發兩次提醒。資料蒐集期間為
> 2018 年 9 月至 2019 年 6 月。
>
> **4. 研究發現。** 自逐字稿發展出三個主題：工作量位移、界線侵蝕、非正式專業。

## G. 修訂 patch 與 apply report

**Patch（節錄）**

```diff
--- a/manuscript.md
+++ b/manuscript.md
@@ 2.2 研究倫理 @@
 核准日期為 2019 年 3 月 14 日。
+參與者於訪談前至少七天收到書面說明，並於訪談開始時簽署
+書面同意；兩份文件皆載明退出權利。
@@ 3.1 設計與樣本 @@
-訪談 26 位行政職員。資料蒐集期間為 2018 年 9 月至 2019 年 6 月。
+訪談 26 位行政職員，以跨四個職務族群與三個校區的最大變異立意取樣
+選出。參與者透過各校區教職員發展辦公室發出的邀請招募，另發兩次提醒。資料蒐集期間為
+2018 年 9 月至 2019 年 6 月。
```

**Apply report**

```json
{
  "report_format_version": "1.2",
  "base_draft_hash": "<<BASE_DRAFT_HASH>>",
  "output_draft_hash": "<<OUTPUT_DRAFT_HASH>>",
  "patch_digest": "<<PATCH_DIGEST>>",
  "hunks_applied": 2,
  "hunks_rejected": 0
}
```

## I. Input manifest 存在性宣告（§11）

九項 artifact 全部 **present**，`cross_model_active: false`，`round_id: "p6-r2"`。

| Artifact | 存在性 | 來源 |
|----------|--------|------|
| `original_manuscript` | present | arm §E |
| `revised_manuscript` | present | arm §F |
| `revision_roadmap` | present | 資料包 §A |
| `editorial_decision_letter` | present | 資料包 §B |
| `response_to_reviewers` | present | 資料包 §H |
| `revision_patches` | present，1 筆 | arm §G |
| `apply_reports` | present，1 筆 | arm §G |
| `round1_findings` | present | 資料包 §C |
| `round1_config_cards` | present | 資料包 §D |

**雜湊蓋章。** 同其他情境，manifest 的 `sha256` 與 §G 內的 `<<…>>` 佔位符由派工層在
派工當下計算並替換。
