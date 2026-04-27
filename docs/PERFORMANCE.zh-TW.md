# ARS 效能說明

> **建議模型：Claude Opus 4.7**，搭配 **Max plan**（或同等配置）。Opus 4.7 採用 adaptive thinking，不需要手動指定 thinking budget。
>
> 完整學術 pipeline（10 階段）會消耗**大量 token** — 單次完整執行可能超過 200K 輸入 + 100K 輸出 token，視論文長度和修訂輪數而定。請依預算斟酌使用。
>
> 單獨使用個別 skill（如只用 `deep-research` 或 `academic-paper-reviewer`）的消耗明顯較少。

## 各模式 Token 消耗估算

| Skill / 模式 | 輸入 Token | 輸出 Token | 估算費用（Opus 4.7）|
|---|---|---|---|
| `deep-research` socratic | ~30K | ~15K | ~$0.60 |
| `deep-research` full | ~60K | ~30K | ~$1.20 |
| `deep-research` systematic-review | ~100K | ~50K | ~$2.00 |
| `academic-paper` plan | ~40K | ~20K | ~$0.80 |
| `academic-paper` full | ~80K | ~50K | ~$1.80 |
| `academic-paper-reviewer` full | ~50K | ~30K | ~$1.10 |
| `academic-paper-reviewer` quick | ~15K | ~8K | ~$0.30 |
| **完整 pipeline（10 階段）** | **~200K+** | **~100K+** | **~$4-6** |
| + 跨模型驗證 | +~10K（外部）| +~5K（外部）| +~$0.60-1.10 |

*以 ~15,000 字論文、~60 篇引用為基準估算。實際消耗隨論文長度、修訂輪數、對話深度而異。費用以 Anthropic API 2026 年 4 月定價計算。*

## 建議 Claude Code 設定

