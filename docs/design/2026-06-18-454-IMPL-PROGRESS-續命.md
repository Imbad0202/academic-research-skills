# #454 實作進度續命檔（2026-06-18）

**分支**: `fix/454-windows-python-hook-portability`（已 checkout）
**spec**: `docs/design/2026-06-17-454-windows-python-hook-portability-design.md`（已 commit `d050843`，已過 user approve + dual-track 四輪）
**狀態**: 實作中，working tree 有未 commit 改動。正在修 dual-track 實作審（第 5 輪）抓到的 7 個 bug。

## 已完成
- 回覆 #454 reporter（已 post，issue comment 4736057650）：白話 + 隱私保護 + 兩種診斷法，問「有沒有真 Python」，已收緊「VM 看到 placeholder ≠ 重現 bug」。
- 寫了 2 條 memory：更新 `feedback_absence_of_evidence_not_evidence_of_absence.md`（補「沒驗證卻假設存在」鏡像變體）+ 新 `feedback_cross_model_external_system_behavior_needs_first_party_docs.md` + MEMORY.md index 一行。
- 實作初版（TDD 紅→綠，16 測試曾全綠）：`hooks/run_guard.sh`（launcher）、`scripts/test_run_guard_launcher.py`、改 `hooks/hooks.json`(走 `bash .../run_guard.sh`)、CI assertion、`_ci_pytest_manifest.toml` 登記、新 `.gitattributes`(*.sh eol=lf)、README Python note。

## 根因/決策（已定，別重議）
- 根因：hook 寫死 `python3`，Windows 上是 0-byte Microsoft Store alias stub → 啟動前就炸。VM 實證 stub 存在，但 exit 49 確切來源沒重現（SYSTEM context 限制）。
- Plan A（甲）：找真 Python（跳過 stub）；沒真 Python **或** guard 自己壞掉 → pass-through + exit 0 + hot-path 靜默，**不擋**（使用者決定：ARS 核心不需 Python，guard 是 v3.10 可選加固，不該因環境/我們的 bug 鎖死使用者）。
- 不做：per-OS 分支、.ps1 twin、編譯 binary、逼裝 Python。沒 Git Bash 的 Windows = guard 不啟用（誠實標明仍會 hook-noisy）。

## 第 5 輪 dual-track 實作審抓到的 7 個 bug（codex POSIX 重現了 P1）
全部要修，進度如下：

- [x] **P1-a** marker probe 沒檢查 exit status（印 marker + exit 非零被誤收）→ 已修：`find_real_python` 抓 `probe_status` 要 `-eq 0`。
- [x] **P1-b** guard 執行沒 bound（guard hang 整個 hot path 卡死）→ 已修：guard 也走 `run_bounded`，timeout → pass-through。
- [x] **P1-c** 「valid JSON」只用 grep substring（`not json "hookSpecificOutput"` false-accept）→ 已修：新 `is_valid_hook_json()` 用已找到的真 Python 跑 `json.load` + isinstance dict + key 檢查（不引 jq）。
- [x] **P2-d** no-timeout watchdog 不夠強（只 TERM 直接 pid，忽略 TERM 的子進程會 hang/洩漏）→ 已修 launcher：`run_bounded` 改用 `setsid` 開 process group + kill 負 pid (TERM 後 1s KILL)，回 `TIMEOUT_STATUS=124`。**測試還沒補**（見下）。
- [x] **P2-e** test-only env 後門（`ARS_GUARD_PATH_FOR_TEST` 在 production 生效）→ launcher 已移除該後門（guard 路徑一律從 $0 推）；`ARS_NO_TIMEOUT_FOR_TEST` 改名 `ARS_GUARD_FORCE_WATCHDOG` 並誠實註解；`ARS_PROBE_BOUND` 保留但加整數驗證。**測試還在改一半（斷點在這）**。
- [x] **P2-h** launcher 吞健康 guard 的 stderr → 已修：guard stderr 捕到 temp，成功路徑 `cat >&2` 放出、降級路徑丟棄。
- [ ] **P2-f** CI assertion 假綠（只 grep `ars_write_scope_guard.py` 原始文字，註解就能滿足）→ **還沒修**。要改 `.github/workflows/spec-consistency.yml` 那段，驗「非註解的 exec/引用形狀」，不是純 substring。
- [ ] **P2-g** README 漏 Git Bash 前提 → **還沒修**。README Python note 要補一句：Windows 需 Git Bash（hooks.json 直接呼叫 `bash`），沒 Git Bash 不會乾淨 no-op 會 hook-noisy。

