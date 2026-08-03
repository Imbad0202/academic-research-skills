# Editorial Decision Package

## Sprint Contract Audit

dimension_verdicts: [D1=block, D2=warn, D3=block, D4=warn, D5=warn, D6=block]
fired_conditions: [F2, F3, F5]
da_critical_adjudications: []
editorial_decision=major_revision

## Part 1: Editorial Decision Letter

敬啟者：

感謝提交〈少子化情境下臺灣私立大學招生策略證據之可判定性：公開資料趨勢與最低公開證據稽核〉。本稿依《高等教育》區域專業期刊適配標準接受五席完整審查。

## Review Panel Provenance (#540)

All five reviewer personas ran on a single model family (openai-codex/gpt-5.6-sol). Persona diversity is not model diversity — blind spots may be correlated across reviewers (Ren et al. 2026, arXiv:2607.13104 §5.2).

五席在同一Pi工作階段依序執行，沒有獨立context windows，也沒有真正認知paper blindness。每席Phase 1與Phase 2分檔並通過機械檢查，報告彼此未交叉引用；這只能維持程序分離，不能消除單一模型與共享對話脈絡造成的相關錯誤。

### Decision: Major Revision

### Reviewer Summary

| Reviewer | Role | Recommendation or signal | Confidence |
|---|---|---|---:|
| Journal-Fit | 臺灣高等教育期刊定位與結構 | Major Revision | 4/5 |
| R1 | 行政資料、重複橫斷面、次級證據方法 | Major Revision | 4/5 |
| R2 | 臺灣私立高教與TVET治理 | Minor Revision | 4/5 |
| R3 | 教育管理、決策科學與學生風險 | Minor Revision | 4/5 |
| DA | 負面證據與論證壓力測試 | D3 repairable block; no CRITICAL | 5/5 |

### Points of Agreement

- **[CONSENSUS-3, positive]** EIC、R1與R2均肯定稿件維持私立一般大學／TVET分層，並把官方趨勢、校方可見性及Lin與Yang的關聯限制在各自證據層級；R3未反對但未直接審查此領域／方法主張。
- **Corroborated finding** R1與DA均指出，有限取得語料的邊界需要更清楚地與「臺灣公開證據總體不足」分開；R2另從臺灣領域定位不足提供相鄰支持。
- **Corroborated finding** R1與DA均指出，表2由證據層級轉為延後／停止狀態的規則尚未操作化；EIC從貢獻可辨識性提出相鄰問題。
- 四位非DA審查者都確認稿件具有真實優點，但各自發現不同的可修復缺口。沒有任何審查者主張稿件存在不可修復的資料錯誤或因果誇大。

### Points of Disagreement

沒有形成同一原子主張上「存在／處置／嚴重度」相互衝突的SPLIT。推薦差異來自角色評估不同維度：R2與R3認為其領域與實務缺口可用局部補充處理；EIC、R1與DA則分別在D6、D1與D3識別可修復block。依Sprint Contract，這些owner-seat block觸發F2，不能用其他維度的Minor建議平均或軟化。

### Decision Rationale

稿件最穩固的成果是109至113學年度兩類私校雙重指標的可重現重算，以及對分母、校型與關聯／因果邊界的持續節制。這些成果讓論文不至於因資料或推論錯誤而被否決。然而，三個核心維度尚未達區域專業期刊門檻。第一，R1指出正文無法重建316個候選群組到9篇全文的納入排除與篩選規則；這直接限制「公開證據可支持到何種程度」的可評估性。第二，DA指出本次可取得語料的不足仍可能在論證上承擔過廣的管理結論，且表2幾乎一律延後的輸出欠缺可反駁規則。第三，EIC指出最低公開證據稽核尚未與既有做法區別或驗證，因此期刊貢獻仍像一套審慎清單。這些問題均可用既有稽核紀錄、重新定位與程序操作化修復，不需要捏造新效果或進行人體研究；故決定為Major Revision而非Reject。機械判定由F2優先驅動，F3與F5亦觸發。

### Top Blocking Issues

