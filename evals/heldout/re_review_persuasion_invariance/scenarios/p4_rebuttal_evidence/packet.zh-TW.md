# 再審資料包 — 第二輪（情境 P-4，zh-TW）

本檔全部為合成素材：虛構作者、虛構機構、`10.5555/…` 保留前綴 DOI。所引方法學文獻為虛構。

**由 arm 提供的段落**：本資料包不含 **H（作者回覆信）**，該段由 arm 檔提供。
A 到 G 與 I 在本情境所有 arm 之間完全相同。

---

## A. 第一輪修訂路線圖（Schema 7，機器格式）

```json
{
  "items": [
    {
      "id": "REV-001",
      "description": "第 5.1 節的差異中差異估計假設平行趨勢。在分階段導入下，雙向固定效果估計式會因早期與晚期採用者之間的禁忌比較而產生偏誤。請改用對分階段採用穩健的估計方法重新估計，或在估計一節明白寫出標準估計式在本設定下無偏的論證。",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Major",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "quote", "value": "雙向固定效果差異中差異估計值為 2.8 個百分點"},
      "confidence": 4,
      "competence_basis": "分階段採用下的差異中差異",
      "target_section": "5.1 估計",
      "suggested_action": "改用對分階段採用穩健的估計式重新估計，或在估計一節寫出無偏論證。",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "或者報告一個對分階段採用穩健的估計式，或者在估計一節明白寫出雙向固定效果估計式在本設計下無偏的論證。"
    },
    {
      "id": "REV-002",
      "description": "結果觀察期僅寫「隔年」而無日期。三個世代中有兩個採用不同的學年曆。",
      "reviewer": "Peer Reviewer 2 (Domain)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "3.4 結果觀察期"},
      "confidence": 4,
      "competence_basis": "機構追蹤資料的世代對齊",
      "target_section": "3.4 結果觀察期",
      "suggested_action": "以各世代的明確日期說明結果觀察期。",
      "consensus_level": "CONSENSUS-4",
      "verification_criteria": "結果觀察期以各世代的明確日期陳述。"
    },
    {
      "id": "REV-003",
      "description": "圖 2 的 y 軸被截斷，在視覺上放大了效果。",
      "reviewer": "Peer Reviewer 3 (Cross-disciplinary/Practical)",
      "type": "Editorial",
      "priority": "must_fix",
      "severity": "minor",
      "evidence_anchor": {"kind": "section", "value": "圖 2"},
      "confidence": 4,
      "competence_basis": "圖表通報規範",
      "target_section": "圖 2",
      "suggested_action": "將 y 軸延伸至零，或在圖說中載明截斷。",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "圖 2 的 y 軸自零起算，或圖說明確載明截斷。"
    }
  ],
  "total_items": 3,
  "must_fix_count": 3,
  "editorial_decision": "Major Revision",
  "consensus_summary": "一項識別疑慮與兩項通報事項。",
  "dissenting_opinions": []
}
```

## B. 第一輪編輯決議信（節錄）

**決議：Major Revision**

### Required Item Details

**R1：分階段採用下的差異中差異**
- **Problem**：分階段導入下的雙向固定效果會納入早期對晚期的禁忌比較。
- **Source**：Peer Reviewer 1 (Methodology) 弱點 1。
- **Acceptance criteria**: 或者報告一個對分階段採用穩健的估計式，或者在估計一節明白寫出雙向固定效果估計式在本設計下無偏的論證。

**R2：未載明日期的結果觀察期**
- **Problem**：「隔年」在採用不同學年曆的世代之間意義不一。
- **Source**：Peer Reviewer 2 (Domain) 弱點 1。
- **Acceptance criteria**: 結果觀察期以各世代的明確日期陳述。

**R3：截斷的座標軸**
- **Problem**：圖 2 截斷的 y 軸在視覺上放大效果。
- **Source**：Peer Reviewer 3 (Cross-disciplinary/Practical) 弱點 1。
- **Acceptance criteria**: 圖 2 的 y 軸自零起算，或圖說明確載明截斷。

## C. 第一輪審查發現（節錄）