| 設定 | 功能說明 | 啟用方式 | 官方文件 |
|---|---|---|---|
| **Agent Team**（選用） | 啟用 `TeamCreate` / `SendMessage` tools 做手動多 agent 協作。**ARS 內部平行化不需要這個 flag** — skills 透過內建 `Agent` tool 直接 spawn subagent。僅在你想手動跨 session 協作持久 team 時有用。 | 設定 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`（研究預覽） | 實驗性功能 — 尚無穩定文件 |
| **Skip Permissions** | 跳過每次工具使用的確認提示，實現全 pipeline 不中斷的自主執行 | 啟動時加上 `claude --dangerously-skip-permissions` | [Permissions](https://docs.anthropic.com/en/docs/claude-code/cli-reference) · [Advanced Usage](https://docs.anthropic.com/en/docs/claude-code/advanced) |

> **⚠️ Skip Permissions 注意事項**：此旗標會停用所有工具使用的確認對話框。請自行斟酌使用 — 在可信任的長時間 pipeline 中非常方便，但會移除手動審核的安全機制。僅在你確定接受 Claude 自動執行檔案讀寫、shell 指令等操作時才啟用。

## 長時間 session 管理

完整 pipeline 設計為 human-in-the-loop，每個階段都需使用者確認。實務上一次完整執行會跨越數小時到數天，遠長於 Anthropic 的 prompt cache TTL（5 分鐘）。兩項結果：

1. **階段間 cache miss 是常態。** 當 stage checkpoint 停留超過 5 分鐘，下一階段會以未快取狀態讀取 context。這是 human-paced pipeline 不可避免的成本。
2. **跨 session 續跑依賴 Material Passport。** ARS 本身不跨 session 保留 orchestrator 狀態。要在新 session 續跑，把 Material Passport YAML 貼回即可；orchestrator 讀取 `compliance_history[]` 與階段完成標記定位中斷點。

### v3.4.0 compliance agent 成本

在 Stage 2.5 與 Stage 4.5 加上 mode-aware `compliance_agent` 會讓 SR 全 pipeline token 多出：

| Skill / 模式 | 輸入 Token | 輸出 Token | 估算費用 |
|---|---|---|---|
| `deep-research systematic-review`（僅 2.5）| +~5–8K | +~3–5K | +~$0.15 |
| 全 pipeline SR（2.5 + 4.5）| +~10–15K | +~5–8K | +~$0.30 |
| `academic-paper full`（pre-finalize）| +~3–5K | +~2–3K | +~$0.08 |

以上為既有 per-skill 成本之上的額外增量（與上表共用 15,000 字 / 60 篇引用基準，見上表下方 footnote）。跨模型驗證成本（若啟用）維持不變。

### v3.6.3 Passport 重置邊界（opt-in）

設定 `ARS_PASSPORT_RESET=1` 後，每個 FULL checkpoint 變成 context 重置邊界。預期工作流程：

1. Session A 跑完一個 stage 到 FULL checkpoint。
2. 從 checkpoint 通知抄下 `[PASSPORT-RESET: hash=<hash>, stage=<completed>, next=<next>]` tag。
3. 開新的 Claude Code session（session B），貼入 `resume_from_passport=<hash>`。支援可選覆蓋：`resume_from_passport=<hash> stage=<n> mode=<m>`。
4. Session B 只讀 passport ledger，不重播 session A 的對話。Orchestrator 找到相符的 `kind: boundary` entry，append 一個 `kind: resume` entry 完成消費，然後繼續。繼續的 stage 由以下順序決定：使用者在 resume 指令附上 `stage=` 時以其為準，否則當 boundary 帶 `pending_decision` 時由 orchestrator 先重新詢問使用者再用對應選項的 `next_stage`，否則才採用記錄的 `next` 欄位。所有選項都終止時，`next` 可以是 `null`。

**何時重置比延續划算：**

- 長 pipeline，session A 累積 >100K input token，下個 stage 不需要這些上下文。
- `systematic-review` 模式，stage 獨立性由 Material Passport 精確界定。
- 撞到 5 分鐘 prompt cache TTL：重置讓下個 stage 重新起算，不用在臃腫 context 上付 cache miss。

**何時延續仍然比較好：**

- 短 pipeline（end-to-end < 30K input token）。
- Stage 有 in-session 隱含狀態、passport 沒帶的情況（例如使用者想保溫的 Socratic 對話分支）。
- Flag OFF 時，延續是不變的 pre-v3.6.3 預設。

**Passport 檔案位置規約：**

Orchestrator 預設在目前工作目錄下尋找 `./passports/<slug>/` 或 `./material_passport*.yaml`。將 hash 解析到磁碟上的 passport 檔案是整合方的責任，orchestrator 載入呼叫端工具提供的 passport。預設位置見上方 `./passports/<slug>/` 規約。

Resume 指令只定義 hash 與可選的 stage/mode 覆蓋：

```
resume_from_passport=<hash> [stage=<n>] [mode=<m>]
```

Resume 指令本身沒有路徑語法。客製 passport 位置在專案的 `CLAUDE.md` 設定，或由整合方的工具在呼叫 orchestrator 前處理。

**實測 token 節省：** 尚待真實 `systematic-review` 搭配儀器化測量。取得實測資料後會回填本節。目前不做任何數值宣稱。完整協議見 [`../academic-pipeline/references/passport_as_reset_boundary.md`](../academic-pipeline/references/passport_as_reset_boundary.md)。

## 文獻語料庫導入（v3.6.4+）

Material Passport 的 `literature_corpus[]` 欄位由**使用者自行撰寫的 adapter** 產出，不是 ARS 本身。v3.6.4 附三個 reference adapter：`scripts/adapters/folder_scan.py`、`scripts/adapters/zotero.py`、`scripts/adapters/obsidian.py`。執行方式與自行撰寫 adapter 的指引見 [`scripts/adapters/README.md`](../scripts/adapters/README.md)。

### 效能定位

- Adapter 在 ARS session 之外執行（跑 ARS 前跑）；執行時間由使用者自行負責，不進 ARS 的時間預算。
- Adapter 必須具備 determinism：同一份 input 重跑產出 byte-identical 輸出（時間戳除外）。
- `literature_corpus[]` 依 `citation_key` 排序；`rejection_log.rejected[]` 依 `source` 排序。
- Adapter 輸出大小與語料庫大小線性成長。500 筆 Zotero 書目約產出 300 KB 的 passport YAML。大型語料庫建議 ARS 消費端採 lazy load。

### 導入層邊界

- 不讀 PDF 內容、不做文字抽取、不跑 OCR。
- 不呼叫 Zotero Web API、Notion API 或任何遠端服務。
- 不抓付費牆後內容、不用使用者憑證連線機構圖書館。

這些邊界是刻意的，反映 ARS 的 data-layer 定位：ARS 是 writing / review layer 的框架，語料整合留在 user-owned code。如需 API-based live-sync adapter，由使用者以三個 reference adapter 為起點自行撰寫。

### 消費端整合

v3.6.5 起，Phase 1 兩個文獻 agent 透過 **corpus-first、search-fills-gap** 流程讀取 `literature_corpus[]`：`deep-research/agents/bibliography_agent.md` 與 `academic-paper/agents/literature_strategist_agent.md`。兩者走相同的五步流程與四條 Iron Rule（Same criteria / No silent skip / No corpus mutation / Graceful fallback on parse failure）。Search Strategy 報告新增 PRE-SCREENED 可重現區塊，列出已納入／排除／略過的 corpus entry，並含 F3 zero-hit 與 F4 provenance 報告。消費端啟動採 presence-based — passport 帶非空 `literature_corpus[]` 且解析成功時自動進入；解析失敗時 fallback 到 external-DB-only flow，並 surface `[CORPUS PARSE FAILURE]`。

完整 consumer 協定見 [`academic-pipeline/references/literature_corpus_consumers.md`](../academic-pipeline/references/literature_corpus_consumers.md)。`citation_compliance_agent` 的 corpus 整合留到 v3.6.6+。