| Rank | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---:|---|---|---|---|
| 1 | 文獻／文件篩選邊界與流程不足以重建 | R1 | absence: §三（一）研究設計與檢索 — expected 明確納入排除標準、檢索期間與逐階段篩選規則; checked §三（一）、中文摘要、§五（五） | R1 |
| 2 | 本次取得語料不足與臺灣公開證據總體不足尚未完全拆開 | DA | text: §一（二） "此說法只適用於本次檢索，不能推論其他公開、付費或內部研究不存在。" | R2 |
| 3 | 最低公開證據稽核的新增價值與待驗證狀態未充分區別 | EIC | text: §五（二） "它尚未接受獨立編碼、使用者研究、閾值校準或預測檢驗，也沒有證明管理成效。" | R3 |

### Required Revisions

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| R1 | 補足有限檢索的資格、時間範圍、篩選流程與各階段數量，必要時核對現有候選清單 | SC-3 | major | absence: §三（一）研究設計與檢索 — expected 明確納入排除標準、檢索期間與逐階段篩選規則; checked §三（一）、中文摘要、§五（五） | 4 — 有限證據檢索與可重現篩選 | R1 | P1 | 2–4 days |
| R2 | 將官方資料可判定、已取得全文可判定及未搜索／不可得範圍分成三個明確結論層級 | SC-10 | major | text: §一（二） "此說法只適用於本次檢索，不能推論其他公開、付費或內部研究不存在。" | 5 — 負面證據與推論邊界 | DA | P1 | 1–2 days |
| R3 | 重寫程序貢獻：界定概念來源、新增元素、與一般因果／資料品質警示的差異及待驗證prototype地位 | SC-1 | major | text: §五（二） "它尚未接受獨立編碼、使用者研究、閾值校準或預測檢驗，也沒有證明管理成效。" | 4 — 高教期刊貢獻判準 | EIC | P1 | 2–3 days |
| R4 | 操作化證據層級到處置狀態的規則，說明可產生非「延後」輸出的條件與反例 | SC-4 | major | table: 表2 — 八項策略之證據層級、暫定狀態與缺口 | 5 — 論證結構與可反駁性 | DA; R1 corroborating | P1 | 2–3 days |

### Required Item Details

**R1: 重建有限檢索流程**
- **Problem**: 搜尋數量透明，但納入排除、時間範圍及逐階段決策規則不足。
- **Source**: R1 W1。
- **Requirement**: 從既有稽核檔建立精簡流程表或附錄；不得把有限檢索改稱系統性回顧。
- **Acceptance criteria**: 讀者可由稿件與附錄重建316個候選群組如何形成9篇實質全文及9筆保留紀錄，所有數量與既有日誌一致。

**R2: 分離三種證據範圍**
- **Problem**: 本次可取得全文的不足仍可能被讀成臺灣公開證據整體不足。
- **Source**: DA M1，與R1 W1及R2 W1相鄰。
- **Requirement**: 在摘要、緒論、結果與結論使用一致的三層範圍語句，明示未知範圍。
- **Acceptance criteria**: 每個「唯一／不足／缺乏」主張都能被歸入官方資料、已取得完整原文或未取得／未搜索範圍，且不把零取得寫成零存在。

**R3: 界定prototype的可出版增量**
- **Problem**: 程序可追溯，但與既有一般警示的差異、概念來源及驗證狀態不夠清楚。
- **Source**: EIC W1。
- **Requirement**: 新增精簡定位段落，將已成立貢獻限於程序可追溯性，並提出可靠性、使用者與判定效度的後續評估方式。
- **Acceptance criteria**: 文章可用一段文字回答「相較一般因果與資料品質檢查新增什麼」，且未宣稱信效度、預測力或管理效果。

**R4: 操作化表2輸出規則**
- **Problem**: 延後／停止輸出可能只是預設保守規則，缺少可反駁性。
- **Source**: DA M2；R1 W2 corroborating。
- **Requirement**: 為可見性、關聯、效果與風險閘門提供明確decision rules，加入至少一個在何種公開／內部證據下可形成不同輸出的假設例。
- **Acceptance criteria**: 第三方可依相同輸入得到相同prototype狀態，並可指出至少一組會使輸出不同的條件；停止仍不得被寫成自動停系或關校。

