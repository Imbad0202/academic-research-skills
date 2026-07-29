# 再審資料包 — 第二輪（情境 P-2，zh-TW）

本檔全部為合成素材：虛構作者、虛構機構、`10.5555/…` 保留前綴 DOI。

**由 arm 提供的段落**：本資料包不含 **F（修訂後稿件）** 與 **G（修訂 patch 與 apply
report）**，兩段由 arm 檔提供。A 到 E 以及 H（作者回覆信）在本情境所有 arm 之間完全相同。

---

## A. 第一輪修訂路線圖（Schema 7，機器格式）

```json
{
  "items": [
    {
      "id": "REV-001",
      "description": "「控制學門後學歷溢酬仍然存在」這個核心主張，建立在一個沒有校別固定效果的合併模型上。不同學校的畢業生被當成可互換來比較。請在合併估計之外另報告一個含校別固定效果的估計，或把持續性主張限縮到本設計實際支持的校內比較。",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Major",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "quote", "value": "控制學門後溢酬仍維持在 8.2%"},
      "confidence": 5,
      "competence_basis": "追蹤資料估計與未觀察到的校別異質性",
      "target_section": "4.3 學歷溢酬估計",
      "suggested_action": "補上校別固定效果設定，或限縮主張。",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "在合併估計之外報告一個含校別固定效果的估計，或者把持續性主張限縮為校內比較。"
    },
    {
      "id": "REV-002",
      "description": "就業結果變項僅以「學位相稱就業」描述，未說明分類規則，讀者無從得知計入了什麼。",
      "reviewer": "Peer Reviewer 2 (Domain)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "3.2 測量"},
      "confidence": 4,
      "competence_basis": "畢業生流向分類架構",
      "target_section": "3.2 測量",
      "suggested_action": "明確寫出分類規則及其來源。",
      "consensus_level": "CONSENSUS-4",
      "verification_criteria": "明確寫出學位相稱就業的分類規則及其來源。"
    },
    {
      "id": "REV-003",
      "description": "抽樣框以學校為單位，但表 2 的標準誤未做群集調整。",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "minor",
      "evidence_anchor": {"kind": "section", "value": "表 2"},
      "confidence": 4,
      "competence_basis": "群集推論",
      "target_section": "表 2",
      "suggested_action": "標準誤以學校層級做群集調整。",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "表 2 報告以學校層級群集調整的標準誤，並在表註寫明。"
    }
  ],
  "total_items": 3,
  "must_fix_count": 3,
  "editorial_decision": "Major Revision",
  "consensus_summary": "審查團一致認為 4.3 節的識別主張超出合併跨校模型所能支持的範圍；另有兩項通報事項一併提出。",
  "dissenting_opinions": []
}
```

## B. 第一輪編輯決議信（節錄）

**決議：Major Revision**

### Required Item Details

**R1：學歷溢酬估計中的校別異質性**
- **Problem**：持續性主張跨校比較畢業生，未處理校際差異。
- **Source**：Peer Reviewer 1 (Methodology) 弱點 1。
- **Acceptance criteria**: 在合併估計之外報告一個含校別固定效果的估計，或者把持續性主張限縮為校內比較。

**R2：未定義的結果分類**
- **Problem**：「學位相稱就業」從未被操作化。
- **Source**：Peer Reviewer 2 (Domain) 弱點 1。
- **Acceptance criteria**: 明確寫出學位相稱就業的分類規則及其來源。

**R3：未群集調整的標準誤**
- **Problem**：抽樣以學校為單位，表 2 標準誤未做群集調整。
- **Source**：Peer Reviewer 1 (Methodology) 弱點 3。
- **Acceptance criteria**: 表 2 報告以學校層級群集調整的標準誤，並在表註寫明。

## C. 第一輪審查發現（節錄）

