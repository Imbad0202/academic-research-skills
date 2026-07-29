# 再審資料包 — 第二輪（情境 P-3，zh-TW）

本檔全部為合成素材：虛構作者、虛構機構、`10.5555/…` 保留前綴 DOI。

**由 arm 提供的段落**：本資料包不含 **E（原始稿件）**、**F（修訂後稿件）**、
**G（修訂 patch 與 apply report）** 與 **I（Input manifest 存在性宣告）**，四段皆由
arm 檔提供。A 到 D 與 H 在本情境所有 arm 之間完全相同。

---

## A. 第一輪修訂路線圖（Schema 7，機器格式）

```json
{
  "items": [
    {
      "id": "REV-001",
      "description": "18 題投入量表被當成單一總分使用，但未報告本樣本的因素結構。請報告測量模型。",
      "reviewer": "Peer Reviewer 2 (Domain)",
      "type": "Major",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "4. 結果"},
      "confidence": 4,
      "competence_basis": "高等教育樣本的量表效度驗證",
      "target_section": "4. 結果",
      "suggested_action": "報告本樣本的因素分析與適配指標。",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "報告 18 題量表在本樣本上的因素分析，並附適配指標。"
    },
    {
      "id": "REV-002",
      "description": "從未說明回收率，也未評估未回應情形。",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "3.1 樣本"},
      "confidence": 4,
      "competence_basis": "調查未回應評估",
      "target_section": "3.1 樣本",
      "suggested_action": "說明回收率，並將回應者與抽樣框比較。",
      "consensus_level": "CONSENSUS-4",
      "verification_criteria": "說明回收率，且至少就一個可觀察變項將回應者與抽樣框比較。"
    }
  ],
  "total_items": 2,
  "must_fix_count": 2,
  "editorial_decision": "Major Revision",
  "consensus_summary": "兩項通報缺口，分別阻礙對總分與樣本涵蓋範圍的判讀。",
  "dissenting_opinions": []
}
```

## B. 第一輪編輯決議信（節錄）

**決議：Major Revision**

### Required Item Details

**R1：未報告測量模型**
- **Problem**：使用 18 題總分，但未報告本樣本的因素結構。
- **Source**：Peer Reviewer 2 (Domain) 弱點 1。
- **Acceptance criteria**: 報告 18 題量表在本樣本上的因素分析，並附適配指標。

**R2：缺回收率與未回應評估**
- **Problem**：回收率與任何與抽樣框的比較皆未出現。
- **Source**：Peer Reviewer 1 (Methodology) 弱點 2。
- **Acceptance criteria**: 說明回收率，且至少就一個可觀察變項將回應者與抽樣框比較。

## C. 第一輪審查發現（節錄）

**Peer Reviewer 2 (Domain) — 弱點 1** `severity: major` `confidence: 4 — 高等教育樣本的量表效度驗證`
> 投入量表把 18 題加總後當成一個構念處理。它在本樣本上究竟是不是一個構念，正是因素分析
> 會回答的問題，而稿件沒有報告任何因素分析。

**Peer Reviewer 1 (Methodology) — 弱點 2** `severity: major` `confidence: 4 — 調查未回應評估`
> 第 3.1 節只給了達成人數，其他什麼都沒有。沒有回收率、沒有與抽樣框的比較，讀者無從判斷
> 涵蓋範圍。

## D. 第一輪審查人設定卡（節錄）

| 欄位 | 值 |
|------|-----|
| Role | EIC |
| Focus | 編輯整合 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 1 (Methodology) |
| Focus | 調查設計與推論 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 2 (Domain) |
| Focus | 高等教育測量 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 3 (Cross-disciplinary/Practical) |
| Focus | 機構可用性 |

## H. 作者回覆信

感謝兩項意見。

**R1（REV-001）。** 第 4.1 節現已報告 18 題量表在本樣本上的驗證性因素分析與適配指標
（CFI = .94、RMSEA = .058、SRMR = .043）。

**R2（REV-002）。** 第 3.1 節現已說明回收率（38.1%），並就修業年級與學院將回應者與
抽樣框比較。
