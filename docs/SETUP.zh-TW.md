# ARS 安裝設定

Academic Research Skills 的前置需求與選用設定。只需要 Markdown 輸出 + 預設 Claude Opus 4.7 pipeline 的人，大部分內容可以略過 — 見下方「最小可行設定」。

---

## 最小可行設定

1. 安裝 Claude Code（見下方）。
2. 設定 `ANTHROPIC_API_KEY`。
3. 在這個 repo（或任何把 ARS 放在 `.claude/skills/` 下的專案）執行 `claude`。

這樣就夠了 — 可得到 Markdown 輸出 + DOCX 轉換說明。以下其他內容都是選用。

---

## 安裝 Claude Code

**建議：原生安裝程式**（不需要 Node.js，自動更新）：

```bash
# macOS / Linux
curl -fsSL https://claude.ai/install.sh | bash

# Windows（PowerShell）
irm https://claude.ai/install.ps1 | iex
```

<details>
<summary>替代方案：npm 安裝（已棄用）</summary>

需要 Node.js 18+。

```bash
npm install -g @anthropic-ai/claude-code
```

</details>

## 設定 API Key

你需要一個 Anthropic API key，請至 <https://console.anthropic.com/> 取得。

```bash
# Claude Code 首次執行時會提示輸入 API key
claude
```

或設定環境變數：

```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
```

## DOCX 輸出（選用）

