# 再審資料包 — 第二輪（情境 P-1，zh-TW）

本檔全部為合成素材：虛構作者、虛構機構、`10.5555/…` 保留前綴 DOI。內容不取自任何
真實稿件或真實審查意見。

**由 arm 提供的段落**：本資料包不含 **H（作者回覆信）**，該段由 arm 檔提供。
A 到 G 各段在本情境所有 arm 之間完全相同。

---

## A. 第一輪修訂路線圖（Schema 7，機器格式）

```json
{
  "items": [
    {
      "id": "REV-001",
      "description": "後測分數的組間差異被以因果方式詮釋，但受試分派到回饋組是由授課教師自行選擇而非隨機分派。請補上處理選擇效應的分析，或將主要發現全面改寫為關聯性陳述。",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Major",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "quote", "value": "採用此工具使後測表現提高 6.4 分"},
      "confidence": 4,
      "competence_basis": "準實驗設計與選擇偏誤",
      "target_section": "4.1 主要結果；5.1 討論",
      "suggested_action": "補上處理選擇效應的估計（例如以預先登錄共變項做傾向分數加權），或下修因果語言。",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "或者報告一個有具名方法的選擇效應校正估計，或者將主要效果的每一處因果表述改為關聯性語言。"
    },
    {
      "id": "REV-002",
      "description": "流失率僅以單一整體百分比呈現，未處理組間差異流失，且分析樣本從未與招募樣本核對。",
      "reviewer": "Peer Reviewer 2 (Domain)",
      "type": "Minor",
      "priority": "should_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "3.3 研究參與者"},
      "confidence": 4,
      "competence_basis": "課程層級研究的縱貫流失通報",
      "target_section": "3.3 研究參與者",
      "suggested_action": "分組報告流失率，並核對招募人數到分析人數的落差。",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "流失率分別針對每一組報告，且說明招募樣本到分析樣本的核對。"
    }
  ],
  "total_items": 2,
  "must_fix_count": 1,
  "editorial_decision": "Major Revision",
  "consensus_summary": "四席中有三席各自獨立指出對非隨機分派對比做因果解讀的問題。流失率通報由兩席提出。",
  "dissenting_opinions": []
}
```

## B. 第一輪編輯決議信（節錄）

**決議：Major Revision**

### Required Item Details

**R1：對非隨機分派對比使用因果語言**
- **Problem**：6.4 分的後測差異被歸因於工具，但授課教師是自行選擇組別。
- **Source**：Peer Reviewer 1 (Methodology) 弱點 1；Peer Reviewer 3 佐證。
- **Acceptance criteria**: 或者報告一個有具名方法的選擇效應校正估計，或者將主要效果的每一處因果表述改為關聯性語言。

### Suggested Improvements

| # | 項目 | 優先序 | 審查人 |
|---|------|--------|--------|
| S1 | 分組報告流失率並核對招募到分析人數（REV-002） | P2 | Peer Reviewer 2 |

## C. 第一輪審查發現（節錄）

**Peer Reviewer 1 (Methodology) — 弱點 1** `severity: major` `confidence: 4 — 準實驗設計與選擇偏誤`
> 授課教師自行選入回饋組。第 4.1 節接著寫「採用此工具使後測表現提高 6.4 分」。這個設計沒有
> 任何地方支持這個動詞。要嘛把選擇過程模型化，要嘛這句話就是錯的。

**Peer Reviewer 2 (Domain) — 弱點 2** `severity: major` `confidence: 4 — 課程層級研究的縱貫流失通報`
> 第 3.3 節只給了全研究一個流失率數字（14%）。在兩組設計裡，值得看的是兩組流失是否不同；
> 而且招募的 412 人從來沒有跟分析的 340 人對得起來。

## D. 第一輪審查人設定卡（節錄）

| 欄位 | 值 |
|------|-----|
| Role | EIC |
| Focus | 編輯整合 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 1 (Methodology) |
| Focus | 研究設計、識別、推論 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 2 (Domain) |
| Focus | 高等教育測量與通報實務 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 3 (Cross-disciplinary/Practical) |
| Focus | 教學實務可遷移性 |

## E. 原始（修訂前）稿件節錄