## 斷點：正在改 `scripts/test_run_guard_launcher.py`（已確認狀態）
**已確認**：`hooks/run_guard.sh` 的 7 項修改**全部套用成功**（grep 驗過：TIMEOUT_STATUS / is_valid_hook_json / ARS_GUARD_FORCE_WATCHDOG / setsid 都在；`ARS_GUARD_PATH_FOR_TEST` 後門已從 launcher 移除）。
**但** `scripts/test_run_guard_launcher.py` **還是舊版，Edit 沒套用**：`_run_launcher` 仍有 `guard_override`/`with_sys_timeout` 參數（line 74），仍在 line 89 設 `ARS_GUARD_PATH_FOR_TEST`，guard-broke 測試 line 281/308 仍用 `guard_override=`。
**後果**：launcher 已移除後門但測試還在用它 → 現在跑測試，`LauncherGuardBrokeTest` 4 個會壞（後門失效，guard 路徑改從 $0 推，指不到 temp 壞 guard）。**這是預期的紅，續做測試改寫即可。**

### 測試還要做的（P2-e/d 收尾 + 補 P1-a/c 漏的覆蓋）
1. helper 改完後，`LauncherGuardBrokeTest` 的 4 個測試要改：不再用 `guard_override=`，改成建一個 temp plugin layout（hooks/run_guard.sh 複本 + scripts/壞guard.py + scripts/manifest），跑那個複本 launcher。參考既有 `test_plugin_path_with_spaces` 的 layout 建法。
2. 補 **P1-a 測試**：fake python3 印 `ARS_PY_OK` 但 `exit 9` → 必須被跳過（pass-through），證明 probe 檢查 exit status。
3. 補 **P1-c 測試**：壞 guard 印 `not json but has "hookSpecificOutput"` → 必須 pass-through（證明不是 substring grep）。（注意：guard-broke 測試現在要用 temp layout 跑真 launcher 複本 + 真 Python，壞 guard 是 temp 裡的 .py。）
4. 修 **P2-d 測試**：`test_no_timeout_binary_present` 改用 `ARS_GUARD_FORCE_WATCHDOG=1`（不是舊的 `ARS_NO_TIMEOUT_FOR_TEST`）；hanging 測試要加一個「強制 watchdog 路徑」的變體（`ARS_GUARD_FORCE_WATCHDOG=1` + sleep 候選 → 確認被 process-group kill）；移除 dead `with_sys_timeout` 殘留引用。
5. 全部 `extra_env` 仍要帶 `ARS_PROBE_BOUND=1`（helper 已預設）。

## 收尾步驟（測試綠之後）
1. `python3 -m pytest scripts/test_run_guard_launcher.py -q` 全綠 + `python3 -m pytest scripts/test_ars_write_scope_guard.py -q` 沒打壞（55 passed 基準）。
2. `shellcheck hooks/run_guard.sh`（之前 SC1007 已 disable，確認無新 error）。
3. 重跑 CI hooks.json assertion（改完 P2-f 後）。
4. **再跑一輪 dual-track 實作審**（第 6 輪）確認 7 個 bug 真修好、沒引新洞（codex 會 POSIX 重現驗證）。
5. CHANGELOG + 版本（repo 有 version-consistency lint，查 `check_version_consistency`）。
6. commit（分支已開）→ push → 開 PR（ruleset repo 一律 PR；body 結尾加 Generated with Claude Code）。
7. 等 reporter 回診斷 → 若有真 Python，確認修法直接解決他。

## 注意事項（踩過的坑）
- background codex 必接 `< /dev/null`（已知）。
- launcher 測試慢（probe bound）→ helper 已設 `ARS_PROBE_BOUND=1`，hanging 測試容忍久一點。
- 測試 PATH = `bin_dir + _SYS_PATH`（bin_dir 在前遮蔽系統 python），跑 sh 用絕對路徑 `_SH`。
- guard 永遠 exit 0、靠 JSON `permissionDecision:"deny"` 表示拒絕 → 測試 assert JSON 不 assert exit code。
- public repo：push 前確認無個資（diff 過，乾淨）。
