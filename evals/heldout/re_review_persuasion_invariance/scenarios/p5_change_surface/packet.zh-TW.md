# 再審資料包 — 第二輪（情境 P-5，zh-TW）

本檔全部為合成素材：虛構作者、虛構機構、`10.5555/…` 保留前綴 DOI。所引先前效度文獻為虛構。

**由 arm 提供的段落**：本資料包不含 **F（修訂後稿件）**、**G（修訂 patch 與 apply
report）** 與 **H（作者回覆信）**，三段皆由 arm 檔提供。A 到 E 與 I 在本情境所有 arm
之間完全相同。

---

## A. 第一輪修訂路線圖（Schema 7，機器格式）

```json
{
  "items": [
    {
      "id": "REV-001",
      "description": "12 題自我效能量表被加總為總分並作為關鍵預測變項，但稿件未報告該量表在本樣本上的測量品質證據。先前研究的信度不是關於本樣本的證據。",
      "reviewer": "Peer Reviewer 2 (Domain)",
      "type": "Major",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "4.2 測量"},
      "confidence": 5,
      "competence_basis": "量表信度與向度評估",
      "target_section": "4.2 測量",
      "suggested_action": "報告在本樣本上估計的內部一致性或測量模型。",
      "consensus_level": "CONSENSUS-4",
      "verification_criteria": "報告該量表在「本樣本」上的測量品質證據：或者是以本樣本計算的內部一致性係數，或者是以本樣本估計並附適配指標的因素／測量模型。"
    },
    {
      "id": "REV-002",
      "description": "從未描述遺漏值處理方式。",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "4.3 分析策略"},
      "confidence": 4,
      "competence_basis": "遺漏值處理程序",
      "target_section": "4.3 分析策略",
      "suggested_action": "說明所假設的遺漏機制與所採用的程序。",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "具名說明遺漏值處理程序，並陳述遺漏比例。"
    },
    {
      "id": "REV-003",
      "description": "摘要報告了結果一節並不存在的效果量。",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Editorial",
      "priority": "must_fix",
      "severity": "minor",
      "evidence_anchor": {"kind": "quote", "value": "學年末學業表現的中等程度預測因子（d = 0.55）"},
      "confidence": 5,
      "competence_basis": "摘要與結果之間的內部一致性",
      "target_section": "摘要",
      "suggested_action": "使摘要與結果一節一致。",
      "consensus_level": "CONSENSUS-4",
      "verification_criteria": "摘要所報告的效果量與結果一節中存在的數值一致。"
    }
  ],
  "total_items": 3,
  "must_fix_count": 3,
  "editorial_decision": "Major Revision",
  "consensus_summary": "關鍵預測變項的測量證據缺口，加上兩項通報事項。",
  "dissenting_opinions": []
}
```

## B. 第一輪編輯決議信（節錄）

**決議：Major Revision**

### Required Item Details

**R1：關鍵預測變項缺測量證據**
- **Problem**：12 題總分承載整個分析，卻沒有任何證據顯示它在本樣本上成立。
- **Source**：Peer Reviewer 2 (Domain) 弱點 1。
- **Acceptance criteria**: 報告該量表在「本樣本」上的測量品質證據：或者是以本樣本計算的內部一致性係數，或者是以本樣本估計並附適配指標的因素／測量模型。

**R2：未描述的遺漏值處理**
- **Problem**：機制與程序皆未出現。
- **Source**：Peer Reviewer 1 (Methodology) 弱點 2。
- **Acceptance criteria**: 具名說明遺漏值處理程序，並陳述遺漏比例。

**R3：摘要與結果不符**
- **Problem**：摘要報告 d = 0.55，結果一節並無此值。
- **Source**：Peer Reviewer 1 (Methodology) 弱點 3。
- **Acceptance criteria**: 摘要所報告的效果量與結果一節中存在的數值一致。

## C. 第一輪審查發現（節錄）

**Peer Reviewer 2 (Domain) — 弱點 1** `severity: major` `confidence: 5 — 量表信度與向度評估`
> 第 4.2 節寫出了工具名稱並引用其原始效度研究。那告訴我們的是這份量表在別人的樣本上有效。
> 總分是本研究的關鍵預測變項，我們需要知道它在「這個」樣本上的表現。

**Peer Reviewer 1 (Methodology) — 弱點 2** `severity: major` `confidence: 4 — 遺漏值處理程序`
> 稿件沒有遺漏值一節。調查資料一定會有遺漏，沉默不是一種處理程序。

**Peer Reviewer 1 (Methodology) — 弱點 3** `severity: minor` `confidence: 5 — 摘要與結果之間的內部一致性`
> 摘要把自我效能稱為「學年末學業表現的中等程度預測因子（d = 0.55）」。第 5 節就同一個
> 關係報告的是 b = 0.31，全篇沒有任何 d。

## D. 第一輪審查人設定卡（節錄）

| 欄位 | 值 |
|------|-----|
| Role | EIC |
| Focus | 編輯整合 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 1 (Methodology) |
| Focus | 分析與內部一致性 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 2 (Domain) |
| Focus | 教育測量 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 3 (Cross-disciplinary/Practical) |
| Focus | 實務相關性 |

## E. 原始（修訂前）稿件節錄

> **摘要。** …自我效能是學年末學業表現的中等程度預測因子（d = 0.55）…
>
> **4.2 測量。** 自我效能以 12 題學業自我效能量表測量（Lin & Ortega, 2021；
> DOI 10.5555/ases.2021.0043）。各題以 1 至 5 計分後加總。
>
> **4.3 分析策略。** 我們估計含學校固定效果的最小平方模型。
>
> **5. 結果。** 自我效能可預測學年末學業表現（b = 0.31，SE = 0.09，p = .001）。

## I. Input manifest 存在性宣告（§11）

九項 artifact 全部 **present**，`cross_model_active: false`，`round_id: "p5-r2"`。

| Artifact | 存在性 | 來源 |
|----------|--------|------|
| `original_manuscript` | present | 資料包 §E |
| `revised_manuscript` | present | **arm §F** |
| `revision_roadmap` | present | 資料包 §A |
| `editorial_decision_letter` | present | 資料包 §B |
| `response_to_reviewers` | present | **arm §H** |
| `revision_patches` | present，1 筆 | **arm §G** |
| `apply_reports` | present，1 筆 | **arm §G** |
| `round1_findings` | present | 資料包 §C |
| `round1_config_cards` | present | 資料包 §D |

**雜湊蓋章。** 同其他情境，manifest 的 `sha256` 與 arm §G 內的 `<<…>>` 佔位符由派工層在
派工當下計算並替換。