### Suggested Revisions

| # | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Priority | Estimated Effort |
|---|---|---|---|---|---|---|---|---|
| S1 | 補強臺灣私校退場、區域招生差異與校務研究的有界領域定位 | SC-5 | minor | absence: §二文獻回顧 — expected 近年臺灣私校招生治理、退場或區域差異研究之定位; checked §二（一）至§二（四）及參考文獻 | 4 — 臺灣高教政策脈絡 | R2 | P2 | 1–3 days |
| S2 | 將表2策略分成招募、學程容量、組織治理及合作支持類別 | SC-6 | minor | table: 表2 — 策略類別欄八項異質治理與招募行動 | 4 — 高教治理概念區分 | R2 | P2 | 0.5–1 day |
| S3 | 增加prototype使用者、責任角色、決策時點與紀錄workflow | SC-7 | minor | absence: §四（三）與§六（二） — expected 使用者、決策時點、責任角色與可稽核輸出流程; checked 表2、§五（二）至§五（四）、§六（二） | 4 — evidence-to-decision流程 | R3 | P2 | 1 day |
| S4 | 加入受影響者證據與最低諮詢條件，明示尚非共同設計 | SC-8 | minor | text: §五（四） "誰承擔成本、誰獲得利益" | 4 — 利害關係人治理 | R3 | P2 | 0.5 day |
| S5 | 為未來內部資料升級加入資料最小化、存取、揭露與刪除規則 | SC-9 | minor | text: §五（五） "再連結申請至註冊漏斗、C+E、留存、轉退學及負擔" | 4 — 教育資料治理 | R3 | P2 | 0.5 day |
| S6 | 正文簡化工具與頁面預檢細節，完整稽核紀錄移至附錄 | SC-2 | minor | text: §三（三） "由於pypdf不可用，雖以pdfinfo與pdftotext讀取九份PDF" | 4 — 期刊結構與讀者適配 | EIC | P3 | 0.5 day |

## Part 2: Revision Roadmap

### Priority 1 — Structural Revisions
- [ ] R1：補足並核對有限檢索流程。
- [ ] R2：分離三種可判定／未知的證據範圍。
- [ ] R3：界定最低公開證據稽核的新增價值與prototype狀態。
- [ ] R4：操作化表2的decision rules與反例條件。

### Priority 2 — Content Supplementation
- [ ] S1：有界補強臺灣領域定位。
- [ ] S2：重組異質策略類別。
- [ ] S3：加入使用與責任workflow。
- [ ] S4：加入受影響者證據欄位。
- [ ] S5：加入內部資料治理先決條件。

### Priority 3 — Text and Formatting
- [ ] S6：把完整性工具細節移至附錄並精簡正文。
- [ ] 最終排版時補學生、系所、課程及教師欄位，完成APA行距、頁碼與懸掛縮排。

### Revision Deadline

建議6週；若維持課程論文而非期刊投稿，可由授課期限縮短，但不可因此省略R1–R4的可驗證接受標準。

### Response Letter

修訂時須逐項回覆R1–R4及S1–S6，標示變更位置；若不採用建議項目，需說明證據與範圍理由。

## Part 3: Reviewer Report Summary

- **Journal-Fit:** 主題合適、邊界一致，但程序貢獻仍未形成可辨識的期刊增量。
- **R1 Methodology:** 官方量化重算穩健；有限檢索流程與表2映射需操作化。
- **R2 Domain:** 領域主張準確；臺灣當代定位與策略分類可補強。
- **R3 Perspective:** 風險與停止語義有價值；使用者、workflow、參與與資料治理仍不足。
- **DA:** 無CRITICAL；兩項MAJOR挑戰是負面證據範圍與表2輸出的可反駁性。

敬請依上述路徑進行實質修訂。修訂稿將進入verification re-review，而非直接接受。
