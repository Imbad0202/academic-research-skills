# Claude Code를 위한 Academic Research Skills

[![Version](https://img.shields.io/badge/version-v3.22.0-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v3.22.0)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20696614-blue)](https://doi.org/10.5281/zenodo.20696614)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Sponsor](https://img.shields.io/badge/sponsor-Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/crucify020v)

[English](README.md) | [简体中文版](README.zh-CN.md) | [繁體中文版](README.zh-TW.md) | [日本語版](README.ja-JP.md) | [Español](README.es-ES.md)

학술 연구를 위한 Claude Code 통합 스킬 모음으로, 연구 설계부터 논문 작성·검토·출판 준비까지의 전체 워크플로를 지원합니다.

**30초 만에 설치**(Claude Code CLI / VS Code / JetBrains, v3.7.0+):

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

그런 다음 `/ars-plan`을 실행해 소크라테스식 대화로 논문 구조를 짜보거나, 사전 요건과 전통적인 심볼릭 링크 방식을 보려면 [빠른 설치](#빠른-설치)로 이동하세요.

> **AI는 부조종사이지 조종사가 아닙니다.** 이 도구는 논문을 대신 써 주지 않습니다. 참고문헌 탐색, 인용 형식 정리, 데이터 검증, 논리적 일관성 점검과 같은 반복적이고 소모적인 작업을 지원하여, 실제로 사람의 판단이 필요한 부분 — 질문 정의, 방법 선택, 데이터가 의미하는 바의 해석, 그리고 "나는 ~라고 주장한다" 다음에 오는 문장을 쓰는 일 — 에 집중할 수 있게 합니다.
>
> 휴머나이저(humanizer)와 달리, 이 도구는 AI를 사용했다는 사실을 숨기도록 돕지 않습니다. 더 잘 쓰도록 돕습니다. Style Calibration은 과거 작업에서 사용자의 문체를 학습합니다. Writing Quality Check는 기계가 생성한 듯한 느낌을 주는 패턴을 잡아냅니다. 목표는 품질이지 부정행위가 아닙니다.

### 왜 완전 자동화가 아니라 인간 참여형(human-in-the-loop)인가?

Lu et al. (2026, *Nature* 651:914-919)은 **The AI Scientist**를 만들었습니다 — 최상위 ML 학회의 블라인드 동료 심사를 통과해 논문을 게재한 최초의 완전 자율 AI 연구 시스템입니다(ICLR 2025 workshop, 점수 6.33/10 vs workshop 평균 4.87). 이들의 Limitations 절은 완전 자율 AI 연구 파이프라인이 물려받는 실패 양상을 열거합니다: 구현 버그, 환각된 결과, 지름길 의존, 버그를 통찰로 재포장, 방법론 날조, 프레임 고착, 인용 환각.

ARS는 **AI의 지원을 받는 인간 연구자가 인간이나 AI가 단독으로 연구할 때보다 이러한 실패 양상을 더 효과적으로 줄일 수 있다**는 전제에서 설계되었습니다. Stage 2.5와 Stage 4.5 무결성 게이트는 7개 모드의 차단형 체크리스트를 실행합니다. 자세한 내용은 [`academic-pipeline/references/ai_research_failure_modes.md`](academic-pipeline/references/ai_research_failure_modes.md)를 참조하세요. 또한 리뷰어는 사용자가 제공한 골드셋에 대해 자신의 FNR/FPR을 측정하는 옵트인 calibration 모드를 제공합니다.

[**Zhao et al.**](https://arxiv.org/abs/2605.07723) (2026-05)은 arXiv, bioRxiv, SSRN, PMC의 250만 편 논문에 걸친 1억 1,100만 건의 참고문헌을 대규모로 점검했습니다. 이들의 보수적 추정치는 2025년 한 해에만 146,932건의 환각된 인용이며, 2024년 중반에 변곡점이 관찰되었습니다. bioRxiv-to-PMC 쌍에 대해서는 85.3%의 preprint-to-published 지속성을 보고합니다. 이 논문은 "인용된 참고문헌이 실제로는 뒷받침하지 않는 주장을 지지하기 위해 배치된 진짜 인용"을 미해결 과제로 기술합니다. ARS v3.7.1은 출처 provenance를 위한 trust-chain frontmatter를 추가했고, v3.7.3은 향후 주장 수준 감사를 위한 locator 인프라(3계층 인용 앵커)를 추가하고 인용 시점에 참고용 위험 신호를 표시합니다(ARS는 이 주장-충실성 격차를 내부적으로 "L3"로 라벨링합니다. 이는 ARS 용어이며 논문의 용어가 아닙니다). v3.7.x는 Zhao et al.의 코퍼스 규모 발견에 동기를 두며, ARS 자체에 대한 코퍼스 규모 평가는 향후 과제로 남아 있습니다.

v3.8은 L3 격차의 나머지 절반을 메웁니다. v3.7.3은 모든 인용이 locator 앵커를 갖도록 했고, v3.8은 각 앵커에 대해 인용된 출처를 가져와 주장이 실제로 뒷받침되는지 판단하는 옵트인 감사 패스(`ARS_CLAIM_AUDIT=1`)를 추가합니다. 다섯 개의 새로운 HIGH-WARN 클래스(claim-not-supported, negative-constraint-violation, fabricated-reference, anchorless, constraint-violation-uncited)의 출력을 formatter terminal hard gate가 거부합니다. 캘리브레이션은 FNR<0.15 + FPR<0.10 합격 임계값을 갖는 20개 항목으로 구성된 골드셋으로 제공됩니다. 단계적 활성화 계획은 v3.8 명세 §5에 따라 캘리브레이션 후 증거가 나올 때까지 보류됩니다.

v3.3은 [**PaperOrchestra**](https://arxiv.org/abs/2604.05018) (Song, Song, Pfister & Yoon, 2026, Google)에서 영감을 받았습니다: Semantic Scholar API 검증, anti-leakage 프로토콜, VLM 그림 검증, 수정 궤적 추적. 현재 ARS는 수치 델타 대신 기준별 증거 기반 서술형 회귀 점검을 수행하며, typed trajectory carrier는 아직 구현되지 않았습니다.

---

## 아키텍처 & 파이프라인

**👉 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — 전체 파이프라인 개요: 흐름도, 단계별 매트릭스, 데이터 접근 흐름, 스킬 의존성 그래프, 품질 게이트, 모드 목록.

아키텍처 문서는 기존의 상세한 파이프라인 설명을 대체합니다. *어떤 단계에서 무엇이 실행되는지*에 관한 모든 내용이 이제 한 곳에 있습니다.

## 빠른 설치

**사전 요건**

- [Claude Code](https://docs.claude.com/en/docs/claude-code/setup) (최신 버전. 플러그인 패키징은 최근 버전을 요구합니다)
- `ANTHROPIC_API_KEY`를 export하거나, 첫 `claude` 실행 시 설정
- *선택:* DOCX용 Pandoc, APA 7.0 PDF용 tectonic + Source Han Serif TC (Markdown 출력은 둘 다 없어도 동작)
- *선택(실제 Python):* write-scope guard와 몇몇 옵트인 명령에만 필요합니다. 핵심 스킬은 프롬프트 기반입니다. Windows의 Git Bash와 Microsoft Store Python 자리표시자에 관한 설명을 포함한 자세한 내용은 [docs/SETUP.md § Python (optional)](docs/SETUP.md#python-optional)(영어)을 참조하세요.

**플러그인 설치(v3.7.0+, 권장):**

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

**동작 확인:** `/ars-plan`을 실행하고 작업 중인 논문을 설명하세요 — ARS가 소크라테스식 대화를 시작해 논문의 장 구조를 함께 그려 줍니다. 단발성 테스트를 원하면 `/ars-lit-review "your topic"`을 시도하세요.

**👉 [docs/SETUP.md](docs/SETUP.md)** — 전체 가이드: Claude Code 설치, API 키 설정, DOCX/PDF용 선택적 Pandoc/tectonic, 교차 모델 검증(`ARS_CROSS_MODEL`), 여섯 가지 설치 방법(Plugin, project skills, global skills, claude.ai Project, repo-cloned, Claude Science 가져오기).

> **사용 중인 설치 채널에서 어떤 제어 메커니즘이 실제로 작동하나요?** 가용성은 설치 채널에 따라 다릅니다. 채널별 대조표를 참조하세요: [docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md)(영어).

**👉 [docs/DATA_FLOWS.md](docs/DATA_FLOWS.md)** — 어떤 데이터가 기기 밖으로 나가는지(서지 resolver, 명시적 동의가 필요한 선택적 교차 모델 호출, 업데이트 확인), 로컬 캐시에 무엇이 얼마나 저장되는지, 각 경로를 끄는 방법. (영어)

**Claude Science를 사용하시나요?** 네 개의 스킬을 바로 가져올 수 있습니다: **Skills → Import from GitHub**에서 `https://github.com/Imbad0202/academic-research-skills`를 붙여넣고 **Preview** → **Import 4 skills**(이 저장소 v3.14.0+ 필요 — 가져오기 도구는 marketplace manifest에 명시된 스킬 경로를 읽습니다). 가져오기는 특정 시점의 스냅샷입니다: ARS 업데이트 후에는 다시 가져오세요. 가져온 스킬은 ARS 방법론(연구/작성/리뷰 프로토콜)을 담습니다. Claude Code 전용 메커니즘 — slash commands, hooks, 서브에이전트 오케스트레이션 — 은 이전되지 않습니다. 자세한 내용은 [docs/SETUP.md](docs/SETUP.md) Method 5를 참조하세요.

**Pi를 사용하시나요?** `pi install git:github.com/Imbad0202/academic-research-skills`로 저장소 내 커뮤니티 유지보수 wrapper를 설치할 수 있습니다. 원본 ARS 콘텐츠를 기준으로 유지하며 Pi 전용 오케스트레이션 및 hook 제한을 문서화합니다. 자세한 내용은 [`pi/README.md`](pi/README.md)를 참조하세요.

**Codex CLI를 사용하시나요?** 대신 자매 배포판을 설치하세요: [`Imbad0202/academic-research-skills-codex`](https://github.com/Imbad0202/academic-research-skills-codex) — 동일한 워크플로 콘텐츠를, `ars-*` 별칭을 갖는 단일 `$academic-research-suite` 스킬로 Codex 네이티브 패키징한 것입니다.

## 성능 & 비용

**👉 [docs/PERFORMANCE.md](docs/PERFORMANCE.md)** — 모드별 토큰 예산, 전체 파이프라인 추정치(15,000 단어 논문 기준 약 $4–6), 권장 Claude Code 설정(Auto 모드. Agent Team 선택).

## 가이드 & 글

- [Academic Writing Shouldn't Be a Solo Act](https://open.substack.com/pub/edwardwu223235/p/academic-writing-shouldnt-be-a-solo?r=4dczl&utm_medium=ios) — 전체 파이프라인 워크스루(영어)
- [學術寫作不該是一個人的事：一套開源 AI 協作工具如何改變研究者的工作流](https://open.substack.com/pub/edwardwu223235/p/ai?r=4dczl&utm_medium=ios) — 完整使用指南（繁體中文）

---

## 한눈에 보는 기능

- **Deep Research** — 소크라테스식 가이드 모드, PRISMA 체계적 문헌고찰, 의도 감지, 대화 건강도 모니터링, 선택적 교차 모델 DA, Semantic Scholar API 검증을 갖춘 13개 에이전트 연구팀.
- **Academic Paper** — Style Calibration, Writing Quality Check, LaTeX 하드닝, 시각화, 수정 코칭, 인용 변환, anti-leakage 프로토콜, VLM 그림 검증을 갖춘 12개 에이전트 논문 작성.
- **Academic Paper Reviewer** — 기준별 증거에 연결된 서술형 판단(Journal-Fit Reviewer + 동적 리뷰어 3명 + Devil's Advocate), 양보 임계값 프로토콜, 공격 강도 보존, 선택적 교차 모델 DA 비평 / 캘리브레이션, R&R 추적 매트릭스, 읽기 전용 제약을 갖춘 7개 에이전트 다관점 동료 심사. 현재 live review는 항상 `NOT_CALIBRATED`이며, full calibration은 제한된 candidate profile만 만들고 live review 적용은 아직 연결되지 않았습니다.
- **Academic Pipeline** — 적응형 체크포인트, 주장 검증, Material Passport, 선택적 `repro_lock`, 선택적 교차 모델 무결성 검증, 대화 중 강화, 기준별 서술형 회귀 점검을 갖춘 10단계 파이프라인 오케스트레이터(typed trajectory carrier는 아직 미구현).
- **Data Access Level Metadata** (v3.3.2+) — 모든 스킬이 `data_access_level`(`raw` / `redacted` / `verified_only`)을 선언하며, `scripts/check_data_access_level.py`로 강제됩니다. Anthropic의 automated-w2s-researcher (2026)에서 패턴을 차용했습니다. 자세한 내용은 [`shared/ground_truth_isolation_pattern.md`](shared/ground_truth_isolation_pattern.md)를 참조하세요.
- **Task Type Annotation** (v3.3.2+) — 모든 스킬이 `task_type`(`open-ended` 또는 `outcome-gradable`)을 선언합니다. 현재 모든 ARS 스킬은 `open-ended`입니다.
- **Benchmark Report Schema** (v3.3.5+) — 정직한 벤치마크 비교를 위한 JSON Schema와 린트입니다. 자세한 내용은 [`shared/benchmark_report_pattern.md`](shared/benchmark_report_pattern.md)를 참조하세요.
- **Artifact Reproducibility Lockfile** (v3.3.5+) — Material Passport의 선택적 `repro_lock` 하위 블록. **재현 보장이 아니라 구성 문서화입니다** — LLM 출력은 바이트 단위로 재현 가능하지 않습니다. 자세한 내용은 [`shared/artifact_reproducibility_pattern.md`](shared/artifact_reproducibility_pattern.md)를 참조하세요.
- **Experiment Provenance Intake** (#260) — Material Passport의 선택적 `experiment_provenance[]`는 연구자가 **외부에서** 실행한 실험을 기록하며(ARS는 절대 실험을 실행하지 않습니다), 원고의 주장은 `claim_intent_manifest.planned_experiment_ids[]`를 통해 이에 연결됩니다. 무결성 게이트(Stage 2.5/4.5)는 실험 기반 각 주장을 선언된 provenance와 대조해 검증합니다 — `ALIGNED` / `OVERSTATED` / `NOT_SUPPORTED_BY_PROVENANCE` / `PROVENANCE_INSUFFICIENT` — **실험 자체가 옳았는지는 판단하지 않습니다**. fail-closed `experiment_intake_declaration`은 "실험을 실행했는가?"를 명시적인 Stage 1 결정으로 만듭니다(문헌 전용 실행조차 `no_experiments_declared`를 선언). 자세한 내용은 [`shared/handoff_schemas.md`](shared/handoff_schemas.md)의 §"Experiment Provenance Intake (#260)"를 참조하세요.

**무결성 및 검증의 경계:** ARS는 원고와 보고된 연구 과정을 점검합니다. 인용의 존재, 주장-출처 정합성, 보고된 방법론, 선언된 실험 결과와 원고 주장의 정합성, 그림·표의 충실성, 보고·절차·제출 패키지 준수를 다루며 일부 점검은 표본 기반이거나 LLM 판단을 사용합니다. ARS는 절차가 실제로 수행되었는지, 원자료가 진짜인지, 결과가 재현되는지를 **입증하지 않습니다**. 조작된 내용이 일관되게 보고되면 이러한 점검을 통과할 수 있습니다. 자세한 내용은 [POSITIONING.md의 "Integrity checks and the empirical-work boundary"](POSITIONING.md#integrity-checks-and-the-empirical-work-boundary)를 참조하세요.

---

## 쇼케이스: 실제 파이프라인 출력

실제 10단계 파이프라인 실행에서 나온 완전한 산출물 — 동료 심사 보고서, 무결성 검증 보고서, 최종 논문 — 을 확인하세요:

**[모든 파이프라인 산출물 둘러보기 →](examples/showcase/)**

| 산출물 | 설명 |
|---|---|
| [Final Paper (EN)](examples/showcase/full_paper_apa7.pdf) | APA 7.0 형식, LaTeX 컴파일 |
| [Final Paper (ZH)](examples/showcase/full_paper_zh_apa7.pdf) | 중국어 버전, APA 7.0 |
| [Integrity Report — Pre-Review](examples/showcase/integrity_report_stage2.5.pdf) | Stage 2.5: 날조된 참고문헌 15건 + 통계 오류 3건 적발 |
| [Integrity Report — Final](examples/showcase/integrity_report_stage4.5.pdf) | Stage 4.5: 회귀 없음 확인 |
| [Peer Review Round 1](examples/showcase/stage3_review_report.pdf) | Journal-Fit Reviewer + 리뷰어 3명 + Devil's Advocate |
| [Re-Review](examples/showcase/stage3prime_rereview_report.pdf) | 수정 후 검증 |
| [Peer Review Round 2](examples/showcase/stage3_review_report_r2.pdf) | 후속 심사 |
| [Response to Reviewers](examples/showcase/response_to_reviewers_r2.pdf) | 항목별 저자 응답 |
| [Post-Publication Audit Report](examples/showcase/post_publication_audit_2026-03-09.pdf) | 독립적 전체 참고문헌 감사: 3회의 무결성 점검이 놓친 21/68 문제 발견 |

---

## 동반 도구: Experiment Agent

연구가 글쓰기 전에 실험(코드 또는 인간 대상 연구)을 수행해야 한다면, [Experiment Agent](https://github.com/Imbad0202/experiment-agent) 스킬이 ARS Stage 1(RESEARCH)과 Stage 2(WRITE) 사이의 공백을 메웁니다.

```
ARS Stage 1 RESEARCH  →  RQ Brief + Methodology Blueprint
        ↓
  experiment-agent     →  run/manage experiments → validate results
        ↓
ARS Stage 2 WRITE     →  write paper with verified experiment results
```

**무엇을 하는가**: 실시간 모니터링과 함께 코드 실험(Python, R 등)을 실행하고, IRB 윤리 체크리스트로 인간 대상 연구 프로토콜을 관리하며, 11종 오류(fallacy) 감지로 통계를 해석하고, 재현성을 검증합니다.

**함께 사용하는 방법**: Stage 1 이후 ARS 파이프라인을 일시 중지하고, 별도의 experiment-agent 세션에서 실험을 실행한 다음, 결과를(Material Passport와 함께) ARS Stage 2로 다시 가져옵니다. ARS는 어떤 수정도 필요하지 않습니다. 설정 방법은 [experiment-agent README](https://github.com/Imbad0202/experiment-agent)를 참고하세요.

**Stage 1 intake 선언 (#260)**: Stage 1에서 ARS는 해당 실행이 실험 기반 주장을 포함할지 감지하고 Material Passport에 fail-closed `experiment_intake_declaration`을 설정합니다. 외부에서 실험을 실행했다면 연구자는 실험당 하나의 `experiment_provenance[]` 항목(`experiment_id`, 중첩된 `repro_lock`, `planned_vs_executed[]`, `negative_results[]`, `known_limitations[]`)을 입력하고 선언은 `experiments_declared`로 설정됩니다. 그렇지 않으면 `no_experiments_declared`로 설정됩니다. 이 선언은 **#260 이후 모든 passport에서 필수**입니다 — 실험을 전혀 다루지 않는 실행도 `no_experiments_declared`를 선언하므로, 잊힌 provenance 블록 때문에 무결성 게이트가 조용히 우회될 수 없습니다. `experiment_id`는 이 intake 시점에 고정되며, 작성자는 이후 `planned_experiment_ids[]`를 통해 이를 참조합니다.

**교육 측 동반 도구**: [Teaching Skills](https://github.com/YujxZJCN/teaching-skills)는 ARS 아키텍처(스킬 앙상블, 공유 계약, 단계별 게이트, Course Passport)를 학술 생활의 교육 측면에 적용합니다 — 강좌 설계 → 수업 → 평가 → 전달 → 성찰. 이것의 `sotl` 모드는 수업 탐구 프로젝트를 출판 단계를 위해 ARS deep-research / academic-paper로 넘깁니다.

---

## 사용법

### 빠른 시작

```
# 전체 연구 파이프라인 시작
You: "I want to write a research paper on AI's impact on higher education QA"

# 소크라테스식 가이던스로 시작
You: "Guide my research on AI in educational evaluation"

# 가이드된 플래닝으로 논문 작성
You: "Guide me through writing a paper on demographic decline"

# 기존 논문 검토
You: "Review this paper" (그런 다음 논문을 제공)

# 파이프라인 상태 확인
You: "status"
```

### 개별 스킬

#### Deep Research (8개 모드)

```
"Research the impact of AI on higher education"       → full 모드
"Give me a quick brief on X"                          → quick 모드
"Do a systematic review on X with PRISMA"             → systematic-review 모드
"Guide my research on X"                              → socratic 모드 (guided)
"Fact-check these claims"                             → fact-check 모드
"Do a literature review on X"                         → lit-review 모드
"Compare these papers in WHY/HOW/WHAT format"         → three-way-scan 모드
"Review this paper's research quality"                → review 모드
```

#### Academic Paper (11개 모드)

```
"Write a paper on X"                                  → full 모드
"Guide me through writing a paper"                    → plan 모드 (guided)
"Build a paper outline"                               → outline-only 모드
"I have a draft, here are reviewer comments"          → revision 모드
"Parse these reviewer comments into a roadmap"        → revision-coach 모드
"Write an abstract for this paper"                    → abstract-only 모드
"Turn this into a literature review paper"            → lit-review 모드
"Convert to LaTeX" / "Convert citations to IEEE"      → format-convert 모드
"Check citations"                                     → citation-check 모드
"Generate an AI disclosure statement for NeurIPS"     → disclosure 모드
"Audit my rebuttal draft against the reviews"         → rebuttal-audit 모드
```

#### Academic Paper Reviewer (6개 모드)

```
"Review this paper"                                   → full 모드 (Journal-Fit Reviewer + R1/R2/R3 + Devil's Advocate)
"Quick assessment of this paper"                      → quick 모드
"Guide me to improve this paper"                      → guided 모드
"Check the methodology"                               → methodology-focus 모드
"Verify the revisions"                                → re-review 모드
"Calibrate this reviewer against my gold set"         → calibration 모드
```

#### Academic Pipeline (오케스트레이터)

```
"I want to write a complete research paper"           → Stage 1부터 full 파이프라인
"I already have a paper, review it"                   → Stage 2.5 중간 진입 (무결성 먼저)
"I received reviewer comments"                        → Stage 4 중간 진입
```

> 파이프라인은 **Stage 6: Process Summary**로 끝납니다 — 6차원 협업 품질 평가(1–100 점수)와 함께 논문 작성 과정 기록을 자동 생성합니다.

### 지원 언어

- **번체중국어**(繁體中文) — 사용자가 중국어로 작성할 때 기본값
- **영어** — 사용자가 영어로 작성할 때 기본값
- 학술 논문용 이중언어 초록(중국어 + 영어)

> **다른 언어를 사용하시나요?** Socratic 모드(deep-research)와 Plan 모드(academic-paper)는 **의도 기반 활성화**를 사용합니다 — 특정 키워드가 아니라 요청의 의미를 감지합니다. 즉, 수정 없이 **어떤 언어에서도** 동작합니다.
>
> 다만, 일반적인 `Trigger Keywords` 섹션(스킬이 애초에 활성화되는지를 결정함)은 여전히 영어와 번체중국어 키워드를 나열합니다. 사용하는 언어에서 스킬이 안정적으로 활성화되지 않는다면, 각 `SKILL.md` 파일의 `### Trigger Keywords` 섹션에 해당 언어의 키워드를 추가해 매칭 신뢰도를 높일 수 있습니다.

### 지원 인용 형식

- APA 7.0 (기본값, 중국어 인용 규칙 포함)
- Chicago (Notes & Author-Date)
- MLA
- IEEE
- Vancouver

### 지원 논문 구조

- IMRaD (실증 연구)
- 주제별 문헌고찰(Thematic Literature Review)
- 이론 분석(Theoretical Analysis)
- 사례 연구(Case Study)
- 정책 브리프(Policy Brief)
- 학회 논문(Conference Paper)

---

## 스킬 상세

에이전트별 책임과 단계별 산출물은 이제 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)에 있습니다. 릴리스 메타데이터를 한 곳에 유지하기 위해 버전 번호는 여기에 고정합니다.

### Deep Research (v2.12.1)

13개 에이전트 연구팀. 모드: full, quick, review, lit-review, three-way-scan, fact-check, socratic, systematic-review. 전체 에이전트 명단과 산출물: ARCHITECTURE.md §3 참조.

### Academic Paper (v3.3.1)

12개 에이전트 논문 작성 파이프라인. 모드: full, plan, outline-only, revision, revision-coach, abstract-only, lit-review, format-convert, citation-check, disclosure, rebuttal-audit. 출력: MD + DOCX (가능한 경우 Pandoc 경유) + LaTeX (APA 7.0 `apa7` class / IEEE / Chicago) → tectonic 경유 PDF. 전체 에이전트 명단과 단계별 책임: ARCHITECTURE.md §3 참조.

### Academic Paper Reviewer (v1.11.1)

기준별 증거에 연결된 **서술형 판단**을 수행하는 7개 에이전트 다관점 심사. 모드: full, re-review, quick, methodology-focus, guided, calibration. 현재 live review와 Schema 6 package는 항상 `NOT_CALIBRATED`이며, full calibration은 제한된 candidate profile만 만들고 live review 적용은 아직 연결되지 않았습니다. 고정 총점을 Accept / Minor Revision / Major Revision / Reject에 매핑하지 않습니다. 1차 심사 패널 대 계약 기반 re-review 디스패치 경계: ARCHITECTURE.md §3 Stage 3 / Stage 3' 참조.

### Academic Pipeline (v3.22.0)

무결성 검증, 2단계 심사, 소크라테스식 코칭, 협업 평가를 갖춘 10단계 오케스트레이터. 파이프라인 보장: 모든 단계는 사용자 확인 체크포인트를 요구하며, 무결성 검증(Stage 2.5 + 4.5)은 MANDATORY이며 기록 없는 우회 경로가 없고(모든 오버라이드는 Stage 6를 위해 사용자 사유 기록을 요구), R&R Traceability Matrix(Schema 11)는 저자의 수정 주장을 독립적으로 검증합니다. v3.4는 Stage 2.5 / 4.5에 Compliance Agent(PRISMA-trAIce + RAISE)를 추가했습니다. v3.5는 모든 FULL/SLIM 체크포인트와 파이프라인 완료 시점에 **Collaboration Depth Observer**(`collaboration_depth_agent`, 자문 전용 — 절대 차단하지 않음)를 추가합니다. 필수(MANDATORY) 무결성 게이트(2.5 / 4.5)는 컴플라이언스 점검이 희석되지 않도록 observer를 명시적으로 건너뜁니다. Wang & Zhang (2026), IJETHE 23:11에 기반합니다. 에이전트·산출물·게이트를 포함한 단계별 매트릭스: ARCHITECTURE.md §3 참조.

---

## v3.0 최적화: AI의 구조적 한계에 대해 우리가 발견한 것

### 무슨 일이 있었나

고등교육의 AI에 대한 성찰 글을 쓰기 위해 ARS를 사용하던 중, 어떤 프롬프트 엔지니어링으로도 고칠 수 없는 세 가지 구조적 문제에 부딪혔습니다:

1. **프레임 고착(Frame-lock)**: AI에게 자기 논제에 대한 devil's advocate 토론을 시켰습니다. 실제로 그렇게 했습니다 — 네 라운드, 매번 더 정교해졌습니다. 하지만 모든 라운드는 내가 설정한 프레임 안에 머물렀습니다. DA는 논증을 공격했을 뿐 전제를 공격한 적이 없습니다. "우리가 애초에 올바른 질문을 논의하고 있는가?"를 묻지 않았습니다. 이는 v2.7 스트레스 테스트에서 31% 인용 오류율을 일으킨 것과 같은 패턴입니다: 검증하는 AI와 생성하는 AI가 동일한 인지 프레임을 공유합니다.

2. **반박에 대한 아첨(Sycophancy under pushback)**: DA의 공격에 이의를 제기할 때마다 너무 빨리 양보했습니다. 자신이 제기한 지적을 충분한 근거 없이 지나치게 쉽게 철회했습니다. 모델의 학습은 대화의 화합을 보상하므로 — "사용자가 반박했다"가 공격이 틀렸다는 증거로 취급되었지만, 사실은 사용자가 끈질겼다는 의미일 뿐인 경우가 많았습니다.

3. **의도 오인식(Intent misdetection)**: Socratic Mentor는 내가 아직 탐색 중인데도 계속 수렴해 산출물을 만들려 했습니다("정리해 드릴까요?"). "사용자가 깊은 철학적 논의를 원한다"와 "사용자가 RQ 브리프를 원한다"를 구분하지 못했습니다. 둘 다 참여처럼 보이지만 정반대의 AI 행동이 필요합니다.

### 우리가 바꾼 것 (v3.0)

**Devil's Advocate — 양보 임계값 프로토콜**(`deep-research` + `academic-paper-reviewer`)
- DA는 이제 응답 전에 모든 반박을 1-5 척도로 채점해야 합니다
- 양보는 점수 ≥4(반박이 증거와 함께 핵심 공격을 직접 다룸)에서만 허용됩니다
- 점수 ≤3: 입장을 유지하고 원래 공격을 다시 진술합니다
- 안티-아첨 규칙: 연속 양보 금지, 양보율 추적, 각 체크포인트 후 프레임 고착 감지

**Socratic Mentor — 의도 감지 계층**(`deep-research`)
- 대화 시작과 매 3턴마다 사용자 의도를 탐색형 대 목표지향형으로 분류합니다
- 탐색형 모드: 자동 수렴 비활성화, 최대 라운드를 60으로 상향, "요약해 드릴까요?" 프롬프트 금지
- 목표지향형 모드: 표준 수렴 동작
- 조기 종료 방지 규칙: 탐색형 모드에서는 사용자가 중단 시점을 결정합니다

**Socratic Mentor — 대화 건강도 지표**(`deep-research`)
- 매 5턴마다 세 차원(지속적 동의, 갈등 회피, 조기 수렴)에 대해 조용히 자기 평가합니다
- 동의 패턴이 감지되면 도전적 질문을 자동 주입합니다
- 사용자에게 보이지 않음(게이밍 방지). 단, 사후 세션 검토용 로그는 제공됩니다

### 왜 중요한가

이 최적화들은 AI의 구조적 한계를 해결하지 못합니다 — 한계를 가시화하고 관리 가능하게 만들 뿐입니다. DA는 충분히 강하게 밀어붙이면 결국 양보합니다. Socratic Mentor는 여전히 약간의 수렴 편향을 가집니다. 하지만 이제 아첨을 늦추고, DA가 양보를 정당화하도록 강제하며, Mentor가 사용자가 준비되기 전에 마무리하지 못하게 하는 명시적 체크포인트가 있습니다.

더 깊은 교훈: AI 리터러시는 AI를 도구로 사용하는 법을 배우거나, 윤리 규칙을 따르거나, AI 위험을 두려워하는 것이 아닙니다. AI와 충분히 깊이 관여해 그 구조적 한계를 — 그리고 그 과정에서 자신의 사고 한계를 — 스스로 발견하는 것입니다.

---

## 라이선스

이 저작물은 [CC-BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 하에 라이선스됩니다.

**다음을 자유롭게 할 수 있습니다:**
- 공유 — 자료를 복사하고 재배포
- 각색 — 자료를 리믹스, 변형, 기반으로 제작

**다음 조건 하에서:**
- **저작자 표시(Attribution)** — 적절한 출처를 표기해야 합니다
- **비영리(NonCommercial)** — 자료를 상업적 목적으로 사용할 수 없습니다

**저작자 표시 형식:**
```
Based on Academic Research Skills by Cheng-I Wu
https://github.com/Imbad0202/academic-research-skills
```

---

## 기여자

**Cheng-I Wu** (吳政宜) — 저자 및 메인테이너

**[aspi6246](https://github.com/aspi6246)** — 기여자. v3.1 최적화는 [Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics)의 패턴에서 영감을 받았습니다: 읽기 전용 제약 패턴, 일급(first-class) 설계로서의 안티패턴 성문화, 인지 프레임워크 접근(절차가 아니라 "어떻게 생각할지" 교육), 그리고 lean 스킬 크기 철학.

**[mchesbro1](https://github.com/mchesbro1)** — 기여자. `academic-paper-reviewer/references/top_journals_by_field.md`를 위한 IS Basket of 8 저널을 최초로 제안하고 초안을 작성했습니다([Issue #5](https://github.com/Imbad0202/academic-research-skills/issues/5)).

**[cloudenochcsis](https://github.com/cloudenochcsis)** — 기여자. IS 절을 *Basket of 8*에서 전체 *Senior Scholars' Basket of 11*로 확장 — *Decision Support Systems*, *Information & Management*, *Information and Organization*을 추가했습니다([Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7), [PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8)). 출처: [AIS Senior Scholars' List of Premier Journals](https://aisnet.org/research/seniorscholarsbasket/).

**[eltociear](https://github.com/eltociear)** (Ikko Eltociear Ashimine) — 기여자. 일본어 README([`README.ja-JP.md`](README.ja-JP.md))를 번역했습니다([PR #161](https://github.com/Imbad0202/academic-research-skills/pull/161)).

**[xpfo-go](https://github.com/xpfo-go)** (xpfo) — 기여자. 간체중국어 README([`README.zh-CN.md`](README.zh-CN.md))를 번역했습니다([PR #181](https://github.com/Imbad0202/academic-research-skills/pull/181)).

**[devCharlotte](https://github.com/devCharlotte)** — 기여자. 한국어 README([`README.ko-KR.md`](README.ko-KR.md))를 번역했습니다([PR #469](https://github.com/Imbad0202/academic-research-skills/pull/469)).

**[Yaobin29](https://github.com/Yaobin29)** — 기여자. [PR #433](https://github.com/Imbad0202/academic-research-skills/pull/433)에서 리뷰어 응답 도구를 제안했습니다. `deep-research three-way-scan` 모드와 `academic-paper rebuttal-audit` 모드(해당 PR의 `audit` 개념을 발전시킨 기능)가 v3.12.1에서 정식으로 통합되었습니다.

**[ktao732084-arch](https://github.com/ktao732084-arch)** — 기여자. `academic-paper`의 disclosure 시스템에 9개의 의학 출판 정책 대상, 대상별 필수 사실 입력 수집, fail-closed 독립형 렌더링을 추가해 확장했습니다([Issue #596](https://github.com/Imbad0202/academic-research-skills/issues/596), [PR #599](https://github.com/Imbad0202/academic-research-skills/pull/599)). 또한 EQUATOR 임상 보고 참고자료에 CARE, STARD, TRIPOD+AI 요약 지침과 fail-closed 연구 설계 라우팅을 추가했습니다([Issue #594](https://github.com/Imbad0202/academic-research-skills/issues/594), [PR #601](https://github.com/Imbad0202/academic-research-skills/pull/601)). 아울러 독립형 중국어 문헌 리졸버, API 프로토콜, 합성 전송 fixture 테스트 스위트를 설계하고 기여했습니다([Issue #595](https://github.com/Imbad0202/academic-research-skills/issues/595), [PR #600](https://github.com/Imbad0202/academic-research-skills/pull/600)).

---

## 변경 이력

여기에는 최근 3개 릴리스만 실려 있습니다. 전체 변경 이력은 영어판 [CHANGELOG.md](CHANGELOG.md)를 참조하세요. v3.21.2까지의 한국어 릴리스 요약은 [docs/changelog-archive/ko-KR.md](docs/changelog-archive/ko-KR.md)에 동결 보관되며 이후 갱신되지 않습니다.

### v3.22.0 (2026-09-16) — 출력 언어 쌍 계약, 로케일 트랙, plugin eval 스위트, Windows/전송 수정

> **추가되는 것은 구조, 증거는 범위 제한 유지:** v3.22.0에서는 레지스트리 키 기반 Schema 4 필드로 한 번의 실행이 출력 언어 쌍을 선언할 수 있으며, 필드가 없으면 기존 파일이 그대로 재현됩니다(#862 Phase 1, PR #869). 그 주위에 로케일 트랙을 세웠습니다: @didacrios가 기여한 es-ES README와 보수적인 트리거 문구, 커뮤니티가 유지하는 로케일 팩 정책과 단독 소유자 잠정 신청 경로입니다. 두 `claude plugin eval` 스위트(revision-coach, citation-check)와 reviewer-calibration harness는 회귀 가드와 dispatch 기반으로만 출하되며, 측정된 향상이나 보정값을 주장하지 않습니다. 수정: `/ars-mark-read`와 나머지 다섯 잠금 지점이 공용 `msvcrt` 백엔드로 Windows에서 동작, OpenAI 요청은 GPT-6 Astra가 거부하는 매개변수를 보내지 않음, 격리된 Codex 전송은 `effort=ultra`를 거부, 감사 출처는 실제 판정자 신원을 기록, 소크라테스 경로 F6은 방향을 미리 고르지 않음, 근거 없는 주장은 hedge로 구제되지 않음. README는 최근 3개 릴리스만 유지하고, Gartenberg 외와 Wang, Li 외가 human-in-the-loop 앵커에 합류했습니다. Roadmap Phase 4(단계별 증거 상한)는 이번 릴리스에서 제공되지 않으며 기간은 이월됩니다.

### v3.21.2 (2026-09-06) — 모델 현황 정렬(Fable 5.1 / GPT-6 Astra), 체크포인트 결정 출처, CJK 제목 매칭 수정

> **새 기능이 아니라 현황 정렬과 출처 명시:** v3.21.2는 2026년 9월에 나온 두 벤더 system card에 스위트를 정렬합니다. `gpt-6-astra`는 두 전송 경로 모두에서 provisional로 교차 모델 표에 들어가며, 세대 현황 정책에 따라 권장 OpenAI 검증 모델이 됩니다. `gpt-5.6-sol`은 ChatGPT 구독 인용 전송 경로에서의 validated 상태를 유지하며, 새로운 bakeoff 결과는 주장하지 않습니다. 격리된 Codex 전송 경로의 reasoning-effort 집합에 `ultra`가 추가됩니다. 두 가지 가드레일을 추가하되 둘 다 프롬프트 수준이며 ARS 측정이 아닌 벤더 문서에 근거합니다. 체크포인트 결정 출처(사용자 턴만 결정으로 간주하고, 결정은 서브에이전트에 그대로 재전달. 위험 R11), 그리고 제공자 측 모니터링이나 안전 개입을 전송 실패로 다루고 결코 판정으로 보지 않는 규정입니다. 두 카드에 대한 harness-retirement 감사는 아무것도 폐기하지 않았습니다(프롬프트 문구 폐기 0건. keep-as-debt 8건에 카드 인용 추가). 수정: CJK 제목이 네 인덱스 리졸버의 정확 제목 게이트에서 더 이상 실패하지 않으며(#798), 바깥 괄호는 하나의 균형 잡힌 단위를 이룰 때만 제거합니다(#800). autolink 왕복 테스트가 의존성을 선언하고(#801), `check_surface_form_parity`는 매니페스트 대신 깨진 환경을 지목하며, skill 목록 일치 lint를 추가하고(#809), R10 잔여 격차를 최신화하고(#813), MLA 규칙 한 줄을 바로잡았습니다(#805). 스위트/pipeline → v3.21.2; deep-research → v2.12.1; academic-paper → v3.3.1; academic-paper-reviewer → v1.11.1.

### v3.21.1 (2026-08-24) — 범위가 제한된 워크플로 기반, 봉인된 bakeoff, 전송 강화

> **명시된 항목만 측정되었으며 나머지는 범위가 제한됨:** v3.21.1은 codex-cli 0.147.0용으로 격리된 ChatGPT 구독 인용 transport를 복구하고 첫 Promotion Bakeoff를 기록합니다. `gpt-5.6-sol`은 이 구독 transport에서만 validated이며 first-party API 경로에서는 여전히 provisional입니다. 향후 bakeoff에는 봉인된 사전등록이 필요합니다. 또한 default-off 연구 워크플로 profile 기반(오프라인 결정론적 conformance만 제공하며 pipeline hook과 연구 계열별 출시 profile은 없음), opt-in inquiry-ledger alpha(`ARS_INQUIRY_LEDGER=1`), 아직 구현되지 않은 design-only alternative register를 추가합니다. 이들의 행동 증거는 `NOT_RUN`이며 사용성, 복구, novelty, 정확성 또는 연구 성과 개선을 주장하지 않습니다. 리뷰 기준 registry에는 출처에 근거한 예시용 MSR 2027 exact-profile proving set 하나가 추가되지만, 투고 대상(학술지·학회) 및 학문 분야 범위, 실제 저자 attest 또는 constructive-review 증거를 뜻하지 않으며 필요한 독립적 인간 평가도 아직 완료되지 않았습니다. 그 밖에 `data_access_level` 정렬, markdown lint 문법 통합, guard launcher degradation 등록, 비보증·비추천 커뮤니티 통합으로 OrcaRouter 등재가 포함됩니다. 스위트／pipeline → v3.21.1；deep-research → v2.12.1；academic-paper → v3.3.1；academic-paper-reviewer → v1.11.1.