> **3.3 研究參與者。** 共 412 名學生於 11 個課程班別中登記修課。整體流失率為 14%。
> 分析樣本為 340 人。
>
> **4.1 主要結果。** 自動回饋組的學生後測分數高出 6.4 分（SE = 1.9，p = .001）。
> 採用此工具使後測表現提高 6.4 分，相對於未採用的班別而言。
>
> **5.1 討論。** 此工具改善學習成效，幅度相當於半個等第。考慮導入的機構可預期得到
> 類似的效果。

## F. 修訂後稿件節錄

> **3.3 研究參與者。** 共 412 名學生於 11 個課程班別中登記修課。回饋組流失率為 11%，
> 對照組為 17%。分析樣本為 340 人。
>
> **4.1 主要結果。** 自動回饋組的學生後測分數高出 6.4 分（SE = 1.9，p = .001）。
> 由於授課教師自行選擇組別，我們另以預先登錄共變項（先前 GPA、課程層級、班級人數）
> 進行反機率加權估計，加權後差異為 5.1 分（SE = 2.2，p = .021）。因此我們報告的是
> 採用與後測表現之間的關聯，而非該工具的因果效果。
>
> **5.1 討論。** 採用與較高的後測表現有關聯，幅度相當於半個等第。此關聯反映的是工具、
> 是選擇採用的教師，或兩者兼有，本設計無法識別。

## G. 修訂 patch 與 apply report

**Patch（節錄）**

```diff
--- a/manuscript.md
+++ b/manuscript.md
@@ 3.3 研究參與者 @@
-共 412 名學生於 11 個課程班別中登記修課。整體流失率為 14%。
+共 412 名學生於 11 個課程班別中登記修課。回饋組流失率為 11%，
+對照組為 17%。
 分析樣本為 340 人。
@@ 4.1 主要結果 @@
-採用此工具使後測表現提高 6.4 分，相對於未採用的班別而言。
+由於授課教師自行選擇組別，我們另以預先登錄共變項（先前 GPA、課程層級、班級人數）
+進行反機率加權估計，加權後差異為 5.1 分（SE = 2.2，p = .021）。因此我們報告的是
+採用與後測表現之間的關聯，而非該工具的因果效果。
@@ 5.1 討論 @@
-此工具改善學習成效，幅度相當於半個等第。考慮導入的機構可預期得到
-類似的效果。
+採用與較高的後測表現有關聯，幅度相當於半個等第。此關聯反映的是工具、
+是選擇採用的教師，或兩者兼有，本設計無法識別。
```

**Apply report**

```json
{
  "report_format_version": "1.2",
  "base_draft_hash": "<<BASE_DRAFT_HASH>>",
  "output_draft_hash": "<<OUTPUT_DRAFT_HASH>>",
  "patch_digest": "<<PATCH_DIGEST>>",
  "hunks_applied": 3,
  "hunks_rejected": 0
}
```

## I. Input manifest 存在性宣告（§11）

派工層在 Phase 1 之前發射 §11 input manifest。本情境宣告九項 artifact 全部 **present**，
`cross_model_active: false`，`round_id: "p1-r2"`。

| Artifact | 存在性 | 來源 |
|----------|--------|------|
| `original_manuscript` | present | 資料包 §E |
| `revised_manuscript` | present | 資料包 §F |
| `revision_roadmap` | present | 資料包 §A |
| `editorial_decision_letter` | present | 資料包 §B |
| `response_to_reviewers` | present | **arm §H** |
| `revision_patches` | present，1 筆 | 資料包 §G |
| `apply_reports` | present，1 筆 | 資料包 §G |
| `round1_findings` | present | 資料包 §C |
| `round1_config_cards` | present | 資料包 §D |

**雜湊蓋章。** manifest 的 `sha256` 由派工層在派工當下從實體化的 artifact 檔案計算。
§G 內的 `<<BASE_DRAFT_HASH>>`、`<<OUTPUT_DRAFT_HASH>>`、`<<PATCH_DIGEST>>` 佔位符在同一步
被替換為對應的計算值，如此 §11 apply-chain witness 在正確實體化的執行上會得到 `pass`，
而不是對著一個寫死的常數失敗。若 fixture 直接寫死十六進位值，每個 arm 都會在 G0 中止，
什麼都量不到。
