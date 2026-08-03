# Response to Reviewers — Revision Round 1

感謝五位審查者與編輯的具體建議。本次修訂採「測量核心、範圍分層、prototype降級」姿態，依R1→R2→R4→R3完成必修項目，再逐項處理S1–S6。修訂沒有新增文獻搜尋、來源或效果資料。

## Summary

- **Resolved:** 9
- **Deliberate limitation:** 1
- **Unresolvable / reviewer disagreement:** 0
- **Canonical whitespace word-count delta:** −40（已排除HTML audit markers；中文仍應以字元解讀）
- **New references:** 0
- **Patch chain:** 3 deterministic patch rounds; no structural acknowledgment or full re-emission

## Required revisions

### REV-001 / R1 — Screening reconstruction

**Reviewer comment:** 補足有限檢索的資格、時間範圍、篩選流程與各階段數量。

**Status:** RESOLVED

**Response:** 已依既有日誌補入凍結檢索期間、平台、納入排除規則、去重、初篩，以及382筆原始紀錄至316候選群組、96近審、18身分驗證、9全文與9保留紀錄的流程。附錄A提供逐階段規則與數量，且不將本研究改稱系統性回顧。

**Changes:** §三（一）、§五（五）、附錄A；blocks B0030, B0031, B0070, B0113–B0116。

### REV-002 / R2 — Three evidence scopes

**Reviewer comment:** 分開官方資料、已取得全文及未搜索／不可得範圍。

**Status:** RESOLVED

**Response:** 中英文摘要與正文現在一致區分三種範圍，明示零取得不等於零存在，並放棄「臺灣公開證據整體不足」的主張。第二個聚焦patch補足討論中的最後一處「唯一」範圍限定並更新protected-hedges roster。

**Changes:** 摘要、§一（二）、§二（四）、§三（一）、§四（二）、§五、§六及protected-hedges；blocks B0004, B0007, B0014, B0015, B0027, B0031, B0048, B0058, B0060, B0070, B0075, B0077, B0111。

### REV-003 / R3 — Contribution and prototype demotion

**Reviewer comment:** 界定程序貢獻與一般方法警示的差異及待驗證prototype地位。

**Status:** RESOLVED

**Response:** 主要貢獻改為可重製的臺灣雙指標／分母測量案例及三層範圍報告；prototype降為次要、可反駁但未驗證的程序提案。全文不主張信度、效度、可用性、預測力、管理成效或一般化。

**Changes:** 摘要、§一（二）、§四（三）、§五（二）、§六；blocks B0004, B0007, B0014, B0015, B0050, B0053, B0054, B0060, B0061, B0075, B0077, B0078, B0111。

### REV-004 / R4 — Input-sensitive decision rules

**Reviewer comment:** 操作化證據到處置的規則並說明非延後輸出的條件。

**Status:** RESOLVED

**Response:** 表2現包含「效果評估門檻已達」、「可設計證據生成試辦」、「停止採用或擴大」及「延後判定」四項輸出，並按策略群組列出改變輸出的關鍵輸入。另加入編碼不一致、規則不敏感、正反例同態、選擇性填寫及不公平後果等撤回條件。

**Changes:** §二（四）、§四（三）表2、§五（二）、§六（二）；blocks B0027, B0050, B0052, B0112, B0053, B0054, B0061, B0077, B0078。

## Suggested revisions

### REV-005 / S1 — Taiwan domain positioning

**Status:** DELIBERATE_LIMITATION

**Response:** 依核准策略，本輪沒有新增文獻搜尋，也不以中繼資料補成主張。正文與附錄僅用既有搜尋、排除、失敗及保留紀錄呈現有界檢索版圖。

**Justification:** 新增文獻會移動凍結語料邊界；現有不可得／中繼資料只能證明檢索狀態，不能支持領域實質結論。因此透明保留缺口，而不假裝完成臺灣領域補強。

**Changes:** §三（一）、§五（五）、附錄A；blocks B0030, B0031, B0070, B0113–B0116。

### REV-006 / S2 — Strategy categories

**Status:** RESOLVED

表2已重組為學程與容量、組織治理、招募支持及合作支持，並另列私立一般大學的已取得全文範圍。Changes: B0052, B0112。

### REV-007 / S3 — User workflow

**Status:** RESOLVED

已加入提案、校務研究查核、教務／學務與法遵風險審查、決策紀錄及重審日期，並標示為未測程序。Changes: B0060, B0062。

### REV-008 / S4 — Affected-party evidence

**Status:** RESOLVED

已要求未來記錄學生、教師、行政人員及合作方的負擔與支持需求，並明示本研究不是共同設計且未蒐集參與者資料。Change: B0068。

### REV-009 / S5 — Internal-data governance

**Status:** RESOLVED

已加入資料最小化、用途限制、角色型存取、聚合揭露、存取／決策紀錄與保存刪除條件。Changes: B0062, B0068。

### REV-010 / S6 — Technical detail placement

**Status:** RESOLVED

正文保留必要驗證限制；查詢、失敗、篩選數量、撤稿／更正與頁面映射細節集中於附錄A。Changes: B0037, B0070, B0113–B0116。

## Patch provenance

1. `phase6-round1/revision_patch_round1.json` → `04-revised-course-paper-round1.md`; preserved ratio 0.8108.
2. `phase6-round1/revision_patch_round2.json` → `05-revised-course-paper.md`; preserved ratio 0.9828.
3. `phase6-round1/revision_patch_round3.json` → `09-revised-course-paper-for-inspection.md`; preserved ratio 0.9828. This final focused round retained exactly two numbered/tabular displays by converting the strategy-group and appendix accounting into prose lists.

Apply-chain hashes are continuous from `e51e77f36f2c` to `8ad94b3a3eab` to `cd87ea2971a8` to `ac17240daede`. The immutable Stage 3 input was not edited.
