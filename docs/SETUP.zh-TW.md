# ARS 安裝設定

Academic Research Skills 的前置需求與選用設定。只需要 Markdown 輸出與預設 Claude Opus 4.7 pipeline 的人，大部分內容可以略過。請見下方「最小可行設定」。

---

## 最小可行設定

1. 安裝 Claude Code（見下方）。
2. 設定 `ANTHROPIC_API_KEY`。
3. 在這個 repo（或任何把 ARS 放在 `.claude/skills/` 下的專案）執行 `claude`。

這樣就夠了。可得到 Markdown 輸出與 DOCX 轉換說明。以下其他內容都是選用。

---

## 安裝 Claude Code

**建議：原生安裝程式**（不需要 Node.js，自動更新）：

```bash
# macOS / Linux
curl -fsSL https://claude.ai/install.sh | bash

# Windows (PowerShell)
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
# Claude Code will prompt for your API key on first run
claude
```

或設定環境變數：

```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
```

## DOCX 輸出（選用）

若要直接產出 `.docx`，需要安裝 [Pandoc](https://pandoc.org/)。若系統沒有 Pandoc，formatter 會回退為提供 Markdown 與 DOCX 轉換說明。

```bash
# macOS
brew install pandoc

# Linux (Debian/Ubuntu)
sudo apt-get install pandoc

# Windows — download from https://pandoc.org/installing.html
```

## LaTeX / PDF 輸出（選用）

PDF 輸出需要 [tectonic](https://tectonic-typesetting.github.io/) 和特定字型。**這是選用的**。Markdown 輸出與 DOCX 轉換說明不需要這些。

```bash
# macOS
brew install tectonic

# Linux (Debian/Ubuntu)
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh

# Windows — download from https://tectonic-typesetting.github.io/en-US/install.html
```

**所需字型**（APA 7.0 中文輸出）：

- **Times New Roman**：macOS/Windows 通常已內建；Linux 安裝 `ttf-mscorefonts-installer`
- **Source Han Serif TC VF**（思源宋體）：從 [Google Fonts](https://fonts.google.com/specimen/Noto+Serif+TC) 或 [Adobe GitHub](https://github.com/adobe-fonts/source-han-serif) 下載
- **Courier New**：通常已內建

> 如果只需要 Markdown 輸出或 DOCX 轉換說明，可完全跳過此步驟。直接產出 `.docx` 需要 Pandoc，PDF 需要 `tectonic`。

---

## Material Passport `literature_corpus[]` adapters（v3.6.4+，選用）

如果你已經維護一個策展過的文獻語料（Zotero、Obsidian、PDF 資料夾等），可以先把它打包進 Material Passport，讓 Phase 1 ARS agent 在去外部資料庫搜尋之前先讀你的文獻庫。此功能採 opt-in 與 presence-based 設計。沒提供語料時，ARS 走 external-DB-only flow，行為不變。

v3.6.4 附三個 reference Python adapter，位於 `scripts/adapters/`：

```bash
# 1. Install adapter dependencies (PyYAML + jsonschema, already in requirements-dev.txt)
pip install -r requirements-dev.txt

# 2. Run a reference adapter (pick one that matches your corpus source).
#    Both --passport and --rejection-log are required.
python scripts/adapters/folder_scan.py --input /path/to/pdfs               --passport passport.yaml --rejection-log rejection_log.yaml
python scripts/adapters/zotero.py      --input my-zotero-export.json       --passport passport.yaml --rejection-log rejection_log.yaml
python scripts/adapters/obsidian.py    --input ~/Obsidian/Lit\ Notes       --passport passport.yaml --rejection-log rejection_log.yaml

# 3. Pass the resulting passport.yaml into your ARS session
#    (concrete invocation depends on which skill you're running — see scripts/adapters/README.md)
```

每個 adapter 產兩個檔案：`passport.yaml`（Schema 9，已填 `literature_corpus[]`）與 `rejection_log.yaml`（永遠輸出，無 rejection 時為空，採 categorical reason 封閉 enum）。Reference 之外的語料來源預期由使用者自行撰寫 adapter，遵循 [`academic-pipeline/references/adapters/overview.md`](../academic-pipeline/references/adapters/overview.md)。

v3.6.5 接上 `bibliography_agent`（deep-research, Phase 1）與 `literature_strategist_agent`（academic-paper, Phase 1）作為 consumer。兩者在 passport 帶非空 corpus 且解析成功時走 corpus-first / search-fills-gap flow。完整 consumer 協定見 [`academic-pipeline/references/literature_corpus_consumers.md`](../academic-pipeline/references/literature_corpus_consumers.md)。

## 選用環境變數（v3.5.1+）

ARS 暴露若干 opt-in flag，全部預設 OFF；設定後僅影響當前 session。

| Flag | 起始版本 | 作用 | 參考 |
|---|---|---|---|
| `ARS_CROSS_MODEL` | v3.0 | 啟用跨模型驗證（見下節） | [§「跨模型驗證」](#跨模型驗證選用) |
| `ARS_SOCRATIC_READING_PROBE=1` | v3.5.1 | 啟用 `socratic_mentor_agent` 的讀書檢查 probe layer。僅 goal-oriented intent；使用者引用過具體論文時最多觸發一次；婉拒不留紀錄懲罰。 | `deep-research/agents/socratic_mentor_agent.md` |
| `ARS_PASSPORT_RESET=1` | v3.6.3 | 把每個 FULL checkpoint 提升為 context 重置邊界。**emit** boundary entry 必須設此 flag；新 session 用 `resume_from_passport=<hash>` 續跑**不需要** flag。`systematic-review` 模式下 flag ON 時，每個 FULL checkpoint 一律強制重置。 | `academic-pipeline/references/passport_as_reset_boundary.md` |
| `ARS_CROSS_MODEL_SAMPLE_INTERVAL` | v3.5.0 | 跨模型完整性抽查的取樣間隔（advisory） | `shared/cross_model_verification.md` |

---

## 跨模型驗證（選用）

ARS 使用 Claude Opus 4.7 即可完整運作。想要更高信心，可選擇啟用第二 AI 模型來獨立驗證完整性檢查，並挑戰魔鬼代言人。

### 快速設定

```bash
# Step 1: Set your API key (choose one or both)
export OPENAI_API_KEY="sk-your-key-here"        # For GPT-5.4 Pro
export GOOGLE_AI_API_KEY="AIza-your-key-here"    # For Gemini 3.1 Pro

# Step 2: Choose your cross-verification model
export ARS_CROSS_MODEL="gpt-5.4-pro"            # Best reasoning
# or: export ARS_CROSS_MODEL="gemini-3.1-pro-preview"  # Strong at factual verification

# Step 3: Run Claude Code as normal — cross-verification activates automatically
claude
```

### 啟用後的差異

| 功能 | 未啟用跨模型 | 啟用跨模型 |
|---|---|---|
| 完整性驗證 | 單模型 100% 檢查 | + 30% 樣本由第二模型獨立驗證 |
| 魔鬼代言人 | 單模型 DA | + 跨模型產生獨立 critique，新發現自動加入 |
| 同儕審查 | 5 位審稿人（同模型） | 同樣 5 位審稿人 + 跨模型 DA critique / calibration 支援 |

### 費用

完整 pipeline 會增加約 $0.60-1.10 的跨模型 API 費用（GPT-5.4 Pro 定價）。詳細拆解見 [`shared/cross_model_verification.md`](../shared/cross_model_verification.md)。

### 沒有 API key？沒問題

沒有設定 `ARS_CROSS_MODEL` 時，一切照舊運作。跨模型功能不會出現，也不會增加任何額外開銷。

---

## 安裝方式

Claude 會在 `<install-root>/<skill-name>/SKILL.md` 尋找 skills。這個 repo 包含四個獨立 skills，每個都有自己的 `SKILL.md`：

- `deep-research`
- `academic-paper`
- `academic-paper-reviewer`
- `academic-pipeline`

不要把整個 repository 當成單一巢狀 skill 資料夾安裝到 `.claude/skills/academic-research-skills/`。那會讓四個 `SKILL.md` 比 Claude 可發現的位置多埋一層。請參考 Anthropic 的 [Claude Code Skills documentation](https://code.claude.com/docs/en/skills)。

### 方法一：作為專案 Skills（推薦）

當你希望 ARS 可在既有 Claude Code 專案內使用時，請用此方式。

先將 repo clone 到穩定的本機路徑，再把每個 skill 資料夾複製到專案的 `.claude/skills/` 目錄：

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills

cd /path/to/your/project
mkdir -p .claude/skills
cp -R ~/academic-research-skills/deep-research .claude/skills/deep-research
cp -R ~/academic-research-skills/academic-paper .claude/skills/academic-paper
cp -R ~/academic-research-skills/academic-paper-reviewer .claude/skills/academic-paper-reviewer
cp -R ~/academic-research-skills/academic-pipeline .claude/skills/academic-pipeline
```

預期路徑形狀：

```text
/path/to/your/project/.claude/skills/deep-research/SKILL.md
/path/to/your/project/.claude/skills/academic-paper/SKILL.md
/path/to/your/project/.claude/skills/academic-paper-reviewer/SKILL.md
/path/to/your/project/.claude/skills/academic-pipeline/SKILL.md
```

接著將 `.claude/CLAUDE.md` 的內容複製到你專案的 `.claude/CLAUDE.md`（若已有則合併）。

> **全域 Claude Code 安裝：** 若希望所有 Claude Code 專案都能使用這些 skills，請改安裝四個資料夾到 `~/.claude/skills/`：
>
> ```bash
> git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills
>
> mkdir -p ~/.claude/skills
> cp -R ~/academic-research-skills/deep-research ~/.claude/skills/deep-research
> cp -R ~/academic-research-skills/academic-paper ~/.claude/skills/academic-paper
> cp -R ~/academic-research-skills/academic-paper-reviewer ~/.claude/skills/academic-paper-reviewer
> cp -R ~/academic-research-skills/academic-pipeline ~/.claude/skills/academic-pipeline
> ```

### 方法二：作為獨立專案

當你想直接在 ARS repository 內工作時，請用此方式。

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git
cd academic-research-skills
claude
```

<details>
<summary><strong>沒有安裝 Git？</strong>改下載 ZIP</summary>

1. 前往 <https://github.com/Imbad0202/academic-research-skills>
2. 點擊綠色 **Code** 按鈕 → **Download ZIP**
3. 解壓縮 ZIP 到你想要的位置
4. 方法一：將解壓後的四個 skill 資料夾（`deep-research`、`academic-paper`、`academic-paper-reviewer`、`academic-pipeline`）複製到你專案內的 `.claude/skills/`
5. 獨立使用：在解壓後的資料夾中開啟終端機，執行 `claude`

</details>

### 方法三：Claude Cowork（桌面版）

當你想在 [Claude Cowork](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork) 使用四個 ARS skills 時，請用此方式。Cowork 是 Claude Desktop 的 agentic workspace。

Cowork 使用相同的 skill 資料夾形狀：`~/.claude/skills/<skill-name>/SKILL.md`。

#### 前置需求

- macOS 或 Windows 的最新版 Claude Desktop。請從 Anthropic 的 [Claude Desktop page](https://claude.ai/download) 下載。
- 可用的網路連線；Cowork tasks 會呼叫 Anthropic API。
- Cowork tasks 執行時，請保持 Claude Desktop 開啟。Cowork 在 Desktop process 內執行。
- Cowork 對 project folder 需有可讀寫的資料夾與檔案權限。
- 具備 Cowork 存取權的付費方案。目前方案可用性請參考 Anthropic 的 [Cowork requirements](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)。
- Team 或 Enterprise 方案中，組織管理員可能停用了 Skills、plugins、connectors 或 egress。若重啟後已安裝 skills 仍未註冊，請管理員檢查組織層級設定。

#### 選項 A：symlink 安裝（最快，單機使用）

如果你只在一台機器上工作，且希望日後透過 pull repo 更新，請使用 symlinks。

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills

mkdir -p ~/.claude/skills
cd ~/.claude/skills
ln -s ~/academic-research-skills/deep-research deep-research
ln -s ~/academic-research-skills/academic-paper academic-paper
ln -s ~/academic-research-skills/academic-paper-reviewer academic-paper-reviewer
ln -s ~/academic-research-skills/academic-pipeline academic-pipeline
```

預期路徑形狀：

```text
~/.claude/skills/deep-research/SKILL.md
~/.claude/skills/academic-paper/SKILL.md
~/.claude/skills/academic-paper-reviewer/SKILL.md
~/.claude/skills/academic-pipeline/SKILL.md
```

如果你透過雲端資料夾在多台機器之間同步 `~/.claude/skills`，請改用選項 B。絕對路徑 symlinks 可能在新的 checkout 或另一台機器上失效。

#### 選項 B：copy 安裝（跨機器安全，不會自動更新）

如果你在多台機器之間同步 `~/.claude/skills`，或不想使用 symlinks，請使用 copies。更新時需要重新執行四個 `cp -R` 指令。

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills

mkdir -p ~/.claude/skills
cp -R ~/academic-research-skills/deep-research ~/.claude/skills/deep-research
cp -R ~/academic-research-skills/academic-paper ~/.claude/skills/academic-paper
cp -R ~/academic-research-skills/academic-paper-reviewer ~/.claude/skills/academic-paper-reviewer
cp -R ~/academic-research-skills/academic-pipeline ~/.claude/skills/academic-pipeline
```

預期路徑形狀：

```text
~/.claude/skills/deep-research/SKILL.md
~/.claude/skills/academic-paper/SKILL.md
~/.claude/skills/academic-paper-reviewer/SKILL.md
~/.claude/skills/academic-pipeline/SKILL.md
```

#### 建立或開啟 Cowork Project

標準 UI 操作流程請參考 Anthropic 的 [Organize your tasks with Projects in Claude Cowork](https://support.claude.com/en/articles/14116274-organize-your-tasks-with-projects-in-claude-cowork)。

1. 開啟 Claude Desktop。
2. 使用模式選擇器（**Chat / Cowork**），切換到 **Cowork**。
3. 在 **Tasks** 中使用左側導覽面板，選擇 **Use an existing folder**（使用既有資料夾）。
4. 選取你希望 Cowork 在其中工作的本機資料夾。這會建立一個指向該資料夾的 Cowork Project。
5. 安裝或更新 skill 資料夾後，請重啟 Cowork，讓四個 skills 註冊。

#### Cowork 如何呼叫 skills

Claude 會使用每個 skill 的 `description` 判斷相關性，方式如 Anthropic 的 [Skills documentation](https://code.claude.com/docs/en/skills) 所述。例如 "help me write a paper" 這類句子只是示例，不是必須逐字輸入的 trigger phrase；改寫後的意圖也能運作。

若 description-based routing 沒有選到你想用的 skill，Cowork 也提供 Anthropic 的 [Cowork plugins documentation](https://support.claude.com/en/articles/13837440-use-plugins-in-claude-cowork) 中說明的顯式 UI 入口：

- 在 Cowork Task 中輸入 `/`，使用 command palette 並選取可用 skill。
- 使用 `+` capability picker，把 skill 加入目前 Task。

### 方法四：使用 claude.ai（網頁版）

claude.ai 有兩種不同方式可以使用這個 repository。兩者並不等價：

- **方法 4a** 會上傳真正的 Custom Skills。這是標準 claude.ai Skill 安裝路徑，支援自動載入與 skill routing。
- **方法 4b** 透過 GitHub integration 將 repository 檔案加入 Project 知識庫。這是備援知識模式，不是 Skill 安裝。

#### 前置需求

- 付費 claude.ai 方案。目前方案資訊請見 [claude.ai](https://claude.ai)。
- 方法 4a 不需要 GitHub 驗證。你要在本機將每個 skill 資料夾各自壓成 zip，再透過 **Settings** → **Capabilities** → **Skills**（設定 → 功能 → Skills）逐一上傳。Zip 結構錯誤與 200 字元 `description` 上限會在上傳時顯示錯誤；請參考 Anthropic 的 [Custom Skills packaging documentation](https://claude.com/docs/skills/how-to)。
- 方法 4b 需要透過 Anthropic connector 進行 GitHub 驗證。請參考 [Using the GitHub integration](https://support.claude.com/en/articles/10167454-using-the-github-integration) 與 [Set up Claude integrations](https://support.claude.com/en/articles/10168395-set-up-claude-integrations)。Private repositories 需要在 repo 或 organization 上授權 Anthropic GitHub App。Team 與 Enterprise 方案則需要 owner 層級先啟用 connector，使用者才能加入 GitHub 來源的檔案。

#### 方法 4a：Custom Skill upload（claude.ai 的標準 Skill 安裝路徑）

這是 claude.ai 真正的 Skill 安裝路徑。透過 **Settings** → **Capabilities** → **Skills**（設定 → 功能 → Skills）上傳，每個 skill 各一個 zip。

每個 zip 都必須把 skill 資料夾放在最上層，所以 zip 內容應包含 `<skill-name>/SKILL.md`，而不是 `<skill-name>/<skill-name>/SKILL.md`。

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git
cd academic-research-skills

zip -r deep-research.zip deep-research
zip -r academic-paper.zip academic-paper
zip -r academic-paper-reviewer.zip academic-paper-reviewer
zip -r academic-pipeline.zip academic-pipeline
```

接著上傳：

1. 登入 [claude.ai](https://claude.ai)。
2. 開啟 **Settings**。
3. 開啟 **Capabilities**。
4. 開啟 **Skills**。
5. 上傳 `deep-research.zip`。
6. 上傳 `academic-paper.zip`。
7. 上傳 `academic-paper-reviewer.zip`。
8. 上傳 `academic-pipeline.zip`。

v3.6.5.1 目前的 blocker：這個 repo 中四個 skill 的 `description` 欄位目前超過 200 字元上限，會被 upload UI 拒絕。Description trim 會在後續 patch（v3.6.5.2）推出。此處先記錄正確安裝方式；在 v3.6.5.2 發布前，請優先使用方法一、方法二或方法三。

#### 方法 4b：Project + GitHub integration（備援知識模式，不是 Skill 安裝）

claude.ai Projects 會將內容作為靜態知識提供給 Claude 擷取與引用。請參考 Anthropic 的 [What are Projects?](https://support.claude.com/en/articles/9517075-what-are-projects)。這不是 Skill 安裝。Skill 不會自動載入，trigger phrases 不會路由。Claude 可以讀取 repo 內容，但不會把 skills 當成 agentic workflows 執行。

當你希望 claude.ai 能存取 repo 內容以便閱讀或引用，但不需要 agentic skill execution 時，請使用此方式。

1. 登入 [claude.ai](https://claude.ai)。
2. 建立新 Project：**Projects** → **Create Project**。
3. 從 GitHub 匯入：在 Project 中，點擊 **Files** → **+** → **GitHub** → 選擇 `Imbad0202/academic-research-skills`。
4. 選取以下資料夾與檔案。

   | 選取 | 目錄 / 檔案 | 原因 |
   |---|---|---|
   | ✅ | `deep-research/` | 核心 skill 內容，可供閱讀 |
   | ✅ | `academic-paper/` | 核心 skill 內容，可供閱讀 |
   | ✅ | `academic-paper-reviewer/` | 核心 skill 內容，可供閱讀 |
   | ✅ | `academic-pipeline/` | 核心 skill 內容，可供閱讀 |
   | ✅ | `shared/` | 跨模型驗證、handoff schemas、共用 protocols |
   | ✅ | `scripts/` | `literature_corpus[]` adapters（`folder_scan`、`zotero`、`obsidian`）與 schema validators；Material Passport corpus mode 與 CI-style validation 需要 |
   | ✅ | `MODE_REGISTRY.md` | Mode definitions |
   | Optional | `.claude/` | Project-level routing rules。若你在下方步驟 5 設定 Project Instructions，建議跳過；只有在你偏好把 routing rules 作為 Project files 顯示時才納入。 |
   | Optional | `examples/` | 可作為參考範例；若想縮小 Project 知識庫，請跳過 |
   | Optional | `.github/`、READMEs、LICENSE 等 | Repository metadata；核心閱讀 context 不需要 |

5. （建議）將 `.claude/CLAUDE.md` 的內容設為 Project 的 **Instructions**，以獲得更好的 routing。
6. 開始對話："Guide my research on X" 或 "Help me write a paper about Y"。

Anthropic 目前的 [Project file limits](https://support.claude.com/en/articles/8241126-upload-files-to-claude) 說明：Project 並未刻意設定 200 檔上限，但每個檔案有 30 MB 大小限制，總可用內容仍受 runtime context-window 影響。請讓 Project 保持聚焦，Claude 才能穩定擷取相關檔案。

**claude.ai 與 Claude Code 的差異：**

- 方法 4b 用於內容閱讀，不是主動 Skill execution。若需要 agentic skill execution，請優先使用方法一、方法二、方法三，或在 v3.6.5.2 之後使用方法 4a。
- claude.ai 不支援本機 shell commands；結果可能不如依賴本機 scripts 的 Claude Code workflows 完整。
- 跨模型驗證（`ARS_CROSS_MODEL`）需要 Claude Code 與 API keys。
- 直接產出 `.docx` 需要 Pandoc，LaTeX/PDF 輸出需要 Claude Code 搭配 `tectonic`；claude.ai 仍可產出 Markdown 與 DOCX 轉換說明。