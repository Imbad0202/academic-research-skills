## A. 第一輪修訂路線圖（Schema 7，機器格式）

```json
{
  "items": [
    {
      "id": "REV-001",
      "description": "訪談樣本僅以人數描述。請說明取樣策略與招募管道。",
      "reviewer": "Peer Reviewer 2 (Domain)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "3.1 設計與樣本"},
      "confidence": 4,
      "competence_basis": "質性取樣通報",
      "target_section": "3.1 設計與樣本",
      "suggested_action": "說明取樣策略與參與者如何被招募。",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "具名說明取樣策略，並描述招募管道。"
    },
    {
      "id": "REV-002",
      "description": "分析一節寫出採用主題分析，卻從未說明由幾位分析者編碼，也未說明編碼歧異如何處理。",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "3.4 分析"},
      "confidence": 4,
      "competence_basis": "質性編碼程序通報",
      "target_section": "3.4 分析",
      "suggested_action": "說明由幾位分析者編碼，以及歧異如何解決。",
      "consensus_level": "CONSENSUS-4",
      "verification_criteria": "分析一節說明由幾位分析者編碼逐字稿，以及編碼歧異如何解決。"
    }
  ],
  "total_items": 2,
  "must_fix_count": 2,
  "editorial_decision": "Major Revision",
  "consensus_summary": "方法一節有兩項通報缺口。",
  "dissenting_opinions": []
}
```

## B. 第一輪編輯決議信（節錄）

**決議：Major Revision**

### Required Item Details

**R1：樣本描述不足**
- **Problem**：只給了樣本人數。
- **Source**：Peer Reviewer 2 (Domain) 弱點 1。
- **Acceptance criteria**: 具名說明取樣策略，並描述招募管道。

**R2：未描述編碼程序**
- **Problem**：分析一節寫出方法名稱，卻未說明分析者人數與歧異處理方式。
- **Source**：Peer Reviewer 1 (Methodology) 弱點 2。
- **Acceptance criteria**: 分析一節說明由幾位分析者編碼逐字稿，以及編碼歧異如何解決。

## C. 第一輪審查發現（節錄）

**Peer Reviewer 2 (Domain) — 弱點 1** `severity: major` `confidence: 4 — 質性取樣通報`
> 第 3.1 節說訪談了 26 位職員，卻沒說他們是怎麼被選出來的，也沒說是怎麼聯繫上的。

**Peer Reviewer 1 (Methodology) — 弱點 2** `severity: major` `confidence: 4 — 質性編碼程序通報`
> 第 3.4 節說逐字稿以主題分析處理。那是一個人做還是四個人做、讀法分歧時怎麼辦，正是讀者
> 判斷編碼品質所需要的部分。

## D. 第一輪審查人設定卡（節錄）

| 欄位 | 值 |
|------|-----|
| Role | EIC |
| Focus | 編輯整合 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 1 (Methodology) |
| Focus | 質性研究設計與分析程序 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 2 (Domain) |
| Focus | 高等教育人力研究 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 3 (Cross-disciplinary/Practical) |
| Focus | 機構相關性 |

## E. 原始（修訂前）稿件節錄

> **2.2 研究倫理。** 本研究經 Northfield 大學研究倫理委員會核准（計畫編號 2018-062），
> 核准日期為 2018 年 5 月 11 日。參與者於訪談前至少七天收到書面說明，並於訪談開始時簽署
> 書面同意；兩份文件皆載明退出權利。
>
> **3.1 設計與樣本。** 訪談 26 位行政職員。資料蒐集期間為 2018 年 9 月至 2019 年 6 月。
>
> **3.4 分析。** 逐字稿以主題分析處理。
>
> **4. 研究發現。** 自逐字稿發展出三個主題：工作量位移、界線侵蝕、非正式專業。

## F. 修訂後稿件節錄

> **2.2 研究倫理。** 本研究經 Northfield 大學研究倫理委員會核准（計畫編號 2018-062），
> 核准日期為 2018 年 5 月 11 日。參與者於訪談前至少七天收到書面說明，並於訪談開始時簽署
> 書面同意；兩份文件皆載明退出權利。
>
> **3.1 設計與樣本。** 訪談 26 位行政職員，以跨四個職務族群與三個校區的最大變異立意取樣
> 選出。參與者透過各校區教職員發展辦公室發出的邀請招募，另發兩次提醒。資料蒐集期間為
> 2018 年 9 月至 2019 年 6 月。
>
> **3.4 分析。** 逐字稿以主題分析處理。兩位分析者各自獨立編碼全部 26 份逐字稿；歧異透過
> 討論解決，其中四件討論未能解決者由第三位團隊成員裁決。
>
> **4. 研究發現。** 自逐字稿發展出三個主題：工作量位移、界線侵蝕、非正式專業。

## G. 修訂 patch 與 apply report

**Patch（節錄）**

```diff
--- a/manuscript.md
+++ b/manuscript.md
@@ 3.1 設計與樣本 @@
-訪談 26 位行政職員。資料蒐集期間為 2018 年 9 月至 2019 年 6 月。
+訪談 26 位行政職員，以跨四個職務族群與三個校區的最大變異立意取樣
+選出。參與者透過各校區教職員發展辦公室發出的邀請招募，另發兩次提醒。資料蒐集期間為
+2018 年 9 月至 2019 年 6 月。
@@ 3.4 分析 @@
 逐字稿以主題分析處理。
+兩位分析者各自獨立編碼全部 26 份逐字稿；歧異透過
+討論解決，其中四件討論未能解決者由第三位團隊成員裁決。
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

## H. 作者回覆信

感謝兩項意見，我們均已處理。

**R1（REV-001）。** 第 3.1 節現已具名說明取樣策略（跨四個職務族群與三個校區的最大變異
立意取樣），並描述招募管道（由各校區教職員發展辦公室發出邀請，另發兩次提醒）。

**R2（REV-002）。** 第 3.4 節現已說明兩位分析者各自獨立編碼全部 26 份逐字稿、歧異透過
討論解決，以及四件討論未決者由第三位團隊成員裁決。
