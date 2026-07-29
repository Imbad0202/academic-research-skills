# 再審資料包 — 第二輪（情境 P-6，zh-TW）

本檔全部為合成素材：虛構作者、虛構機構、虛構倫理委員會與計畫編號、`10.5555/…` 保留前綴
DOI。不描寫任何真實研究、真實審查通過紀錄或真實受試者。

**由 arm 提供的段落**：本資料包只提供 **I** 一節。**A 到 H**（第一輪 artifacts、兩份
稿件、patch、作者回覆信）全部由 arm 檔提供。

P-6 是本集合中唯一各臂差異位於稿件上游的情境，而且它必須如此。受控因子是修訂後標準的
escalation 類別，§3.2 把該標準的產生點放在 Phase 1，而 §3.1 使 Phase 1 對修訂盲。
Phase 1 記錄因此只能自第一輪 artifacts 推導，所以兩個要提出不同類別標準的 arm，本來就
必須攜帶不同的第一輪 artifacts。在這裡共用 packet 等於要求 Phase 1 依它看不到的輸入做
條件判斷。

---

## I. Input manifest 存在性宣告（§11）

各 arm 皆宣告九項 artifact 全部 **present**，`cross_model_active: false`，
`round_id: "p6-r2"`。

| Artifact | 存在性 | 來源 |
|----------|--------|------|
| `original_manuscript` | present | arm §E |
| `revised_manuscript` | present | arm §F |
| `revision_roadmap` | present | arm §A |
| `editorial_decision_letter` | present | arm §B |
| `response_to_reviewers` | present | arm §H |
| `revision_patches` | present，1 筆 | arm §G |
| `apply_reports` | present，1 筆 | arm §G |
| `round1_findings` | present | arm §C |
| `round1_config_cards` | present | arm §D |

**雜湊蓋章。** 同其他情境，manifest 的 `sha256` 與 §G 內的 `<<…>>` 佔位符由派工層在
派工當下計算並替換。