若要直接產出 `.docx`，需要安裝 [Pandoc](https://pandoc.org/)。若系統沒有 Pandoc，formatter 會回退為提供 Markdown + DOCX 轉換說明。

```bash
# macOS
brew install pandoc

# Linux (Debian/Ubuntu)
sudo apt-get install pandoc

# Windows — 請至 https://pandoc.org/installing.html 下載
```

## LaTeX / PDF 輸出（選用）

PDF 輸出需要 [tectonic](https://tectonic-typesetting.github.io/) 和特定字型。**這是選用的** — Markdown 輸出與 DOCX 轉換說明不需要這些。

```bash
# macOS
brew install tectonic

# Linux (Debian/Ubuntu)
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh

# Windows — 請至 https://tectonic-typesetting.github.io/en-US/install.html 下載
```

**所需字型**（APA 7.0 中文輸出）：

- **Times New Roman** — macOS/Windows 通常已內建；Linux 安裝 `ttf-mscorefonts-installer`
- **思源宋體 VF**（Source Han Serif TC VF）— 從 [Google Fonts](https://fonts.google.com/specimen/Noto+Serif+TC) 或 [Adobe GitHub](https://github.com/adobe-fonts/source-han-serif) 下載
- **Courier New** — 通常已內建

> 如果只需要 Markdown 輸出或 DOCX 轉換說明，可完全跳過此步驟。直接產出 `.docx` 需要 Pandoc，PDF 需要 `tectonic`。

---

## Material Passport `literature_corpus[]` adapter（v3.6.4+，選用）

如果你已經維護一個策展過的文獻語料（Zotero、Obsidian、PDF 資料夾等），可以先把它打包進 Material Passport，讓 Phase 1 ARS agent 在去外部資料庫搜尋之前先讀你的文獻庫。此功能 opt-in、presence-based — 沒提供語料時，ARS 走 external-DB-only flow，行為不變。

v3.6.4 附三個 reference Python adapter，位於 `scripts/adapters/`：

```bash
# 1. 安裝 adapter 依賴（PyYAML + jsonschema，已在 requirements-dev.txt）
pip install -r requirements-dev.txt

# 2. 跑一個對應你語料來源的 reference adapter。
#    --passport 與 --rejection-log 兩個皆為必填。
python scripts/adapters/folder_scan.py --input /path/to/pdfs               --passport passport.yaml --rejection-log rejection_log.yaml
python scripts/adapters/zotero.py      --input my-zotero-export.json       --passport passport.yaml --rejection-log rejection_log.yaml
python scripts/adapters/obsidian.py    --input ~/Obsidian/Lit\ Notes       --passport passport.yaml --rejection-log rejection_log.yaml

# 3. 把產出的 passport.yaml 帶進你的 ARS session
#    （實際 invocation 視你跑哪個 skill 而定 — 詳見 scripts/adapters/README.md）
```

每個 adapter 產兩個檔案：`passport.yaml`（Schema 9，已填 `literature_corpus[]`）與 `rejection_log.yaml`（永遠輸出，無 rejection 時為空，採 categorical reason 封閉 enum）。Reference 之外的語料來源預期由使用者自行撰寫 adapter，遵循 [`academic-pipeline/references/adapters/overview.md`](../academic-pipeline/references/adapters/overview.md)。

v3.6.5 接上 `bibliography_agent`（deep-research, Phase 1）與 `literature_strategist_agent`（academic-paper, Phase 1）作為 consumer — 兩者在 passport 帶非空 corpus 且解析成功時走 corpus-first / search-fills-gap flow。完整 consumer 協定見 [`academic-pipeline/references/literature_corpus_consumers.md`](../academic-pipeline/references/literature_corpus_consumers.md)。

## 選用環境變數（v3.5.1+）

ARS 暴露若干 opt-in flag，全部預設 OFF；設定後僅影響當前 session。

| Flag | 起始版本 | 作用 | 參考 |
|---|---|---|---|
| `ARS_CROSS_MODEL` | v3.0 | 啟用跨模型驗證（見下節） | [§「跨模型驗證」](#跨模型驗證選用) |
| `ARS_SOCRATIC_READING_PROBE=1` | v3.5.1 | 啟用 `socratic_mentor_agent` 的讀書檢查 probe layer。僅 goal-oriented intent；user 引用過具體論文時最多觸發一次；婉拒不留紀錄懲罰。 | `deep-research/agents/socratic_mentor_agent.md` |
| `ARS_PASSPORT_RESET=1` | v3.6.3 | 把每個 FULL checkpoint 提升為 context 重置邊界。**emit** boundary entry 必須設此 flag；新 session 用 `resume_from_passport=<hash>` 續跑**不需要** flag。`systematic-review` 模式下 flag ON 時，每個 FULL checkpoint 一律強制重置。 | `academic-pipeline/references/passport_as_reset_boundary.md` |
| `ARS_CROSS_MODEL_SAMPLE_INTERVAL` | v3.5.0 | 跨模型完整性抽查的取樣間隔（advisory） | `shared/cross_model_verification.md` |

---

## 跨模型驗證（選用）

ARS 使用 Claude Opus 4.7 即可完整運作。想要更高信心，可選擇啟用第二 AI 模型獨立驗證。

### 快速設定

```bash
# 設定 API key（擇一或兩者皆設）
export OPENAI_API_KEY="sk-your-key-here"        # GPT-5.4 Pro
export GOOGLE_AI_API_KEY="AIza-your-key-here"    # Gemini 3.1 Pro

# 選擇跨驗證模型
export ARS_CROSS_MODEL="gpt-5.4-pro"
# 或：export ARS_CROSS_MODEL="gemini-3.1-pro-preview"

# 照常啟動 Claude Code — 跨驗證會自動啟用
claude
```

### 啟用後的差異

| 功能 | 未啟用 | 啟用後 |
|---|---|---|
| 誠信驗證 | 單模型 100% 檢查 | + 30% 樣本由第二模型獨立驗證 |
| 魔鬼代言人 | 單模型 DA | + 跨模型獨立 critique，新發現自動加入 |
| 同儕審查 | 5 位審稿人（同模型） | + 來自第二模型的獨立 DA critique / calibration |

### 費用

完整 pipeline 會增加 ~$0.60-1.10 的跨模型 API 費用（GPT-5.4 Pro 定價）。詳細拆解見 [`shared/cross_model_verification.md`](../shared/cross_model_verification.md)。

### 沒有 API key？沒問題

沒有設定 `ARS_CROSS_MODEL`？一切照舊運作，無任何額外開銷。

---

## 安裝方式

### 方法一：作為專案 Skills（推薦）

將此 repo clone 到專案的 `.claude/skills/` 目錄：

```bash
cd /path/to/your/project
mkdir -p .claude/skills
git clone https://github.com/Imbad0202/academic-research-skills.git .claude/skills/academic-research-skills
```

接著將 `.claude/CLAUDE.md` 的內容複製到你專案的 `.claude/CLAUDE.md`（若已有則合併）。

> **全域安裝：** 若希望所有專案都能使用這些 skills，可安裝到 `~/.claude/skills/`：
>
> ```bash
> mkdir -p ~/.claude/skills
> git clone https://github.com/Imbad0202/academic-research-skills.git ~/.claude/skills/academic-research-skills
> ```

### 方法二：作為獨立專案

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git
cd academic-research-skills
claude
```

<details>
<summary><strong>沒有安裝 Git？</strong>直接下載 ZIP</summary>

1. 前往 <https://github.com/Imbad0202/academic-research-skills>
2. 點擊綠色 **Code** 按鈕 → **Download ZIP**
3. 解壓縮到你想要的位置
4. 方法一：將解壓後的資料夾移動到你專案內的 `.claude/skills/academic-research-skills`
5. 獨立使用：在解壓後的資料夾中開啟終端機，執行 `claude`

</details>

### 方法三：Claude Cowork（桌面版）

在 [Claude Cowork](https://claude.com/product/cowork) 中使用這些 skills — Claude Desktop 的 AI 自主工作區。

**選項 A：資料夾存取（最快）**

1. 將此 repo clone 到本機：
   ```bash
   git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills
   ```
2. 開啟 Claude Desktop → 點擊上方 **Cowork** 分頁
3. 選擇 clone 下來的 `academic-research-skills` 資料夾作為工作目錄
4. Claude 會自動從 `SKILL.md` 偵測並載入 skills

**選項 B：作為專案 Skills**

若你已有 Cowork 專案資料夾：

```bash
cd /path/to/your/project
mkdir -p .claude/skills
git clone https://github.com/Imbad0202/academic-research-skills.git .claude/skills/academic-research-skills
```

Skills 會在對話相關時自動載入 — 例如說「幫我寫論文」會觸發 `academic-paper`。

**需求：** Claude Desktop（最新版本）且已啟用 Cowork；付費方案（Pro、Max、Team 或 Enterprise）。

### 方法四：使用 claude.ai（網頁版）

透過 [claude.ai](https://claude.ai) 的 **Project** 功能搭配 GitHub 整合，即可使用這些 skills，不需要安裝 Claude Code。

1. 登入 [claude.ai](https://claude.ai)（需付費方案）
2. 建立新 Project：**Projects** → **Create Project**
3. 從 GitHub 匯入：在 Project 中，點擊 **Files** → **+** → **GitHub** → 選擇 `Imbad0202/academic-research-skills`

   **建議勾選項目**（以控制在容量限制內）：

   | 勾選 | 目錄 | 說明 |
   |---|---|---|
   | ✅ | `.claude/` | 路由規則 |
   | ✅ | `deep-research/` | 核心 skill |
   | ✅ | `academic-paper/` | 核心 skill |
   | ✅ | `academic-paper-reviewer/` | 核心 skill |
   | ✅ | `academic-pipeline/` | 核心 skill |
   | ✅ | `shared/` | 跨模型驗證、handoff schema |
   | ✅ | `MODE_REGISTRY.md` | Mode 定義 |
   | ❌ | `examples/` | 佔約 39% 容量，空間不足時可跳過 |
   | ❌ | `.github/`、README、LICENSE 等 | 功能運行不需要 |

4. （選用）將 `.claude/CLAUDE.md` 的內容貼入 Project 的 **Instructions**，以獲得更好的路由效果
5. 開始對話：「引導我研究 X」或「幫我寫一篇關於 Y 的論文」

**claude.ai 與 Claude Code 的差異：**

- claude.ai 不支援多 agent 平行執行和 shell 指令，效果可能不如 Claude Code 完整
- 跨模型驗證（`ARS_CROSS_MODEL`）需要 Claude Code + API key
- 直接產出 `.docx` 需要 Pandoc，PDF 需要 `tectonic`；claude.ai 仍可產出 Markdown 與 DOCX 轉換說明