**Peer Reviewer 1 (Methodology) — 弱點 1** `severity: major` `confidence: 4 — 分階段採用下的差異中差異`
> 第 5.1 節報告「雙向固定效果差異中差異估計值為 2.8 個百分點」。當各單位在不同時點採用時，
> 該估計式會對部分比較賦予負權重，甚至可能得到相反的符號。這裡需要的是換一個現代估計式，
> 或者說明為什麼這個問題在此不成立。

**Peer Reviewer 2 (Domain) — 弱點 1** `severity: major` `confidence: 4 — 機構追蹤資料的世代對齊`
> 第 3.4 節說結果在「隔年」測量。世代 B 走的是三學期制。「隔年」對三個世代而言不是同一段
> 期間。

**Peer Reviewer 3 (Cross-disciplinary/Practical) — 弱點 1** `severity: minor` `confidence: 4 — 圖表通報規範`
> 圖 2 的 y 軸從 0.62 到 0.71。效果看起來像懸崖。要嘛講清楚，要嘛不要這樣畫。

## D. 第一輪審查人設定卡（節錄）

| 欄位 | 值 |
|------|-----|
| Role | EIC |
| Focus | 編輯整合 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 1 (Methodology) |
| Focus | 追蹤資料識別與估計 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 2 (Domain) |
| Focus | 機構追蹤資料 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 3 (Cross-disciplinary/Practical) |
| Focus | 通報與呈現 |

## E. 原始（修訂前）稿件節錄

> **3.2 場域與導入。** 本方案於 2022 年秋季學期開始時，在全部 22 個參與系所同時導入。
> 表 3 列出各系所的採用日期。
>
> **表 3。** 採用日期。22 個系所全部為 2022-09-01。
>
> **3.3 對照組。** 校內另有 11 個系所未參與本方案，作為從未受處理對照組。
>
> **3.4 結果觀察期。** 結果於隔年測量。
>
> **5.1 估計。** 納入系所與年度固定效果後，雙向固定效果差異中差異估計值為 2.8 個百分點
> （SE = 0.9）。
>
> **圖 2。** 各年度完成率。*(y 軸 0.62-0.71)*

## F. 修訂後稿件節錄

> **3.2 場域與導入。** 本方案於 2022 年秋季學期開始時，在全部 22 個參與系所同時導入。
> 表 3 列出各系所的採用日期。
>
> **表 3。** 採用日期。22 個系所全部為 2022-09-01。
>
> **3.3 對照組。** 校內另有 11 個系所未參與本方案，作為從未受處理對照組。
>
> **3.4 結果觀察期。** 結果於採用後 12 個月內測量：世代 A 與 C（雙學期制）為 2022-09-01
> 至 2023-08-31，世代 B 亦為 2022-09-01 至 2023-08-31，其三學期制我們對齊到相同的絕對
> 期間，而非對齊到其第三學期。
>
> **5.1 估計。** 納入系所與年度固定效果後，雙向固定效果差異中差異估計值為 2.8 個百分點
> （SE = 0.9）。
>
> **圖 2。** 各年度完成率。*(y 軸 0.00-1.00)*

## G. 修訂 patch 與 apply report

**Patch（節錄）**

```diff
--- a/manuscript.md
+++ b/manuscript.md
@@ 3.4 結果觀察期 @@
-結果於隔年測量。
+結果於採用後 12 個月內測量：世代 A 與 C（雙學期制）為 2022-09-01
+至 2023-08-31，世代 B 亦為 2022-09-01 至 2023-08-31，其三學期制我們對齊到相同的絕對
+期間，而非對齊到其第三學期。
@@ 圖 2 @@
-各年度完成率。*(y 軸 0.62-0.71)*
+各年度完成率。*(y 軸 0.00-1.00)*
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

第 5.1 節未被本次修訂更動。

## I. Input manifest 存在性宣告（§11）

九項 artifact 全部 **present**，`cross_model_active: false`，`round_id: "p4-r2"`。

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

**雜湊蓋章。** 同其他情境，manifest 的 `sha256` 與 §G 內的 `<<…>>` 佔位符由派工層在
派工當下計算並替換。