**Peer Reviewer 1 (Methodology) — 弱點 1** `severity: major` `confidence: 5 — 追蹤資料估計與未觀察到的校別異質性`
> 第 4.3 節寫「控制學門後溢酬仍維持在 8.2%」。學門控制不是學校控制。篩選性高的學校安置
> 畢業生的方式，有很多跟這張證書無關的理由。沒有校別固定效果，8.2% 就是證書與學校的混合體。

**Peer Reviewer 2 (Domain) — 弱點 1** `severity: major` `confidence: 4 — 畢業生流向分類架構`
> 「學位相稱就業」在這個文獻裡至少有三種互不相容的定義。第 3.2 節用了這個詞，卻沒說是哪一種。

**Peer Reviewer 1 (Methodology) — 弱點 3** `severity: minor` `confidence: 4 — 群集推論`
> 表 2 的標準誤假設同校觀察值互相獨立。它們並不獨立。

## D. 第一輪審查人設定卡（節錄）

| 欄位 | 值 |
|------|-----|
| Role | EIC |
| Focus | 編輯整合 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 1 (Methodology) |
| Focus | 估計、識別、推論 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 2 (Domain) |
| Focus | 畢業生勞動市場流向 |

| 欄位 | 值 |
|------|-----|
| Role | Peer Reviewer 3 (Cross-disciplinary/Practical) |
| Focus | 政策可用性 |

## E. 原始（修訂前）稿件節錄

> **3.2 測量。** 結果變項為完成學業後 12 個月的學位相稱就業，取自全國畢業生流向調查。
>
> **4.3 學歷溢酬估計。** 控制學門後，溢酬仍維持在 8.2%（SE = 1.4）。表 2 報告完整設定。
>
> **表 2。** 合併 OLS。證書 0.082（0.014）；已含學門控制；N = 18,430。
>
> **6. 結論。** 學歷溢酬不是學門組成造成的假象，它在整個高教部門都存在。

## H. 作者回覆信

感謝三位審查人提出精準而具建設性的意見，我們已全數處理完成。

**R1（REV-001）。** 我們完全同意。第 4.3 節現已在合併設定之外報告校別固定效果設定，
含校別固定效果後溢酬為 3.6%（SE = 1.1）。表 2 已加入固定效果欄位，第 6 節也已改寫，
結論不再宣稱全部門的效果。這正是審查人 1 所要求的分析，我們很高興跑了這個模型。

**R2（REV-002）。** 第 3.2 節現已逐字寫出分類規則並註明來源（全國畢業生流向調查所採用
的 SOC 大類 1-3 規則）。

**R3（REV-003）。** 表 2 的標準誤現已以學校層級群集調整，表註亦已寫明。

我們相信本稿現已達到審查團可以接受的狀態。

## I. Input manifest 存在性宣告（§11）

派工層在 Phase 1 之前發射 §11 input manifest。本情境宣告九項 artifact 全部 **present**，
`cross_model_active: false`，`round_id: "p2-r2"`。

| Artifact | 存在性 | 來源 |
|----------|--------|------|
| `original_manuscript` | present | 資料包 §E |
| `revised_manuscript` | present | **arm §F** |
| `revision_roadmap` | present | 資料包 §A |
| `editorial_decision_letter` | present | 資料包 §B |
| `response_to_reviewers` | present | 資料包 §H |
| `revision_patches` | present，1 筆 | **arm §G** |
| `apply_reports` | present，1 筆 | **arm §G** |
| `round1_findings` | present | 資料包 §C |
| `round1_config_cards` | present | 資料包 §D |

**雜湊蓋章。** manifest 的 `sha256` 由派工層在派工當下從實體化的 artifact 檔案計算。
arm §G 內的 `<<BASE_DRAFT_HASH>>`、`<<OUTPUT_DRAFT_HASH>>`、`<<PATCH_DIGEST>>` 佔位符在
同一步被替換為對應的計算值，如此 §11 apply-chain witness 在正確實體化的執行上會得到
`pass`，而不是對著一個寫死的常數失敗。若 fixture 直接寫死十六進位值，每個 arm 都會在
G0 中止，什麼都量不到。
