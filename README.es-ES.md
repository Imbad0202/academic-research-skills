# Academic Research Skills para Claude Code

[![Version](https://img.shields.io/badge/version-v3.21.2-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v3.21.2)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20696614-blue)](https://doi.org/10.5281/zenodo.20696614)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Sponsor](https://img.shields.io/badge/sponsor-Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/crucify020v)

[English](README.md) | [简体中文版](README.zh-CN.md) | [繁體中文版](README.zh-TW.md) | [日本語版](README.ja-JP.md) | [한국어](README.ko-KR.md)

Un conjunto completo de skills para Claude Code dedicadas a la investigación académica, que cubre todo el flujo desde la investigación hasta la publicación.

**Instalación en 30 segundos** (Claude Code CLI / VS Code / JetBrains, v3.7.0+):

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

Después prueba `/ars-plan` para revisar la estructura de tu artículo mediante diálogo socrático, o ve directamente a [Instalación rápida](#instalación-rápida) si necesitas los prerrequisitos y el flujo tradicional con enlaces simbólicos.

> **La IA es tu copiloto, no el piloto.** Esta herramienta no escribe tu artículo por ti. Se ocupa del trabajo pesado: buscar referencias, formatear citas, verificar datos, comprobar la coherencia lógica. Así puedes concentrarte en lo que de verdad requiere tu cabeza: definir la pregunta, elegir el método, interpretar qué significan los datos y escribir la frase que va después de «sostengo que».
>
> A diferencia de un humanizador, esta herramienta no te ayuda a ocultar que has usado IA. Te ayuda a escribir mejor. Style Calibration aprende tu voz a partir de trabajos anteriores. Writing Quality Check detecta los patrones que hacen que un texto se sienta generado por una máquina. El objetivo es la calidad, no hacer trampa.

### ¿Por qué un humano en el bucle y no la automatización completa?

Lu et al. (2026, *Nature* 651:914-919) construyeron **The AI Scientist**: el primer sistema de investigación autónomo por completo que publica un artículo tras revisión ciega por pares en una venue de primer nivel de machine learning (workshop de ICLR 2025, puntuación 6.33/10 frente a una media de 4.87 en el workshop). Su sección de Limitaciones enumera los modos de fallo que hereda cualquier pipeline de investigación autónomo: errores de implementación, resultados alucinados, dependencia de atajos, reinterpretación de bugs como hallazgos, fabricación de metodología, frame-lock y citas alucinadas.

ARS parte de la premisa de que **un investigador humano aumentado por IA evita esos modos de fallo mejor que cualquiera de los dos por separado**. Las puertas de integridad de la Etapa 2.5 y la Etapa 4.5 ejecutan una lista de bloqueo de 7 modos (consulta [`academic-pipeline/references/ai_research_failure_modes.md`](academic-pipeline/references/ai_research_failure_modes.md)); el revisor ofrece un modo de calibración opcional que mide su propio FNR/FPR contra un gold set proporcionado por el usuario.

[**Zhao et al.**](https://arxiv.org/abs/2605.07723) (2026-05) auditó 111 M de referencias en 2,5 M de artículos de arXiv, bioRxiv, SSRN y PMC. Su estimación conservadora es de 146.932 citas alucinadas solo en 2025, con un punto de inflexión observado a mediados de 2024; para el emparejamiento bioRxiv-PMC reportan una persistencia del 85,3 % de preprint a publicación. El artículo describe como problema abierto el uso de «citas reales desplegadas para sostener afirmaciones que las referencias citadas no sostienen realmente». ARS v3.7.1 añadió trust-chain frontmatter para la procedencia de las fuentes; v3.7.3 añadió infraestructura de localizadores (anclas de cita en tres capas) para futuras auditorías a nivel de afirmación y muestra señales de riesgo advertidas en el momento de citar (ARS llama internamente «L3» a esa brecha de fidelidad entre afirmación y fuente; es terminología de ARS, no del artículo). v3.7.x responde a los hallazgos a escala de corpus de Zhao et al.; la evaluación a escala de corpus del propio ARS sigue siendo trabajo futuro.

v3.8 cierra la segunda mitad de la brecha L3. v3.7.3 hizo que cada cita llevara un ancla de localizador; v3.8 añade una pasada de auditoría opcional (`ARS_CLAIM_AUDIT=1`) que recupera la fuente citada contra cada ancla y juzga si la afirmación está realmente sostenida. Cinco nuevas clases HIGH-WARN (claim-not-supported, negative-constraint-violation, fabricated-reference, anchorless, constraint-violation-uncited) bloquean mediante gate la salida de la hard gate terminal del formatter. La calibración se publica como un gold set de 20 tuplas con umbrales de aceptación FNR<0,15 + FPR<0,10; el plan de ramp-on se aplaza hasta tener evidencia post-calibración, según la especificación de v3.8 §5.

[**Ren et al.**](https://arxiv.org/abs/2607.13104) (2026, *Self-Improvements in Modern Agentic Systems: A Survey*) aporta una tercera ancla, a nivel de survey. Su síntesis sobre descubrimiento científico (§7.4) concluye que los agentes de descubrimiento no pueden verificar por sí mismos novedad, corrección o reproducibilidad y que pueden apoyarse en proxies débiles, que deben gestionar evidencia entre herramientas y literaturas heterogéneas y que plantean problemas de gobernanza: "la escritura científica también puede amplificar desinformación cuando la evidencia es débil". Sus capítulos sobre el bucle de generación (§5.1–§5.2) incluyen la auditoría humana y los anclas humanas conservadas entre las salvaguardas prácticas para bucles de evaluación autogenerados, y su capítulo histórico (§2.2) registra la forma más antigua de esa misma lección: el éxito práctico de EURISKO de Lenat dependía en gran medida de que el usuario actuara como señal externa de evaluación, podando la deriva improductiva de heurísticas; una limitación que el survey documenta como persistente en los sistemas agénticos modernos. ARS cita el survey como justificación de diseño de su postura de humano en el bucle, no como prueba empírica de que los pipelines con humano en el bucle superen a los autónomos; las mejoras accionables del survey para ARS se siguen en #539–#541 y #547–#550.

[**Gartenberg et al.**](https://doi.org/10.1287/orsc.2026.ed.v37.n3) (2026, *Organization Science* 37(3):795-812, "More versus better") aporta una cuarta ancla, y la primera desde la revista. El AI Task Force de *Organization Science* puntuó todas las primeras presentaciones (6.957) y todas las reseñas en formato de texto (10.389) que la revista recibió entre enero de 2021 y febrero de 2026 con un clasificador comercial de escritura por IA y índices estándar de legibilidad. Los manuscritos puntuados como muy escritos por IA se leían peor en esos índices y se desk-rechazaban más a menudo; las reseñas puntuadas como más escritas por IA se inclinaban hacia la teoría y se alejaban de los datos; y los editores concluyen que las herramientas de IA actuales, amplificadas por los incentivos de publish-or-perish, "parecen empujar el sistema hacia un equilibrio de más bien que de mejor investigación". Su §5 contrasta la «rendición cognitiva» (Shaw & Nave, 2026, según se cita allí) con un uso centrado en el humano y pide a los autores que declaren cómo se produjo el manuscrito. La evidencia es observacional, agregada y de una sola revista, y el clasificador es un instrumento propietario. ARS cita el editorial como justificación de diseño para registrar el volumen como no-objetivo (consulta `POSITIONING.md`) y para el Collaboration Depth Observer y la escalera de fuerza de afirmación, no como evidencia sobre la salida de ARS; las mejoras accionables se siguen en #829–#833.

v3.3 se inspiró en [**PaperOrchestra**](https://arxiv.org/abs/2604.05018) (Song, Song, Pfister & Yoon, 2026, Google): verificación con la API de Semantic Scholar, protocolo anti-fuga, verificación de figuras con VLM y seguimiento de la trayectoria de revisión. ARS implementa ahora esa última idea mediante trayectorias de criterios categóricas y ancladas en evidencia, en lugar de deltas de puntuación.

---

## Arquitectura y pipeline

**👉 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — la vista completa del pipeline: diagrama de flujo, matriz etapa por etapa, flujo de acceso a datos, grafo de dependencias entre skills, puertas de calidad y lista de modos.

El documento de arquitectura sustituye a la extensa descripción del pipeline que antes vivía aquí. Todo lo relativo a *qué se ejecuta en cada etapa* está ahora en un único sitio.

## Instalación rápida

**Prerrequisitos**

- [Claude Code](https://docs.claude.com/en/docs/claude-code/setup) (última versión; el empaquetado como plugin requiere versiones recientes)
- `ANTHROPIC_API_KEY` exportada, o definida en la primera ejecución de `claude`
- *Opcional:* Pandoc para DOCX, tectonic + Source Han Serif TC para PDF en APA 7.0 (la salida en Markdown funciona sin ninguno de los dos)
- *Opcional (Python real):* Las skills principales (investigación / escritura / revisión) no necesitan Python; están guiadas por prompts. Solo se necesita un **intérprete de Python real** para: la guarda `PreToolUse` de ámbito de escritura (endurecimiento opcional de subagentes; si no encuentra un Python real, se desactiva de forma limpia y la guarda simplemente no actúa; las skills principales no se ven afectadas), más algunas funciones opcionales que invocan Python mediante shell (el modo de parches de revisión, el verificador del paquete de envío y los comandos `/ars-cache-invalidate` / `/ars-mark-read` / `/ars-unmark-read`). En Windows, ten en cuenta que `python3` suele ser un placeholder no funcional de Microsoft Store en lugar de Python real; instala Python desde python.org (o mediante `winget`) para que el lanzador encuentre un intérprete real. El lanzador de la guarda es un script de shell POSIX y `hooks.json` lo invoca a través de `bash`, así que en Windows necesita **Git Bash** (incluido con Git for Windows). Con Git Bash presente, la ausencia de Python real se degrada de forma limpia (la guarda no actúa, en silencio). Sin Git Bash, Claude Code recurre a PowerShell, que no puede ejecutar el lanzador `.sh` en absoluto: la guarda queda inactiva y el hook `PreToolUse` registrará un error en cada llamada en lugar de no hacer nada silenciosamente (degradación aceptada: la guarda es opcional y nunca bloquea tus escrituras, pero el ruido en el log del hook es el coste hasta que instales Git Bash).

> **¿Qué controles están activos en *tu* canal de instalación?** La disponibilidad varía según el canal de instalación. Consulta el mapa por canal: [docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md).

**Instalación como plugin (v3.7.0+, recomendada):**

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

**Comprueba que funciona:** ejecuta `/ars-plan` y describe un artículo en el que estés trabajando; ARS iniciará un diálogo socrático para definir la estructura de los capítulos. Como prueba de un solo disparo, prueba `/ars-lit-review "your topic"`.

**👉 [docs/SETUP.md](docs/SETUP.md)** — guía completa: instalar Claude Code, configurar claves de API, Pandoc/tectonic opcionales para DOCX/PDF, verificación entre modelos (`ARS_CROSS_MODEL`) y seis métodos de instalación (plugin, skills de proyecto, skills globales, claude.ai Project, repositorio clonado e importación en Claude Science).

**👉 [docs/DATA_FLOWS.md](docs/DATA_FLOWS.md)** — qué sale de tu máquina (resolutores bibliográficos, llamadas entre modelos opcionales con consentimiento explícito, la comprobación de actualizaciones del plugin), qué se guarda en caché localmente y durante cuánto tiempo, y cómo desactivar cada camino.

**👉 [docs/RISK_REGISTER.md](docs/RISK_REGISTER.md)** — los riesgos permanentes que el conjunto conoce, qué controles existentes abordan cada uno, cuál es el estado de la evidencia detrás de esos controles y qué queda abierto.

**¿Usas Claude Science?** Las cuatro skills se importan directamente: **Skills → Import from GitHub**, pega `https://github.com/Imbad0202/academic-research-skills`, **Preview** y después **Import 4 skills** (requiere la v3.14.0+ de este repositorio: el importador lee las rutas explícitas de skill en el manifiesto del marketplace). Las importaciones son capturas puntuales; vuelve a importar cuando ARS se actualice. Las skills importadas conservan la metodología de ARS (protocolos de investigación / escritura / revisión); la maquinaria específica de Claude Code —comandos de barra, hooks, orquestación de subagentes— no se transfiere. Consulta [docs/SETUP.md](docs/SETUP.md), Método 5, para más detalle.

**¿Usas Pi?** Instala el wrapper comunitario mantenido dentro del árbol con `pi install git:github.com/Imbad0202/academic-research-skills`. Mantiene el contenido original de ARS como autoritativo y documenta la orquestación específica de Pi y las limitaciones de hooks. Consulta [`pi/README.md`](pi/README.md).

**¿Usas Codex CLI?** Instala en su lugar la distribución hermana: [`Imbad0202/academic-research-skills-codex`](https://github.com/Imbad0202/academic-research-skills-codex) — el mismo contenido de workflow, empaquetado de forma nativa para Codex como una única skill `$academic-research-suite` con alias `ars-*`.

**Plataformas e integraciones de terceros** que envuelven u hospedan ARS están listadas en [THIRD_PARTY.md](THIRD_PARTY.md) — enviadas por la comunidad y no revisadas ni avaladas por quien mantiene el proyecto.

**Gobernanza:** quién decide, qué aporta y qué no aporta la revisión entre modelos, y la postura de fin de vida del proyecto se explican en [GOVERNANCE.md](GOVERNANCE.md); la notificación de problemas de seguridad y su triage, en [SECURITY.md](SECURITY.md).

## Rendimiento y coste

**👉 [docs/PERFORMANCE.md](docs/PERFORMANCE.md)** — presupuestos de tokens por modo, estimación del pipeline completo (unos 4–6 $ por un artículo de 15k palabras) y ajustes recomendados de Claude Code (Auto mode; Agent Team opcional).

## Guías y artículos

- [Academic Writing Shouldn't Be a Solo Act](https://open.substack.com/pub/edwardwu223235/p/academic-writing-shouldnt-be-a-solo?r=4dczl&utm_medium=ios) — recorrido completo del pipeline (en inglés)
- [學術寫作不該是一個人的事：一套開源 AI 協作工具如何改變研究者的工作流](https://open.substack.com/pub/edwardwu223235/p/ai?r=4dczl&utm_medium=ios) — 完整使用指南（繁體中文）

---

## Funciones de un vistazo

- **Deep Research** — equipo de investigación de 13 agentes con modo guiado socrático, revisión sistemática PRISMA, detección de intención, monitorización de la salud del diálogo, DA opcional entre modelos y verificación por API de Semantic Scholar.
- **Academic Paper** — escritura de artículos con 12 agentes, con Style Calibration, Writing Quality Check, endurecimiento de LaTeX, visualización, coaching de revisión, conversión de citas, protocolo anti-fuga y verificación de figuras con VLM.
- **Academic Paper Reviewer** — revisión multiperspectiva con 7 agentes y juicios narrativos atados a criterios y anclados en evidencia (Journal-Fit Reviewer + 3 revisores dinámicos + Devil's Advocate), protocolo de umbral de concesión, preservación de la intensidad de ataque, crítica y calibración opcionales entre modelos, matriz de trazabilidad R&R y restricción de solo lectura. Las revisiones en vivo actuales siguen siendo `NOT_CALIBRATED`; la calibración completa produce un perfil de candidato acotado, pero su aplicación en una revisión en vivo todavía no está conectada.
- **Academic Pipeline** — orquestador de pipeline de 10 etapas con checkpoints adaptativos, verificación de afirmaciones, Material Passport, `repro_lock` opcional, verificación de integridad opcional entre modelos, refuerzo a mitad de conversación y comprobaciones de regresión narrativas criterio a criterio (el portador tipado de trayectorias queda aplazado).
- **Metadatos de nivel de acceso a datos** (v3.3.2+) — cada skill declara `data_access_level` (`raw` / `redacted` / `verified_only`); lo aplica `scripts/check_data_access_level.py`. Patrón adaptado del automated-w2s-researcher de Anthropic (2026). Consulta [`shared/ground_truth_isolation_pattern.md`](shared/ground_truth_isolation_pattern.md).
- **Anotación de tipo de tarea** (v3.3.2+) — cada skill declara `task_type` (`open-ended` o `outcome-gradable`). Todas las skills actuales de ARS son `open-ended`.
- **Esquema de informes de benchmark** (v3.3.5+) — JSON Schema + lint para comparaciones de benchmark honestas. Consulta [`shared/benchmark_report_pattern.md`](shared/benchmark_report_pattern.md).
- **Lockfile de reproducibilidad de artefactos** (v3.3.5+) — sub-bloque `repro_lock` opcional en el Material Passport. **Es documentación de configuración, no una garantía de repetición byte a byte**: las salidas de un LLM no son reproducibles. Consulta [`shared/artifact_reproducibility_pattern.md`](shared/artifact_reproducibility_pattern.md).
- **Jerarquía de modelos** (#517, v3.16+) — interruptor opcional `ARS_MODEL_TIERING` con dos direcciones: `economy` (los agentes de tipo ejecución se despachan un nivel por debajo del modelo de la sesión, con suelo en la clase Opus) y `quality-boost` (los agentes de tipo juicio en las puertas de integridad y en el paso final de revisión suben al nivel frontera). Sin valor definido = comportamiento equivalente byte a byte al previo a #517. Consulta [`shared/model_tiering.md`](shared/model_tiering.md).
- **Sobre canónico de traspaso entre modelos** (#527, v3.17+) — el camino de transporte de checkpoints a ciegas owner→dispatcher→owner (#523) tiene ahora un sobre `[CROSS-MODEL-HANDOFF v1]` estable a máquina, con una gramática Python normativa (`scripts/cross_model_handoff.py`) en lugar de una aplicación solo en prosa, que fija el enrutamiento de acuerdo / divergencia / resultado malformado en los tres propietarios de checkpoint. Consulta [`shared/cross_model_verification.md`](shared/cross_model_verification.md), §«Cross-model handoff envelope».
- **Entrada de procedencia de experimentos** (#260) — el campo opcional `experiment_provenance[]` del Material Passport registra experimentos que el investigador ejecutó **externamente** (ARS nunca ejecuta experimentos), y las afirmaciones del manuscrito se unen a ellos mediante `claim_intent_manifest.planned_experiment_ids[]`. La puerta de integridad (Etapa 2.5/4.5) audita cada afirmación respaldada por experimento contra la procedencia declarada: `ALIGNED` / `OVERSTATED` / `NOT_SUPPORTED_BY_PROVENANCE` / `PROVENANCE_INSUFFICIENT`, **sin juzgar si el experimento en sí fue correcto**. Un `experiment_intake_declaration` fail-closed convierte «¿has ejecutado experimentos?» en una decisión explícita de la Etapa 1 (incluso las ejecuciones solo con literatura declaran `no_experiments_declared`). Consulta [`shared/handoff_schemas.md`](shared/handoff_schemas.md), §«Experiment Provenance Intake (#260)».

**Límite de integridad y verificación:** ARS revisa el manuscrito y el proceso reportado, incluida la existencia de las citas, la alineación afirmación–fuente, la metodología declarada, la alineación experimento–resultado declarada, la fidelidad de figuras y tablas y la conformidad de reporte/proceso/paquete. Algunas comprobaciones se hacen por muestreo o mediante LLM. ARS **no** establece que los procedimientos se hayan ejecutado realmente, que los datos crudos sean auténticos o que los resultados se reproduzcan; una fabricación reportada de forma coherente puede pasar estas comprobaciones. Consulta [POSITIONING.md § Integrity checks and the empirical-work boundary](POSITIONING.md#integrity-checks-and-the-empirical-work-boundary).

---

## Escaparate: salida real del pipeline

Consulta los artefactos completos de una ejecución real del pipeline de 10 etapas: informes de revisión por pares, informes de verificación de integridad y el artículo final.

**[Ver todos los artefactos del pipeline →](examples/showcase/)**

| Artefacto | Descripción |
|---|---|
| [Final Paper (EN)](examples/showcase/full_paper_apa7.pdf) | Formateado en APA 7.0, compilado con LaTeX |
| [Final Paper (ZH)](examples/showcase/full_paper_zh_apa7.pdf) | Versión en chino, APA 7.0 |
| [Integrity Report — Pre-Review](examples/showcase/integrity_report_stage2.5.pdf) | Etapa 2.5: detectó 15 referencias fabricadas + 3 errores estadísticos |
| [Integrity Report — Final](examples/showcase/integrity_report_stage4.5.pdf) | Etapa 4.5: cero regresiones confirmadas |
| [Peer Review Round 1](examples/showcase/stage3_review_report.pdf) | Journal-Fit Reviewer + 3 revisores + Devil's Advocate |
| [Re-Review](examples/showcase/stage3prime_rereview_report.pdf) | Verificación tras las revisiones |
| [Peer Review Round 2](examples/showcase/stage3_review_report_r2.pdf) | Revisión de seguimiento |
| [Response to Reviewers](examples/showcase/response_to_reviewers_r2.pdf) | Respuesta puntual de los autores |
| [Post-Publication Audit Report](examples/showcase/post_publication_audit_2026-03-09.pdf) | Auditoría independiente de todas las referencias: encontró 21 de 68 problemas que se escaparon en 3 rondas de comprobaciones de integridad |

---

## Complemento: Experiment Agent

Si tu investigación implica ejecutar experimentos (código o estudios con personas) antes de escribir, la skill [Experiment Agent](https://github.com/Imbad0202/experiment-agent) cubre el hueco entre la Etapa 1 (RESEARCH) de ARS y la Etapa 2 (WRITE).

```
ARS Stage 1 RESEARCH  →  RQ Brief + Methodology Blueprint
        ↓
  experiment-agent     →  run/manage experiments → validate results
        ↓
ARS Stage 2 WRITE     →  write paper with verified experiment results
```

**Qué hace**: ejecuta experimentos con código (Python, R, etc.) con monitorización en tiempo real, gestiona protocolos de estudios con personas mediante la lista de verificación ética IRB, interpreta estadística con detección de 11 tipos de falacia y verifica la reproducibilidad.

**Cómo usarlos juntos**: pausa el pipeline de ARS después de la Etapa 1, ejecuta los experimentos en una sesión aparte de experiment-agent y devuelve los resultados (con el Material Passport) a la Etapa 2 de ARS. ARS no requiere ninguna modificación. Consulta el [README de experiment-agent](https://github.com/Imbad0202/experiment-agent) para las instrucciones de configuración.

**Declaración de entrada en la Etapa 1 (#260)**: en la Etapa 1, ARS detecta si la ejecución llevará afirmaciones respaldadas por experimentos y fija un `experiment_intake_declaration` fail-closed en el Material Passport. Si ejecutaste experimentos externamente, el investigador introduce una entrada `experiment_provenance[]` por experimento (`experiment_id`, `repro_lock` anidado, `planned_vs_executed[]`, `negative_results[]`, `known_limitations[]`) y la declaración queda en `experiments_declared`; si no, queda en `no_experiments_declared`. La declaración es **obligatoria en todo passport posterior a #260**: una ejecución que no toca experimentos también declara `no_experiments_declared`, de modo que la puerta de integridad nunca puede saltarse en silencio por un bloque de procedencia olvidado. Los `experiment_id` se congelan en este punto de entrada; más adelante, los agentes de escritura los referencian mediante `planned_experiment_ids[]`.

**Complemento del lado docente**: [Teaching Skills](https://github.com/YujxZJCN/teaching-skills) aplica la arquitectura de ARS (conjuntos de skills, contratos compartidos, puertas por fases, un Course Passport) al lado docente de la vida académica: diseño de cursos → lecciones → evaluación → impartición → reflexión; su modo `sotl` entrega los proyectos de investigación sobre el aula a ARS deep-research / academic-paper para la fase de publicación.

---

## Uso

### Inicio rápido

```
# Start a full research pipeline
You: "I want to write a research paper on AI's impact on higher education QA"

# Start with Socratic guidance
You: "Guide my research on AI in educational evaluation"

# Write a paper with guided planning
You: "Guide me through writing a paper on demographic decline"

# Review an existing paper
You: "Review this paper" (then provide the paper)

# Check pipeline status
You: "status"
```

### Skills individuales

#### Deep Research (8 modos)

```
"Research the impact of AI on higher education"       → full mode
"Give me a quick brief on X"                          → quick mode
"Do a systematic review on X with PRISMA"             → systematic-review mode
"Guide my research on X"                              → socratic mode (guided)
"Fact-check these claims"                             → fact-check mode
"Do a literature review on X"                         → lit-review mode
"Compare these papers in WHY/HOW/WHAT format"         → three-way-scan mode
"Review this paper's research quality"                → review mode
```

#### Academic Paper (11 modos)

```
"Write a paper on X"                                  → full mode
"Guide me through writing a paper"                    → plan mode (guided)
"Build a paper outline"                               → outline-only mode
"I have a draft, here are reviewer comments"          → revision mode
"Parse these reviewer comments into a roadmap"        → revision-coach mode
"Write an abstract for this paper"                    → abstract-only mode
"Turn this into a literature review paper"            → lit-review mode
"Convert to LaTeX" / "Convert citations to IEEE"      → format-convert mode
"Check citations"                                     → citation-check mode
"Generate an AI disclosure statement for NeurIPS"     → disclosure mode
"Audit my rebuttal draft against the reviews"         → rebuttal-audit mode
```

#### Academic Paper Reviewer (6 modos)

```
"Review this paper"                                   → full mode (Journal-Fit Reviewer + R1/R2/R3 + Devil's Advocate)
"Quick assessment of this paper"                      → quick mode
"Guide me to improve this paper"                      → guided mode
"Check the methodology"                               → methodology-focus mode
"Verify the revisions"                                → re-review mode
"Calibrate this reviewer against my gold set"         → calibration mode
```

#### Academic Pipeline (orquestador)

```
"I want to write a complete research paper"           → full pipeline from Stage 1
"I already have a paper, review it"                   → mid-entry at Stage 2.5 (integrity first)
"I received reviewer comments"                        → mid-entry at Stage 4
```

> El pipeline termina con la **Etapa 6: Process Summary**, que genera automáticamente un registro del proceso de creación del artículo con una evaluación de calidad de la colaboración en 6 dimensiones (puntuación 1–100).

### Idiomas soportados

- **Chino tradicional** (繁體中文) — valor por defecto cuando el usuario escribe en chino
- **Inglés** — valor por defecto cuando el usuario escribe en inglés
- Resúmenes bilingües (chino + inglés) para artículos académicos

> **¿Usas otro idioma?** El modo Socratic (deep-research) y el modo Plan (academic-paper) usan **activación por intención**: detectan el significado de tu solicitud, no palabras clave concretas. Por eso funcionan en **cualquier idioma** sin modificar nada.
>
> Sin embargo, la sección general `Trigger Keywords` (la que decide si la skill se activa o no) sigue listando palabras clave en inglés y en chino tradicional. Si ves que la skill no se activa de forma fiable en tu idioma, puedes añadir las palabras clave de tu idioma a la sección `### Trigger Keywords` de cada archivo `SKILL.md` para mejorar la confianza de la coincidencia.

### Formatos de cita soportados

- APA 7.0 (por defecto, incluidas las reglas de cita en chino)
- Chicago (Notas y Autor-Fecha)
- MLA
- IEEE
- Vancouver

### Estructuras de artículo soportadas

- IMRaD (investigación empírica)
- Revisión bibliográfica temática
- Análisis teórico
- Estudio de caso
- Policy brief
- Artículo de congreso

---

## Detalle de las skills

Las responsabilidades por agente y los artefactos por etapa viven ahora en [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Los números de versión quedan anclados aquí para que los metadatos de cada release estén en un solo sitio.

### Deep Research (v2.12.1)

Equipo de investigación de 13 agentes. Modos: full, quick, review, lit-review, three-way-scan, fact-check, socratic, systematic-review. Roster completo de agentes y artefactos: consulta ARCHITECTURE.md §3.

### Academic Paper (v3.3.1)

Pipeline de escritura de artículos con 12 agentes. Modos: full, plan, outline-only, revision, revision-coach, abstract-only, lit-review, format-convert, citation-check, disclosure, rebuttal-audit. Salida: MD + DOCX (mediante Pandoc cuando está disponible) + LaTeX (clase `apa7` de APA 7.0 / IEEE / Chicago) → PDF vía tectonic. Roster completo de agentes y responsabilidades por fase: consulta ARCHITECTURE.md §3.

### Academic Paper Reviewer (v1.11.1)

Revisión multiperspectiva con 7 agentes y **juicios narrativos atados a criterios**. Modos: full, re-review, quick, methodology-focus, guided, calibration. Las revisiones en vivo actuales y los paquetes Schema 6 siguen siendo `NOT_CALIBRATED`; la calibración completa puede producir un perfil de candidato acotado, pero su aplicación a una revisión en vivo no está conectada. Ninguna puntuación total se mapea a Accept, Minor Revision, Major Revision o Reject. La frontera entre el panel de la primera ronda y el despacho de re-review regido por contrato está en ARCHITECTURE.md §3, Stage 3 / Stage 3'.

### Academic Pipeline (v3.21.2)

Orquestador de 10 etapas con verificación de integridad, revisión en dos fases, coaching socrático y evaluación de la colaboración. Garantías del pipeline: cada etapa requiere un checkpoint de confirmación del usuario; la verificación de integridad (Etapa 2.5 + 4.5) es OBLIGATORIA y sin bypass no registrado (toda excepción requiere que quede registrada la justificación del usuario para la Etapa 6); la Matriz de Trazabilidad R&R (Schema 11) verifica de forma independiente las afirmaciones de revisión de los autores. v3.4 añadió el Compliance Agent (PRISMA-trAIce + RAISE) en las Etapas 2.5 / 4.5. v3.5 añade el **Collaboration Depth Observer** (`collaboration_depth_agent`, solo advisory, nunca bloquea) en cada checkpoint FULL/SLIM y al completar el pipeline. Las puertas de integridad OBLIGATORIAS (2.5 / 4.5) saltan explícitamente el observador para que las comprobaciones de cumplimiento no queden diluidas. Basado en Wang & Zhang (2026), IJETHE 23:11. Matriz etapa por etapa con agentes, artefactos y puertas: consulta ARCHITECTURE.md §3.

---

## Optimizaciones de v3.0: lo que descubrimos sobre los límites estructurales de la IA

### Qué pasó

Mientras usaba ARS para escribir un artículo de reflexión sobre la IA en la educación superior, me encontré con tres problemas estructurales que ninguna cantidad de prompt engineering arreglaba:

1. **Frame-lock**: pedí a la IA que ejecutara un debate de devil's advocate contra su propia tesis. Lo hizo: cuatro rondas, cada una más refinada que la anterior. Pero cada ronda se quedó dentro del marco que yo había definido. El DA atacaba argumentos, nunca premisas. Nunca preguntó «¿estamos discutiendo la pregunta correcta?». Es el mismo patrón que causó la tasa de error del 31 % en citas en la prueba de estrés de v2.7: la IA que verifica y la IA que generan comparten el mismo marco cognitivo.

2. **Sycophancy bajo presión**: cada vez que cuestionaba los ataques del DA, este cedía demasiado rápido. Retiraba hallazgos más deprisa de lo que los lanzaba. El entrenamiento del modelo premia la armonía conversacional, así que «el usuario ha replicado» se trataba como evidencia de que el ataque era equivocado, cuando muchas veces solo significaba que el usuario era persistente.

3. **Detección errónea de intención**: el Socratic Mentor intentaba constantemente converger y producir entregables («¿quieres que lo escriba?») cuando yo todavía estaba explorando. No distinguía «el usuario quiere una discusión filosófica profunda» de «el usuario quiere un brief de pregunta de investigación». Ambos parecen implicación, pero requieren comportamientos opuestos de la IA.

### Qué cambiamos (v3.0)

**Devil's Advocate — Protocolo de umbral de concesión** (`deep-research` + `academic-paper-reviewer`)
- El DA ahora debe puntuar cada réplica en una escala del 1 al 5 antes de responder
- La concesión solo se permite con puntuación ≥4 (la réplica aborda directamente el ataque central con evidencia)
- Puntuación ≤3: mantener la posición y reformular el ataque original
- Reglas anti-sycophancy: sin concesiones consecutivas, seguimiento de la tasa de concesión y detección de frame-lock después de cada checkpoint

**Socratic Mentor — Capa de detección de intención** (`deep-research`)
- Clasifica la intención del usuario como exploratoria o orientada a un objetivo al inicio del diálogo y cada 3 turnos
- Modo exploratorio: desactiva la auto-convergencia, sube el máximo de rondas a 60 y prohíbe preguntas del tipo «¿quieres que lo resuma?»
- Modo orientado a objetivo: comportamiento de convergencia estándar
- Reglas de anti-cierre-prematuro: en modo exploratorio, es el usuario quien decide cuándo parar

**Socratic Mentor — Indicador de salud del diálogo** (`deep-research`)
- Autoevaluación silenciosa cada 5 turnos en tres dimensiones: acuerdo persistente, evitación del conflicto y convergencia prematura
- Inyecta preguntas desafiantes automáticamente cuando detecta un patrón de acuerdo
- Invisible para el usuario (para evitar que se manipule), pero el log queda disponible para revisarlo después de la sesión

### Por qué importa

Estas optimizaciones no resuelven los límites estructurales de la IA: hacen que esos límites sean visibles y manejables. El DA seguirá acabando por ceder si se le empuja lo suficiente. El Socratic Mentor seguirá teniendo cierto sesgo de convergencia. Pero ahora hay checkpoints explícitos que frenan la sycophancy, obligan al DA a justificar sus concesiones e impiden que el Mentor cierre antes de que el usuario esté listo.

La lección más profunda: la alfabetización en IA no consiste en aprender a usar la IA como herramienta, seguir reglas de ética o temer a los riesgos de la IA. Consiste en relacionarse con la IA con la suficiente profundidad como para descubrir tú mismo sus límites estructurales, y en el proceso los tuyos propios.

---

## Licencia

Este trabajo está publicado bajo [CC-BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

**Eres libre de:**
- Compartir — copiar y redistribuir el material
- Adaptar — remezclar, transformar y crear a partir del material

**Bajo las siguientes condiciones:**
- **Atribución** — debes reconocer adecuadamente la autoría
- **NoComercial** — no puedes usar el material con fines comerciales

**Formato de atribución:**
```
Based on Academic Research Skills by Cheng-I Wu
https://github.com/Imbad0202/academic-research-skills
```

---

## Contribuyentes

**Cheng-I Wu** (吳政宜) — Autor y mantenedor

**[aspi6246](https://github.com/aspi6246)** — Contribuyente. La optimización de v3.1 se inspiró en patrones de [Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics): patrón de restricción de solo lectura, codificación de anti-patrones como elemento de diseño de primera clase, enfoque de marcos cognitivos (enseñar «cómo pensar» y no solo procedimientos) y filosofía de skills ligeras.

**[mchesbro1](https://github.com/mchesbro1)** — Contribuyente. Propuso y redactó originalmente la IS Basket of 8 journals para `academic-paper-reviewer/references/top_journals_by_field.md` ([Issue #5](https://github.com/Imbad0202/academic-research-skills/issues/5)).

**[cloudenochcsis](https://github.com/cloudenochcsis)** — Contribuyente. Amplió la sección de IS de la *Basket of 8* al completo *Senior Scholars' Basket of 11*, añadiendo *Decision Support Systems*, *Information & Management* e *Information and Organization* ([Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7), [PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8)). Procedente de la [AIS Senior Scholars' List of Premier Journals](https://aisnet.org/research/seniorscholarsbasket/).

**[eltociear](https://github.com/eltociear)** (Ikko Eltociear Ashimine) — Contribuyente. Tradujo el README al japonés ([`README.ja-JP.md`](README.ja-JP.md)) ([PR #161](https://github.com/Imbad0202/academic-research-skills/pull/161)).

**[xpfo-go](https://github.com/xpfo-go)** (xpfo) — Contribuyente. Tradujo el README al chino simplificado ([`README.zh-CN.md`](README.zh-CN.md)) ([PR #181](https://github.com/Imbad0202/academic-research-skills/pull/181)).

**[devCharlotte](https://github.com/devCharlotte)** — Contribuyente. Tradujo el README al coreano ([`README.ko-KR.md`](README.ko-KR.md)) ([PR #469](https://github.com/Imbad0202/academic-research-skills/pull/469)).

**[Yaobin29](https://github.com/Yaobin29)** — Contribuyente. Propuso herramientas de respuesta a revisores en [PR #433](https://github.com/Imbad0202/academic-research-skills/pull/433); el modo `three-way-scan` de `deep-research` y el modo `rebuttal-audit` de `academic-paper` (rescatados del concepto `audit` de ese PR) se integraron a partir de esa contribución en v3.12.1.

**[ktao732084-arch](https://github.com/ktao732084-arch)** — Contribuyente. Amplió el sistema de disclosure de `academic-paper` con nueve destinos de política de publicaciones médicas, recogida de hechos obligatorios específica por destino y renderizado standalone fail-closed ([Issue #596](https://github.com/Imbad0202/academic-research-skills/issues/596), [PR #599](https://github.com/Imbad0202/academic-research-skills/pull/599)); amplió la referencia de reporte clínico EQUATOR con guías condensadas de CARE, STARD y TRIPOD+AI más una secuencia de ruteo por diseño de estudio fail-closed ([Issue #594](https://github.com/Imbad0202/academic-research-skills/issues/594), [PR #601](https://github.com/Imbad0202/academic-research-skills/pull/601)); y diseñó y aportó el resolutor standalone de literatura en chino, su protocolo de API y el conjunto de fixtures de transporte sintéticas ([Issue #595](https://github.com/Imbad0202/academic-research-skills/issues/595), [PR #600](https://github.com/Imbad0202/academic-research-skills/pull/600)).

---

## Registro de cambios

### v3.21.2 (2026-09-06) — Actualización de modelos a Fable 5.1 y GPT-6 Astra, procedencia de las decisiones en checkpoints y reparaciones de coincidencia de títulos CJK

> **Actualidad y procedencia, no capacidad nueva:** v3.21.2 alinea el conjunto con las dos system cards de vendor de septiembre de 2026. `gpt-6-astra` entra en la tabla de modelos cruzados como provisional en ambos transportes y pasa a ser el verificador de OpenAI recomendado según la política de actualidad de generación; `gpt-5.6-sol` conserva su estado validated en el transporte de citas con suscripción a ChatGPT, y no se reclama ningún resultado nuevo de bakeoff. El conjunto de reasoning-effort del transporte Codex contenido gana `ultra`. Se añaden dos salvaguardas, ambas a nivel de prompt y motivadas por el vendor y no por mediciones de ARS: la procedencia de las decisiones en checkpoint (solo un turno de usuario es una decisión; las decisiones se retransmiten a los subagentes literalmente; riesgo R11) y la monitorización del proveedor o las intervenciones de seguridad del proveedor, que se nombran como fallo del transporte y nunca como veredicto. La auditoría de retirada de harness contra ambas cards no retira nada (0 retiradas de texto de prompt; 8 elementos keep-as-debt pasan a llevar cita de la card). Correcciones: los títulos CJK ya no fallan la puerta de título exacto en los cuatro resolutores de índices (#798) y las marcas de envoltorio se eliminan solo como una unidad balanceada (#800); el test de ida y vuelta de autolinks declara su dependencia (#801); `check_surface_form_parity` señala un entorno roto en lugar del manifiesto; un lint de paridad del inventario de skills (#809); la brecha residual R10 se actualiza (#813); y se corrige una línea de reglas clave de MLA (#805). Suite/pipeline → v3.21.2; deep-research → v2.12.1; academic-paper → v3.3.1; academic-paper-reviewer → v1.11.1.

### v3.21.1 (2026-08-24) — Sustratos de workflow acotados, bakeoffs sellados y endurecimiento del transporte

> **Medido donde se indica; en otro caso, acotado:** v3.21.1 repara el transporte de citas con suscripción a ChatGPT contenido para codex-cli 0.147.0 y registra el primer Promotion Bakeoff: `gpt-5.6-sol` queda validado solo para ese transporte de suscripción y sigue siendo provisional en la ruta de API first-party. Los futuros bakeoffs requieren preregistro sellado. El release añade además un sustrato de perfil de workflow de investigación desactivado por defecto (solo conformidad determinista sin conexión; sin hook en el pipeline ni perfiles publicados por familia), un alpha de opt-in inquiry-ledger (`ARS_INQUIRY_LEDGER=1`) y un registro de alternativas solo de diseño que no está implementado. Su evidencia conductual sigue siendo `NOT_RUN`; no se reclama ningún beneficio en usabilidad, recuperación, novedad, corrección ni resultados de investigación. El registro de criterios de revisión gana un conjunto probatorio ilustrativo de perfil exacto para MSR 2027, respaldado por la fuente: no es cobertura de venues ni de disciplinas, ni una atestación de autores reales, ni evidencia de revisión constructiva, y la evaluación humana independiente obligatoria que lo acompaña sigue pendiente. Los cambios adicionales alinean `data_access_level`, consolidan la gramática del lint de markdown, registran las degradaciones del lanzador de la guarda y listan OrcaRouter como integración comunitaria sin aval. Suite/pipeline → v3.21.1; deep-research → v2.12.1; academic-paper → v3.3.1; academic-paper-reviewer → v1.11.1.

### v3.21.0 (2026-08-18) — Transparencia, verificabilidad y pista de viabilidad al estilo ISO/IEC 42001

> **Transparencia que puedes comprobar:** v3.21.0 completa la pista de auditoría al estilo ISO/IEC 42001 (#753–#760). Las afirmaciones hacia fuera se alinean con el registro de evidencia, y cuatro artefactos permanentes responden ahora a las preguntas que de verdad hacen los usuarios: qué controles operan en tu canal de instalación (`docs/CONTROL_AVAILABILITY.md`), qué sale de tu máquina y qué se almacena (`docs/DATA_FLOWS.md`), con qué fuerza aplica realmente cada workflow de CI (`docs/ARCHITECTURE.md` §7.1) y a qué riesgo responde cada mecanismo, con qué evidencia y qué brecha residual (`docs/RISK_REGISTER.md`); cada uno defendido por su propio lint de CI. `GOVERNANCE.md` explicita la autoridad de decisión, qué aporta y qué no aporta la revisión entre modelos (un control de detección de errores, no independencia organizativa) y la postura de fin de vida; `SECURITY.md` gana un procedimiento de triage por severidad ejecutable por una sola persona. Son principios operativos destilados con anclas informativas a ISO/IEC 42001, no una reclamación de certificación, y no se reclaman cifras nuevas de eficacia. Suite/pipeline → v3.21.0; deep-research → v2.12.1; academic-paper → v3.3.1; academic-paper-reviewer → v1.11.1.

### v3.20.1 (2026-08-15) — Endurecimiento de la honestidad contractual y sustratos de evaluación acotados

> **Endurecido y acotado:** v3.20.1 ajusta las afirmaciones de revisión e integridad a la evidencia que el conjunto puede reproducir de verdad. La cobertura de afirmaciones queda acotada a la población, con la completitud semántica sin resolver; los cambios de fuerza de afirmación en revisiones requieren disposiciones explícitas de autor ligadas a bytes; las nuevas atestaciones de lectura exigen ámbito y fallan de forma visible; los paquetes de revisor en vivo siguen en `NOT_CALIBRATED`; y la procedencia en seis ejes sustituye el lenguaje binario de independencia. También publica el sustrato de sonda de sostén de afirmaciones, offline y sin medir, y una puerta de asignación cerrada de primera ronda para el paquete de diversidad de ideación, más una hoja de ruta opcional para ramas de indagación y alternativas futuras. Estos contratos no establecen mejores resultados científicos, ni mayor corrección del revisor, ni detección semántica completa, ni identidad humana autenticada, ni procesos de error independientes, ni eficacia real del proveedor. Suite/pipeline → v3.20.1; deep-research → v2.12.1; academic-paper → v3.3.1; academic-paper-reviewer → v1.11.1.

### v3.20.0 (2026-08-14) — Revisión y enmiendas ligadas a la evidencia, transportes contenidos, sustratos de evaluación herméticos

> **Añadido y endurecido:** v3.20.0 refuerza los límites de evidencia y autoridad en los flujos de revisión por pares, enmiendas, citas, estudios con participantes humanos y envío. Añade filas de evidencia ligadas a la fuente, hojas de ruta de revisión no graduadas y controladas por el autor, advertencias de consistencia y de cobertura de contenido ligadas a la reproducción, criterios de revisión unificados, trazas de autoridad y de ruta para estudios con participantes humanos, artefactos deterministas de envío y correspondencia, observabilidad opcional de adjudicación posterior a la ejecución, un transporte de citas con suscripción a ChatGPT contenido, un registro offline de candidatos al sostén de afirmaciones y una asesoría opcional de texto/OCR de PDF con aislamiento de procesos. Los contratos de revisor y de re-revisión ganan puntuación con alcance por rol, puertas de evidencia-antes-de-persuasión y un manejo más estricto de procedencia y transporte; también se amplían el reporte clínico, la resolución de literatura en chino, los alias de plugin, Pi y la guía de plataformas. Los nuevos assets de evaluación incluyen fixtures herméticas congeladas y sobres sin llamadas para deriva de revisión, topología de roles, diversidad de ideación, inyección indirecta de prompt y detección de frases forzadas. Salvo que `CHANGELOG.md` cite explícitamente una cohorte medida y conservada, se trata de artefactos de protocolo o de conformidad sintética/offline, no de evidencia de seguridad, eficacia, exactitud o mejora conductual. Suite/pipeline → v3.20.0; deep-research → v2.12.0; academic-paper → v3.3.0; academic-paper-reviewer → v1.11.0.

### v3.19.0 (2026-07-22) — Guards de deriva de afirmaciones entre rondas de revisión, preflight de integridad de lectura de PDF y atestación de ámbito de lectura

> **Añadido:** tres capas de integridad advisory u opt-in más una corrección del lanzador. **Guards de deriva de afirmaciones entre rondas de revisión (#569/#570):** una escalera de fuerza de afirmación («ningún desplazamiento silencioso por `is associated with < predicts < causes` sin un elemento de hoja de ruta que lo autorice») conectada al borrado de revisiones y a una nueva Fase E6 advisory, junto con un comprobador determinista de conservación de tokens numéricos y de citas; en conjunto vigilan las mitades epistémica y de tokens del residuo honest-claim de #390 (el interior de un bloque modificado no tenía ninguna comprobación de fidelidad; si los guards reducen la deriva medida queda pendiente de la re-medición de #652). La línea base se midió primero con el modelo frontera actual (`evals/heldout/revision_claim_drift/`), y la forma del mecanismo se acredita a [Yila-AI/sci-ssci-skills](https://github.com/Yila-AI/sci-ssci-skills). **Preflight de integridad de lectura de PDF (#512):** una comprobación cruzada de número de páginas con tres señales para que una lectura de PDF truncada o mal paginada no pueda generar un ancla `page` aparentemente válida. **Atestación `read_scope` (#513):** una declaración opcional de cobertura honesta en el registro de lecturas humanas (`full_text` / `sections` / `abstract_only` / `toc_only`) que hace que la promoción de citas del finalizador tenga en cuenta el ámbito de lectura. **Corrección del watchdog del lanzador (#545):** elimina un estancamiento de tubería que bloqueaba todas las llamadas sanas de la guarda PreToolUse de ámbito de escritura durante todo el límite de tiempo real. Suite → v3.19.0; las tres versiones de skills subyacentes no cambian.

### v3.18.0 (2026-07-18) — Integración del survey de auto-mejora: capas de calidad advisory, puerta de afirmaciones por riesgo y pistas de revisor y juez entre modelos

> **Añadido:** ocho mecanismos de calidad motivados por Ren et al. (2026, arXiv:2607.13104, *Self-Improvements in Modern Agentic Systems: A Survey*): vinculaciones de ámbito por sub-pregunta más una asesoría de conformidad de ámbito en la Fase E (#547), y afirmaciones de novedad acotadas por la búsqueda más una clasificación de novedad E5 (#548); ambas solo advisory, mostradas fila a fila en los checkpoints de integridad OBLIGATORIOS. Verificación de afirmaciones en la Etapa 2.5 estratificada por riesgo (100 % de las afirmaciones HIGH-IMPACT más un centinela aleatorio, extendiendo los niveles de referencia de #518 al nivel de afirmación, #549); cache-through conectado a la puerta de verificación de citas con una asesoría de caducidad por antigüedad y revalidación en vivo opcional (#541, que cierra la promesa pendiente Delta-2 de v3.11); una pista de revisor entre modelos con consentimiento, una de las cinco plazas fijas del panel en la segunda familia de modelos (#540), e independencia del juez en la re-revisión con un Judge Record transparente (#539); un conjunto de semillas de evaluación de robustez de enrutamiento y puertas metamórfico (#550), que además publicó los alias de triggers zh-TW que le faltaban a la skill del revisor; y el propio survey como tercera ancla bibliográfica del humano en el bucle (#542). Independientemente de la pista del survey, las instalaciones como plugin ganan también el recordatorio SessionStart de actualización disponible de #544 (anuncia `/plugin update` cuando vas por detrás; interruptor `ARS_UPDATE_CHECK=0`). `academic-pipeline` sigue a la suite en v3.18.0; las otras tres versiones de skill no cambian.

### v3.17.0 (2026-07-16) — Semántica de los límites del pipeline, sobre canónico de traspaso entre modelos y comprobador ejecutable de paneles

> **Corregido:** dos límites del pipeline poco especificados se cierran (#528). La regla de la Etapa 5 «antes de finalizar: siempre OBLIGATORIO» nombra ahora exactamente un checkpoint (la puerta de entrada entre el PASS de la Etapa 4.5 y el despacho de la Etapa 5), y la Etapa 6 gana un vocabulario definido de confirmación terminal (`finish`/`end`/`done`/`confirm`) más una ruta explícita de rechazo. Las cinco superficies del pipeline llevan bloqueos de contenido sha256 de archivo completo (#529), de modo que cualquier deriva adicional en la superficie de prompt falla en CI hasta que el hash se actualice en el mismo commit. El transporte de checkpoints a ciegas se mueve a la capa de despacho (#523): a los propietarios de checkpoints del Bucket A se les pedía ejecutar ellos mismos el transporte entre modelos, algo que no se puede ejecutar con Bash prohibido en el runtime; ahora la capa de despacho es la dueña de la llamada de transporte. **Añadido:** un sobre canónico `[CROSS-MODEL-HANDOFF v1]` con una gramática Python normativa (#527) sustituye la aplicación solo en prosa del camino de transporte owner→dispatcher→owner, y fija el enrutamiento de acuerdo / divergencia / resultado malformado en los tres propietarios de checkpoint. Un candado anti-deriva para la lista blanca de herramientas de #514 (#524, 74 mutaciones de prueba) cierra la ruta de deriva en la que una edición simétrica de un agente y su espejo podía volver a añadir Bash en silencio. Un comprobador ejecutable de contratos de sprint (#510) recalcula las dos capas de decisión de v3.6.2 desde los artefactos primarios y detecta un error de transcripción en la fórmula de mayoría. Un registro de degradación legible por máquina (#511 Parte A) indexa cada mecanismo de degradación elegante del conjunto, junto con un test de integración de fixtures de transporte hermético para la puerta de verificación de citas (#511 Parte B) que ejercita los cuatro clientes de resolutores de extremo a extremo contra cuerpos de API sintéticos versionados. `academic-pipeline` sigue a la suite en v3.17.0; las otras tres versiones de skill no cambian.

### v3.16.0 (2026-07-12) — Jerarquía de modelos, endurecimiento de la puerta entre modelos y precisión del asesor WP

> **Añadido:** jerarquía de modelos opcional (#517): un nuevo interruptor `ARS_MODEL_TIERING` con dos direcciones (`economy` despacha los 13 agentes de tipo ejecución un nivel por debajo del modelo de la sesión, con suelo en la clase Opus; `quality-boost` sube los agentes de tipo juicio en las puertas de integridad y en las superficies de revisión final al nivel frontera); sin valor definido se mantiene byte-equivalente al comportamiento previo, con la clasificación congelada de 39 agentes fijada por un nuevo manifiesto y un lint. Endurecimiento de la puerta entre modelos (#518): muestreo de verificación estratificado por riesgo (las referencias HIGH-IMPACT se verifican al 100 % en ambas puertas), checkpoints ciegos de desacuerdo en las dos decisiones irreversibles (congelación del diseño y decisión editorial final), una lista blanca de estado id para los identificadores de modelos verificadores y un protocolo de bakeoff de promoción; el revisor genérico número 6 que en su día se planificó se retira, no se aplaza. GPT-5.6 Sol se lista como verificador entre modelos provisional con control explícito del reasoning-effort (#515). Palabras clave de trigger en coreano y fixtures del límite de enrutamiento aportadas por devCharlotte (#452/#509). Una referencia de retórica de introducción CARS y de construcción de títulos para el redactor del artículo (#500). **Cambiado:** la asesoría de pregunta de investigación del WP se generaliza más allá de su tabla de 20 plantillas mediante la prueba de sustantivo de intercambio (#501), y una cláusula de exención más afinada detecta las plantillas de título decoradas (#505): tasa de fallo en el conjunto reservado 0,34–0,38 → 0,094, manteniendo 0/16 falsos disparos; el protocolo de calibración del revisor documenta ahora la dirección de indulgencia del juicio LLM-as-judge (ancla FARS, #484); autenticación con API key de OpenAlex, manejo de 429 consciente del presupuesto y backoff alineado con los ToU de arXiv (#495/#496). **Docs:** directorio comunitario THIRD_PARTY.md (#497/#498). `academic-pipeline` sigue a la suite en v3.16.0; las otras tres versiones de skill no cambian.

### v3.15.0 (2026-07-04) — Endurecimiento de las puertas de release, segunda ronda de retirada de deuda de prompts y candados anti-deriva

> Un release de disciplina e higiene; ningún cambio de comportamiento de las skills. **Añadido:** tres puertas de CI: la comprobación previa al tag de que el CHANGELOG cubre los merges (#483), los invariantes de consistencia de versión 9-11 más una re-ejecución en el momento del tag (#487) y una puerta de invariantes de comandos que fija la lista del anuncio SessionStart al inventario real de 16 comandos (#486). Dos candados anti-deriva: la frase de aplicación de la Frontera de Fase queda fijada literalmente en los 23 bloques de agentes del Bucket A, y los ejemplos de modelos cruzados de SETUP quedan anclados entre sí y a las tablas canónicas de modelos (#491 → #492). **Cambiado:** la segunda ronda de retirada de deuda de prompts examina a fondo los 17 agentes que la primera pasada aplazó (#489 → #490): se corrigen dos autocontradicciones vivas en ambos socratic_mentor (reglas obsoletas de abandono a los 15 rondas frente a la ejecución típica documentada de 20-30 rondas), se corrige la frase obsoleta de estado de aplicación en 29 superficies de todo el repositorio y se recortan andamios few-shot y de procesos duplicados en 7 agentes; verificado con una auditoría paralela en 4 lotes y un challenge independiente entre modelos con codex. El informe de auditoría queda en `audits/`. **Corregido:** la insignia de DOI servida desde shields.io (#482). `academic-pipeline` sigue a la suite en v3.15.0; las otras tres versiones de skill no cambian.

### v3.14.0 (2026-07-02) — Importable desde Claude Science, renderizado de comentarios de eval y retirada de deuda de prompts

> Un release de portabilidad y pulido; ningún cambio de comportamiento de las skills. **Añadido:** posibilidad de importar desde Claude Science: el manifiesto del marketplace declara rutas explícitas de skills, de modo que los importadores basados en la API de GitHub que no pueden recorrer el directorio `skills/` enlazado (Claude Science «Import from GitHub», checkouts en Windows) encuentran ahora las cuatro skills; verificado de extremo a extremo en Claude Science, con una guía de importación en README y SETUP (#480). Los comentarios de PR del harness de evaluación se renderizan como un veredicto en una línea más una tabla por tarea, con el JSON crudo plegado en `<details>`, sustituyendo el volcado del informe crudo; solo cambia la capa de visualización, la lógica de la puerta es byte-idéntica (#479). **Cambiado:** tras la auditoría de retirada de harness de 2026-07 se retiran andamios de escritura vencidos de cuatro agentes de la familia de escritura (#476/#477 → #478, neto −111 líneas de prompt); un Platform Port Reminder que avisa pero no bloquea muestra la política de portabilidad entre plataformas cuando un PR añade un directorio nuevo de nivel superior (#473). **Docs:** README en coreano revisado por hablantes nativos, de devCharlotte (#469/#471); instrucciones del repositorio para GitHub Copilot (#465); se recomienda el modo de permisos auto frente a Skip Permissions (#464). El acumulado de `[Unreleased]` (16 entradas cuyo código se publicó antes del tag v3.13.0: modo de revisión por diff/patch #390, verificador del paquete de envío #394, gold sets de evaluación #215/#216 y más) pasa al registro versionado; consulta `CHANGELOG.md`. `academic-pipeline` sigue a la suite en v3.14.0; las otras tres versiones de skill no cambian.

### v3.13.0 (2026-06-18) — Portabilidad de los hooks, verificación agnóstica de proveedor y corrección de la guarda

> Un release menor que endurece la superficie de instalación y ejecución y amplía el alcance de la verificación entre modelos. **Corregido:** la guarda de ámbito de escritura ya no deniega por error el `CLAUDE.md` del propio usuario con el esquema de instalación por clonación y enlaces simbólicos (#459, que cierra la mitad residual de #448/#449: `CLAUDE.md` es documentación, no un archivo de aplicación cargado de peso, así que sale de la lista de infraestructura protegida mientras todos los archivos load-bearing siguen protegidos); portabilidad de los hooks de Python en Windows y degradación elegante sin Python mediante un lanzador multiplataforma `hooks/run_guard.sh` que rechaza el stub de 0 bytes `python3` de Microsoft Store y no satura el log de hooks (#454); la unión estática de las dos fases de `draft_writer` queda documentada y el emparejamiento de rutas en Windows es seguro con POSIX (#451). **Añadido:** verificación entre modelos agnóstica de proveedor que acepta endpoints compatibles con OpenAI (MiMo, DeepSeek, autoalojados) junto con OpenAI first-party con fundamento, que nunca se degrada en silencio (#455); una sonda socrática de encuadres adyacentes opcional (expansión de perspectivas tomada de STORM, `ARS_SOCRATIC_ADJACENT_PROBE=1`, desactivada por defecto, solo en la capa de prosa; `deep-research` 2.10.0 → 2.11.0) (#461). `academic-pipeline` sigue a la suite en v3.13.0; `academic-paper` y `academic-paper-reviewer` no cambian. Consulta `CHANGELOG.md` para el detalle por issue.

### v3.12.1 (2026-06-15) — Modos de triage de respuestas a revisores (integración de la PR #433)

> Un release parche que incorpora a las skills existentes, como modos, las partes genuinamente novedosas de una contribución externa, conforme a la arquitectura modal de ARS. **Nuevos modos:** `three-way-scan` de `deep-research`, un triage ligero de comparación de artículos WHY/HOW/WHAT entre `quick` y `lit-review`, con listas cortas por artículo y una síntesis entre artículos (`deep-research` 2.9.4 → 2.10.0); `rebuttal-audit` de `academic-paper`, un QA asesoría independiente del borrador de réplica o respuesta del autor frente a los comentarios de los revisores (tabla de cobertura por comentario, lista de huecos y banderas de tono, evidencia y riesgo de mala lectura), que no genera nada y suprime explícitamente Schema 11, las escrituras al Material Passport y `ready_to_submit` cuando se ejecuta solo (aplicado por un lint `check_rebuttal_audit_guard()` con cobertura de mutaciones); además, una ampliación del alcance de `revision-coach` hacia posturas de réplica y desacuerdo y a ámbitos no journals, y los comandos de barra `/ars-3w` y `/ars-rebuttal-audit`. El enrutamiento depende de la forma de la entrada: comentarios de revisores Y un borrador → `rebuttal-audit`; solo comentarios → `revision-coach`. Integrado desde la [PR #433](https://github.com/Imbad0202/academic-research-skills/pull/433) de [@Yaobin29](https://github.com/Yaobin29). Modos del conjunto 25 → 27 (siguen siendo 4 skills). Consulta `CHANGELOG.md` para el detalle por issue.

### v3.12.0 (2026-06-08) — Pista de funciones de auto-investigación de Kong: procedencia de experimentos, fidelidad de figuras, contradicción entre artículos y descomposición de evidencia parcial

> Un release menor que publica la pista de funciones auto-research de Kong et al. (2026, arXiv:2605.18661) junto con el trabajo de descomposición de la trampa de evidencia parcial, cada uno revisado e integrado de forma independiente. **Nuevas funciones:** entrada de procedencia de experimentos y alineación afirmación→experimento, una capa de registro de evidencia con esquema primero para las afirmaciones respaldadas por experimentos; solo se recogen y se alinean (el investigador ejecuta los experimentos externamente; ARS nunca los ejecuta) (#260). Una puerta de fidelidad de figuras y tablas que comprueba si la interpretación de un pie de figura se sigue de los datos y si el manuscrito cita el artefacto para una afirmación que ese artefacto sostiene (#261). Un inventario estructurado de contradicciones entre artículos que hace enumerables los pares evaluados para que el investigador los confirme (#262). Y descomposición en sub-afirmaciones antes de juzgar, tanto en el juez de citas (#213) como en el sintetizador editorial (#214), lo que cierra la trampa de evidencia parcial del §F.3.2 en las dos capas. **Capa de guía e interpretación:** refuerzo de frontera de salida concisa y estable bajo presión en los revisores que producen informes (#274); una nota epistémica de calibración de misma familia y consciente de la rúbrica (#273); y la frontera instrucción/datos del contenido recuperado enunciada como principio permanente (#367). **Alcance negativo:** el META de Kong (#255) se cierra con una sección «Rejected mechanisms» en `POSITIONING.md` que enumera los cinco mecanismos autónomos que ARS no hace, más dos documentos de lecciones de diseño Tier D. **Lint de disciplina de release:** invariantes de consistencia de versión 5–7 (#357) y control de versiones de componentes de ARCHITECTURE (#345). Más correcciones de exactitud en las guardas de fundamento entre modelos (#346 / #349 / #351), la clave de caché de la puerta de citas y el límite de justificación (#359 / #360 / #361), el gold set de evaluación (#250) y la refundación del disclosure de ACL/EMNLP (#242). Los nuevos esquemas, el campo del manifiesto y todos los invariantes son aditivos y retrocompatibles. `academic-pipeline` sigue a la suite en v3.12.0; las otras tres versiones de skill no cambian. Consulta `CHANGELOG.md` para el detalle por issue.

### v3.11.1 (2026-06-06) — Resumen de correcciones, endurecimiento y procedencia posteriores al envío

> Un release parche que acumula las correcciones posteriores al envío detectadas después de v3.11.0, cada una revisada e integrada de forma independiente: una ampliación de la puerta de consentimiento entre modelos a los caminos de verificación de integridad y de profundidad de colaboración (#322), una paralelización del relleno por entrada de OpenAlex + Crossref (#138) y siete correcciones de exactitud y endurecimiento en la puerta de existencia de citas, la capa de políticas de v3.10, el harness de evaluación, los perfiles de evidencia de dominio y los casos límite de la frontera de seguridad de #310 (#323 / #327 / #328 / #329 / #331 / #332 / #333), incluidas dos correcciones P1 (#327, activación del perfil de dominio en el camino sin traspaso, y #328, la puerta de umbrales por clase del harness de evaluación). Sin funciones nuevas y sin cambios de esquema incompatibles. Consulta `CHANGELOG.md` para el detalle por issue.

### v3.11.0 (2026-06-04) — Puerta determinista de verificación de citas (#182)

> Añade una **puerta determinista de verificación de existencia de citas** que se ejecuta de forma independiente de la revisión por pares con LLM. Cada referencia citada se contrasta con hasta cuatro índices bibliográficos: Semantic Scholar + OpenAlex + Crossref y el nuevo **resolutor de arXiv** (`scripts/arxiv_client.py`, sin API key), y se escribe un estado `lookup_verified` por cita (`{true, false, unresolvable}`) en un resumen unificado, de modo que una cita fabricada con un DOI o ID de arXiv demostrablemente falso se detecta por búsqueda en lugar de esperar que un agente revisor se dé cuenta. La puerta **hereda el modelo opt-in `terminal_policies` de v3.10**: la detección se ejecuta siempre, pero una fila `lookup_verified == false` es terminal **solo** cuando el usuario activa `terminal_policies.citation_existence == strict`; el comportamiento por defecto es advisory y se puede confirmar con `/ars-mark-read`. `false` se reduce a **coincidencia fallida por ID** (una búsqueda exacta por DOI o arXiv que demostrablemente falla), así que las citas de humanidades, no inglesas o regionales legítimamente no indexadas quedan en `unresolvable` y nunca bloquean (un intercambio documentado de precisión sobre recobrado). Publica una caché de verificación persistente en SQLite (`~/.cache/ars/verification.db`, TTL de 90 días) con un comando `/ars-cache-invalidate`, una API `verification_gate` independiente más una CLI `verify_passport.py`, y una extensión a cuatro índices (k=0..4) de la matriz de triangulación de contaminación de v3.9.0 (todo advisory). `academic-pipeline` sigue a la suite en v3.11.0; las otras tres versiones de skill no cambian. Especificación: `docs/design/2026-05-21-v3.10-182-promote-citation-gate-spec.md` (enmienda §0 + C-V6).

### v3.10.0 (2026-06-01) — Capa de políticas de triangulación, adopciones del survey de Kong, harness de evaluación y guarda de escritura acotada

> Release menor que agrupa: la **capa de políticas terminales** de triangulación de contaminación opt-in (#127; el comportamiento por defecto de las citas es byte-equivalente al de v3.9.0); las **adopciones del survey de Kong et al. 2026**: el Rebuttal Commitment Ledger (#256/#266/#268/#269) y los perfiles de evidencia de dominio relativos a la disciplina (#259); la **infraestructura de medición de v3.10**: un gold set de evaluación generalizado y una puerta de CI de incremento de ranking (#184); el **MVP de la guarda de escritura acotada** (#134), un hook determinista `PreToolUse` que confine los 23 agentes de fase única a su propio directorio de fase y les deniega Bash (usan en su lugar Grep/Glob y las herramientas de edición estructurada); los comandos de plugin `/ars-mark-read` (#190) más una corrección de un fallo presente desde el origen (#195); un README en chino simplificado (#185); y endurecimiento de CI (#156/#155). `academic-paper` → v3.2.0 y `academic-paper-reviewer` → v1.10.0 por las adiciones del Commitment-Ledger y de los perfiles de dominio; `academic-pipeline` sigue a la suite en v3.10.0. El comportamiento por defecto de las skills no cambia salvo que se active un modo de política estricta; el único cambio activo por defecto es la guarda de #134, que restringe a los subagentes confinados y no las salidas que ve el usuario.

### v3.9.4.2 (2026-05-19) — parche posterior al envío para las puertas de disciplina de CI de la PR #149 (codex post-ship)

> La revisión posterior al envío con Codex de la PR #149 (7 puertas de disciplina de CI) detectó 4 hallazgos P2; v3.9.4.2 endurece 3 de 4. F1: `harness-retirement-monthly.yml` añade `GH_REPO` para que las ejecuciones programadas tengan contexto de repositorio para `gh issue create`. F2: `release-cooldown.yml` filtra la búsqueda de `PREV_TAG` a las etiquetas `v*` para que las etiquetas que no son de release no puedan saltarse el enfriamiento. F3: `release-cooldown.yml` lee también el subject de la etiqueta anotada y acepta la grafía `hot-fix` (v3.9.2 había sido un hotfix falso-negativo). Seguimiento de la PR #157: la anulación `[skip-cooldown]` se lee ahora tanto del mensaje del commit como del mensaje de la etiqueta anotada (una corrección auto-iniciada: la derivación del enfriamiento de esta misma etiqueta demuestra que F2 y F3 funcionan de extremo a extremo). F4 (endurecimiento de monotonicidad del conteo de tests) se revirtió porque destapó un problema preexistente del paquete `scripts/`, seguido como #154 (ya corregido por la PR #158) y reintentado en #155. Cierra #152. Seguimientos: #155, #156.

### v3.9.4.1 (2026-05-19) — parche posterior al envío de la verificación temporal de v3.9.4 (#135 codex post-ship)

> La revisión posterior al envío con Codex de v3.9.4 detectó 4 errores reales que los revisores por subagente no vieron. El parche los corrige los cuatro: (1) `audit()` ahora conecta `citation_provenance` con P2 y P4; cuando un slug de referencia tiene `confidence: low` o `conflict`, el verificador emite `TEMPORAL-METADATA-MISSING` en lugar de usar las fechas de la cronología como verdad de referencia (la comprobación de seguridad first-party de la especificación §3.4 estaba rota). (2) `_date_to_interval` interpreta todas las formas de fecha válidas según el esquema, incluidas `YYYY-MM` (precisión por mes de Crossref) y `YYYY-MM-DD..YYYY-MM-DD` (intervalo); v3.9.4 lanzaba un `ValueError` silencioso con estas y se saltaba la comprobación. (3) P4 ahora vincula capturas de fecha directas cuando no hay marcadores de referencia: frases como "The 2026 policy enabled the 2020 rollout" sí activan la comprobación. (4) El `allOf` de `confidence:high` en `citation_provenance.schema.json` exige ahora la presencia (`then.required`) además del no nulo, lo que cierra la derivación por propiedad ausente. 1561 pruebas pasan (+12 nuevas respecto a la línea base de v3.9.4, 0 regresiones). ARCHITECTURE.md se alinea con el estado actual (estaba desactualizado en v3.8.0).

### v3.9.4 (2026-05-18) — Capa de verificación temporal #135 (advisory)

> Verificador determinista advisory en la frontera Fase 4 → 5 que cubre 5 modos de fallo temporal (P1 aritmética retrospectiva, P2 cita anacrónica, P3 comparador no materializado, P4 inversión causal, P5 presente deíctico). El nuevo hermano de Fase 2 `timeline_extraction_agent` es dueño de `phase2_investigation/timeline.yaml` + `phase2_investigation/citation_provenance.yaml`. El script verificador `scripts/temporal_integrity_audit.py` ejecuta 5 pasadas de forma determinista. Regla de hierro M3 de integridad temporal añadida a `report_compiler_agent` + `draft_writer_agent`. M6-minimal: Crossref `issued` + pdftotext cubren la verificación first-party. M7-minimal: procedencia de fechas + materialización del comparador. M5-stub: solo `version_family_id` declarado por el usuario. Modificación cero de `literature_corpus_entry`, `claim_audit_result`, `claim_intent_manifest`. `bibliography_agent` sin cambios (invariante F2). 3 esquemas sidecar nuevos. Estimación de cobertura: 55-70 % en la línea base / 65-75 % con M7 minimal. 1549 pruebas pasan (+44 nuevas, 0 regresiones).

### v3.9.3 (2026-05-18) — Tareas de casa #128 (utilidades de cliente compartidas + resolutores deduplicados)

> Refactor puro más la corrección de un error latente, procedentes del backlog de la revisión `/simplify` de v3.9.0. Extrae `scripts/_text_similarity.py` (deduplicación de 3 clientes: normalizar / similitud / umbral / constantes de reintento) + `scripts/_passport_yaml.py` (deduplicación de las dos herramientas de migración: configuración de ida y vuelta con ruamel.yaml) + un helper privado `_resolve_by_doi_then_title` (deduplicación del cuerpo de los dos resolutores, superficie de API §3.4 / §3.5 preservada). Estandariza la medición del throttle con `time.monotonic` en OpenAlex + Crossref (antes `time.time`, no segura frente a NTP), alineándose con Semantic Scholar. La infraestructura de importación por dos rutas en las 5 importaciones cruzadas a nivel de módulo (hermano primero, respaldo de paquete de espacio de nombres) preserva la identidad de clase de `SemanticScholarUnavailable` y corrige de propina 2 rutas `import scripts.X` rotadas de forma latente. 1505 pruebas pasan (+23 nuevas, 0 regresiones). #128 §4 (paralelizar OA + CR por entrada) se traslada a #138.

### v3.9.2 (2026-05-18) — Parche de frontera de fase #133

> Cierre de #133 (capa de parche). La corrección arquitectónica a largo plazo se sigue como conductor activo de v3.10 en #134. Añade: una puerta de aclaración de enrutamiento en CLAUDE.md (materiales de varias fases → aclarar con las opciones a-d, no despachar en silencio), valla dura en el prompt para 22 agentes de fase única (`## Phase Boundary (v3.9.2)`) y 16 agentes multi-fase / ortogonales a la fase / meta de fases cruzadas sin valla a propósito (encuadre honesto: un placebo en prosa crea una falsa ilusión de aplicación). El verificador advisory `scripts/check_pipeline_integrity.py` detecta el patrón de #133 a posteriori. Pruebas de humo conductuales con muestreo entre modelos (100 % Opus 4.7, ≥75 % Sonnet + GPT-5.5).

### v3.9.1 (2026-05-18) — Endurecimiento de clientes #129 + #130

> Parche de v3.9.0. Envuelve los fallos de lectura de respuestas de OpenAlex / Crossref como `*Unavailable` (#129); protege `check_claim_audit_consistency` frente a `manifest_id` que no sean cadenas (#130). Ningún cambio de especificación.

### v3.9.0 (2026-05-17) — Medición de triangulación entre índices #102

> Cierre de #102. v3.7.3 publicó la detección de contaminación con un solo índice (Semantic Scholar); v3.9.0 la extiende a una triangulación de tres índices (S2 + OpenAlex + Crossref) **solo como evidencia advisory**. Dos booleanos opcionales nuevos (`openalex_unmatched`, `crossref_unmatched`) en `contamination_signals`; la regla de negación de entrada manual se extiende de forma simétrica. El finalizador añade una matriz advisory de 4 niveles (k=0/1/2/3 sobre los campos `*_unmatched` presentes) y conserva el `CONTAMINATED-UNMATCHED` heredado de v3.7.3 para el caso k=1/k_max=1 solo con S2. La lista blanca de paso del Formatter se amplía de 3 → 9 sufijos; las reglas de rechazo 1-10 no cambian según R-L3-2-E. La capa de políticas (modos estrictos, nivel de bloqueo duro, `venue_type` / `triangulation_policy`) se aplaza a v3.10 conforme a la especificación §2.3. El marcador de k=3 es `CONTAMINATED-TRIANGULATION-UNMATCHED` (describe lo observable, no una causa inferida). 3 reglas firmes nuevas: R-L3-2-C (k se calcula sobre los campos presentes), R-L3-2-D (ninguna clasificación inferida por la API) y R-L3-2-E (lista de rechazos sin cambios; se amplía la lista blanca de paso).

**Migración:** corpus de v3.7.3: ejecuta `python scripts/migrate_literature_corpus_to_v3_9_0.py PATH` para completar los dos campos nuevos. Corpus anteriores a v3.7.3: ejecuta PRIMERO `migrate_literature_corpus_to_v3_7_3.py` y después la migración a v3.9.0 (encadenadas según la especificación §3.7; la herramienta de v3.9.0 solo actúa sobre entradas que ya llevan `contamination_signals.semantic_scholar_unmatched`).

### v3.8.2 (2026-05-17) — Superficie audit_tool_failure de citas ausentes #118

> Cierre de #118. El camino de juicio de restricciones sin citas de `ARS_CLAIM_AUDIT=1` sustituía en silencio `{"judgment": "NOT_VIOLATED"}` cuando se producía un `JudgeInvocationError`, lo que suprimía las comprobaciones de restricciones HIGH-WARN durante una caída transitoria del juez. v3.8.2 encauza esos fallos por un agregado `uncited_audit_failures[]` dedicado en el nivel advisory MED-WARN, replicando la fila INV-14 del camino con citas pero con un esquema propio, porque `claim_audit_result.ref_slug` es obligatorio y el camino sin citas no tiene una referencia a la que anclar. Las cuatro valoraciones de las opciones 1..4 del cuerpo del issue #118 desembocaron en la opción 2 (agregado nuevo); la opción 4 (volver a lanzar y abortar) se rechazó por el coste en cobertura de auditoría de unos endpoints de juez inestables.

- **Agregado nuevo `uncited_audit_failure.schema.json`** (especificación §3.6). Una entrada por cada par frase sin cita × manifiesto donde el juez de restricciones lanzó `JudgeInvocationError`. El mismo enum de clases de fallo que INV-14 del camino con citas (`judge_timeout` / `judge_api_error` / `judge_parse_error` / `cache_corruption` / `retrieval_api_error` / `retrieval_timeout` / `retrieval_network_error`). `rule_version: D4-c-v1-uaf-v1`.
- **Lint UAF-INV-1..UAF-INV-6** (especificación §6 regla 4d). Unicidad de `finding_id`, integridad de la atestación de scoped_manifest_id entre arreglos, integridad del par (M, C) cuando manifest_claim_id no es nulo, deduplicación por (frase, manifiesto), prefijo de fault_class en la justificación y exclusividad entre agregados frente a `constraint_violations[]`.
- **Fila advisory MED-WARN en el §5 del Finalizer**: anotación `[CLAIM-AUDIT-TOOL-FAILURE-UNCITED — <fault-class>]`, puertas que pasan (remediación de reintento en la siguiente pasada). La lista REFUSE del Formatter no cambia: UAF es advisory.
- **Integración en el pipeline** (`scripts/claim_audit_pipeline.py`): se elimina el sitio de captura de excepciones de las líneas 1211-1224; `JudgeInvocationError` emite ahora una fila UAF y `continue`s al siguiente par (frase, manifiesto). Ningún NOT_VIOLATED falso llega a `constraint_violations[]`.
- **Tests**: 18 nuevos (15 de esquema/lint TSUAFUncitedAuditFailureInvariants + 3 de integración con el pipeline TP23UncitedJudgeOutageEmitsUAF). Línea base de 694 → 712 pruebas, 0 regresiones.
- **Documento de agente** (`academic-pipeline/agents/claim_ref_alignment_audit_agent.md`): la tabla de emisión de salida gana una séptima fila; la tabla de manejo de errores pasa de 3 a 4 superficies con la fila UAF del camino sin citas.

### v3.8.0 (2026-05-16) — Localizador y auditoría de fidelidad de afirmaciones L3 (hito pareado)

> v3.7.3 y v3.8 cierran de extremo a extremo la brecha L3 (fidelidad de la afirmación). v3.7.3 publica la infraestructura de localizadores: cada cita lleva un ancla de tres capas para que futuras auditorías puedan recuperar el pasaje citado. v3.8 publica la pasada de auditoría que consume esas anclas, juzga si la fuente citada sostiene la afirmación y rechaza mediante gate las violaciones HIGH-WARN en la hard gate terminal del formatter. El release también agrupa 5 PRs de funciones con rastro de auditoría acumulados desde v3.7.0 (#104 / #105 / #108 / #111 / #115).

- **#103 — `claim_ref_alignment_audit_agent`** (v3.8, PR #121). Agente de auditoría de la transición Etapa 4→5, opt-in (`ARS_CLAIM_AUDIT=1`, desactivado por defecto). Juzga cada cita muestreada contra el extracto recuperado; emite los agregados `claim_audit_results[]` + `claim_intent_manifests[]` + `claim_drifts[]` + `uncited_assertions[]` + `constraint_violations[]`. La matriz del finalizador de 8 filas encauza las clases HIGH-WARN (CLAIM-NOT-SUPPORTED / NEGATIVE-CONSTRAINT-VIOLATION / FABRICATED-REFERENCE / ANCHORLESS / CONSTRAINT-VIOLATION-UNCITED) por las reglas REFUSE 6-10 del formatter. El ejecutor de calibración se publica con un gold set de 20 tuplas (T-C1 FNR<0,15 + FPR<0,10, T-C2 por clase, T-C3 integridad de forma). 8 rondas de revisión de doble pista (R1 codex + Gemini-3.1-pro-preview, R2-R8 solo codex después de agotar la cuota de Gemini); trayectoria R1 4P1+2P2 → R8 0P1+4P2 en la puerta de publicación.
- **v3.7.3 — Emisión de citas en tres capas y señales de contaminación** (PR #98). `synthesis_agent` / `draft_writer_agent` / `report_compiler_agent` ganan el H2 `## Three-Layer Citation Emission (v3.7.3)`. Cada `<!--ref:slug-->` lleva un `<!--anchor:<kind>:<value>-->` con `<kind> ∈ {quote, page, section, paragraph, none}` (las anclas de cita están limitadas a 25 palabras y codificadas en URL). El finalizador de `pipeline_orchestrator_agent` pasa a 5 celdas con una comprobación NO-LOCATOR de precedencia cero. `formatter_agent` añade un rechazo explícito de hard gate para `[UNVERIFIED CITATION — NO QUOTE OR PAGE LOCATOR]`. `literature_corpus_entry.schema.json` añade el objeto opcional `contamination_signals: { preprint_post_llm_inflection, semantic_scholar_unmatched }`. `bibliography_agent` calcula ambas señales al ingerir. Trayectoria de revisión de 11 rondas (Codex×10 + entre modelos con Gemini×1) que cerró 22 hallazgos. Especificación: `docs/design/2026-05-12-ars-v3.7.3-claim-faithfulness-and-contaminated-source-spec.md`. Motivación externa: Zhao et al., arXiv:2605.07723 (2026-05).
- **#108 — Renderizador de anclas de política de divulgación de IA** (publicado con rastro de auditoría el 2026-05-14). Añade las rutas de divulgación con anclas de política PRISMA-trAIce / ICMJE / Nature / IEEE junto al renderizador de rutas de venue existente.
- **#111 — Emisión de `slr_lineage` en el traspaso systematic-review → academic-paper** (2026-05-15). Campo booleano opcional `slr_lineage` en Schema 9; el productor `pipeline_orchestrator_agent` lo escribe en cada transición de traspaso; el modo consumidor `disclosure` despacha `--policy-anchor=prisma-trAIce` conforme a la puerta de pista de la invariante G2 del §4.3.
- **#104 — Motivación del README: ancla de evidencia a escala de corpus de Zhao et al.** (2026-05-15). La sección de motivación de README + `README.zh-TW.md` enmarca la línea v3.7.x frente al hallazgo de 146.932 citas alucinadas de Zhao et al.
- **#105 — Herramienta de migración para completar contamination_signals de v3.7.3** (2026-05-15). `scripts/migrate_literature_corpus_to_v3_7_3.py` recalcula hacia atrás ambas señales de contaminación en passports anteriores a v3.7.3.
- **#115 — Madurez del cliente de Semantic Scholar** (2026-05-15). `scripts/semantic_scholar_client.py` añade un throttle de 1 req/s (baja a 0,1 s cuando detecta `S2_API_KEY`), un enclavamiento de caída en URLError y `reset_outage_latch()` para lotes largos entre passports.

### v3.7.0 (2026-05-05) — Empaquetado como plugin de Claude Code

> Actualización de empaquetado: ARS se instala ahora en una línea en Claude Code CLI / VS Code / JetBrains con `/plugin marketplace add Imbad0202/academic-research-skills` + `/plugin install academic-research-skills`. El flujo tradicional de `git clone + symlink to ~/.claude/skills/` sigue funcionando: las dos pistas son de primera clase.

- **Manifiesto del plugin + metadatos del marketplace** (Fase 1, PR #68). `.claude-plugin/plugin.json` declara el conjunto (4 skills autodescubiertas desde el directorio `skills/` mediante enlaces simbólicos relativos). `.claude-plugin/marketplace.json` registra el plugin para que un único endpoint alojado en GitHub sirva tanto el listado del marketplace como la fuente del plugin. README + `README.zh-TW.md` + `docs/SETUP.md` llevan instrucciones de instalación de doble pista.
- **10 comandos de barra** en `commands/ars-*.md` (Fase 2.1, PR #69) que mapean las entradas de `MODE_REGISTRY.md` a disparadores `/ars-<mode>`. El enrutamiento de modelos queda fijado en el frontmatter de cada comando: `opus` para `full` y `revision-coach` (profundidad arquitectónica / de interpretación de reseñas) y `sonnet` para los otros 8. Ninguno con Haiku, por política del proyecto.
- **3 agentes incluidos en el plugin** en `agents/*_agent.md` (Fase 2.1, PR #69) como enlaces simbólicos relativos a los agentes aguas abajo endurecidos en v3.6.7 dentro de `deep-research/agents/`: `synthesis_agent`, `research_architect_agent`, `report_compiler_agent`. Se conservan los nombres de archivo con guion bajo para no romper las rutas fijadas de `scripts/check_v3_6_7_pattern_protection.py` ni la invariante Clause 1 confinada al manifiesto INV-3. Los enlaces simbólicos (no copias) preservan una única fuente de verdad y evitan la superficie de ataque Patrón C3 que la barrida de inversión de v3.6.7 §6 y el lint INV-1/2/3 cierran. (Se materializaron a copias reales byte-idénticas en #413: los enlaces simbólicos relativos rompen los checkouts de Windows sin `core.symlinks` y las instalaciones por descarga zip; la garantía de fuente única pasó al lint de CI de igualdad byte a byte `scripts/check_agents_mirror_sync.py`.)
- Se añade **`model: inherit`** a esos tres frontmatters de agentes fuente. Se elige inherit frente a fijar `sonnet` para que una sesión opus ejecutando el pipeline completo de ARS mantenga agentes opus (en lugar de quedar topada). El hook PreToolUse `~/.claude/hooks/warn-agent-no-model.sh` del usuario bloquea Haiku en la frontera de despacho, así que `inherit` se resuelve a través de un modelo ya libre de Haiku.
- **Hook de anuncio al iniciar sesión** en `hooks/hooks.json` + `scripts/announce-ars-loaded.sh` (Fase 2.2, PR #70). Cuando el plugin se carga, el hook inyecta un `additionalContext` con la lista de los 10 comandos de barra, los 3 agentes del plugin y una referencia al presupuesto de tokens en el primer turno del LLM. Los valores de origen `startup` y `clear` reciben el anuncio completo; `resume` y `compact` reciben una confirmación de una línea para no gastar contexto. Compatible con Bash 3.2: funciona con el `/bin/bash` de fábrica de macOS sin necesidad de `brew install bash`.
- **Reducción de alcance de la Fase 2.2**: se excluyó de v3.7.0 un hook de auditoría codex `SubagentStop → run_codex_audit.sh`, por un hueco de contrato (el payload de SubagentStop no lleva información de etapa ni de entregable, así que el envoltorio tendría que deducir a medias los argumentos obligatorios) y por una frontera de clase de invocador (las líneas 4–7 de `run_codex_audit.sh` prohíben la invocación dentro de la misma sesión por el LLM, y PostToolUse se dispara dentro de la sesión que produce). La integración real del hook de auditoría queda aplazada a un release futuro cuando ARS tenga un contrato de propagación de etapa/entregable. Consulta `docs/design/2026-04-30-ars-v3.7.0-plugin-packaging-roadmap.md`, nota de actualización de 2026-05-05 (reducción de alcance de la Fase 2.2).
- **`docs/PERFORMANCE.md` + `.zh-TW.md`** ganan una subsección «v3.7.0 Plugin agents and model routing» que explica la semántica de inherit y el límite de alcance actual de 3 agentes.
- **Cadena de revisión con Codex a lo largo de las tres PRs**: 8 rondas iterativas en línea + 3 rondas frescas a nivel de PR, todas convergiendo a 0 hallazgos P0/P1/P2 antes de integrar. La revisión fresca de PR de la Fase 2.2 detectó un P2 (`${CLAUDE_PLUGIN_ROOT}` sin comillas, que rompe las rutas de instalación con espacios) que las rondas en línea no vieron; confirma el valor de separar la revisión de implementación (en línea) de la revisión de contrato (fresca).
- **Qué NO cambió**: los cuatro directorios de skill, los 25 modos, los prompts de los agentes, los archivos de esquema y los contratos de lint. El empaquetado como plugin solo añade superficie nueva de nivel superior (`commands/`, `agents/`, `hooks/`, `.claude-plugin/`, el directorio de enlaces `skills/` y tres adiciones de frontmatter `model: inherit` en los agentes del plugin). Los 4,3k usuarios existentes de la instalación por clonación no ven ningún cambio incompatible.

### v3.6.8 (2026-05-03) — Puerta de contrato Generador-Evaluador (publicación de la especificación v3.6.6)

> Nota de nomenclatura: este release publica la **especificación del contrato generador-evaluador de v3.6.6**
> y su implementación. El trabajo de v3.6.6 llegó después del de v3.6.7 por ordenación del proyecto;
> el documento de diseño mantiene la nomenclatura interna v3.6.6 para la versión de la puerta de contrato,
> mientras que el release del conjunto se etiqueta v3.6.8 para mantener el CHANGELOG monótono.

- **Schema 13.1** (`shared/sprint_contract.schema.json`) amplía Schema 13 con dos valores nuevos del enum `mode` (`writer_full` + `evaluator_full`), dos campos opcionales nuevos de nivel superior (`pre_commitment_artifacts` solo para writer, `disagreement_handling` solo para evaluator) y 12 ramas `allOf` que aplican puertas condicionadas a revisor / writer / evaluador. Los contratos de revisor existentes validan byte-equivalentes bajo Schema 13.1 (promesa de cero toques del §3.6).
- **Dos plantillas de contrato publicadas nuevas**, en `shared/contracts/writer/full.json` (D1–D7, F1/F4/F2/F3/F0) y `shared/contracts/evaluator/full.json` (D1–D5, F1/F2/F3/F6/F4/F5/F0). Promovidas de artefactos de diseño en la rama de especificación a estado publicado real de forma atómica con la mejora a Schema 13.1.
- **Orquestación en dos fases** dentro de `academic-paper full`: la Fase 4 se divide en Fase 4a (precompromiso del writer sin ver el artículo) + Fase 4b (redacción del writer con el artículo visible y auto-puntuación); la Fase 6 se divide en Fase 6a (precompromiso del evaluador sin ver el artículo) + Fase 6b (puntuación y decisión del evaluador con el artículo visible). Los delimitadores de datos `<phase4a_output>` / `<phase6a_output>` con número de fase replican el patrón de revisores de v3.6.2. Resumen del conteo de lints: writer 3+4 / evaluador 5+5 / revisor 5+6 (el revisor sigue sin tocarse).
- El **SKILL y los archivos de agente de `academic-paper`** ganan un bloque literal `## v3.6.6 Generator-Evaluator Contract Protocol` (101 líneas en SKILL.md, más 47 en `draft_writer_agent.md` y 57 en `peer_reviewer_agent.md`). SKILL.md añade también una sección nueva `## Known limitations` con notas de degradación elegante y de reanudación entre sesiones para v3.6.7+.
- **Ampliaciones del validador**: `scripts/check_sprint_contract.py` con auditoría SC-* del condicionamiento por modo (SC-5 + SC-11 solo revisor; SC-9 extendido a las tres familias de modos). 17 tests nuevos llevan el conteo de tests unitarios del validador de 54 a 71 (positivo + 5 negativos de rama de esquema + 2 de regresión de revisor del §3.6 + 6 de condicionamiento por modo).
- **Lint de CI sobre el manifiesto**: `scripts/check_v3_6_6_ab_manifest.py` aplica el esquema del manifiesto del §6.2 y los invariantes versionados en git del §6.5 sobre `tests/fixtures/v3.6.6-ab/manifest.yaml`. `.github/workflows/spec-consistency.yml` amplía el bucle de validación de contratos de sprint para iterar los directorios de plantillas de writer y evaluador junto al bucle de revisor existente, y ejecuta además el nuevo lint del manifiesto.
- **Stub del fixture de evidencia A/B** en `tests/fixtures/v3.6.6-ab/` (30 archivos): manifiesto + README + 6 entradas/baseline del artículo A + 1 entrada/baseline del artículo C + extracto de revisor de la Etapa 3 + 6 marcadores de posición del juez codex. Los datos reales del fixture se completan en commits posteriores, antes de que termine la implementación.

### v3.6.7 (2026-04-30) — Protección contra patrones en agentes aguas abajo (Pasos 1+2)

- **Tres agentes aguas abajo endurecidos frente a 13 de los 17 patrones de alucinación/deriva documentados**: `synthesis_agent` (capa narrativa A1–A5), el modo de diseño de encuestas de `research_architect_agent` (capa de instrumentos B1–B5) y el modo abstract-only de `report_compiler_agent` (capa de publicación C1–C3). Cada prompt de agente lleva ahora un bloque `PATTERN PROTECTION (v3.6.7)`.
- **Cuatro archivos de referencia en `shared/references/`**: `irb_terminology_glossary.md`, `psychometric_terminology_glossary.md`, `protected_hedging_phrases.md`, `word_count_conventions.md`. Los archivos de referencia contienen contratos operativos que los prompts de los agentes citan por ruta.
- **Plantilla de prompt de auditoría entre modelos** en `shared/templates/codex_audit_multifile_template.md`, con siete dimensiones de auditoría y una comprobación obligatoria de tres partes en la Sección 4(f) para los paquetes de `report_compiler_agent`. Fallar cualquier sub-comprobación es un hallazgo P1.
- **Lint estático + suite de mutaciones de 29 tests**: `scripts/check_v3_6_7_pattern_protection.py` aplica la presencia de las cláusulas de protección y la forma de las frases de obligación; `scripts/test_check_v3_6_7_pattern_protection.py` conserva la evidencia de la revisión codex para que futuras regresiones del comprobador salten en CI. Ambos están conectados a `.github/workflows/spec-consistency.yml`.
- **Historial de revisión con Codex**: siete rondas de revisión entre modelos con `gpt-5.5` + `xhigh` alcanzaron SHIP-OK con cero hallazgos P1+P2. El Paso 6 (hooks de runtime del orquestador) y el Paso 8 (caso sintético de evaluación) se publican en una PR posterior.

### v3.6.5 (2026-04-27) — Integración de consumidores de `literature_corpus[]` del Material Passport

- **Dos consumidores de literatura de Fase 1 conectados**: `deep-research/agents/bibliography_agent.md` y `academic-paper/agents/literature_strategist_agent.md`. Ambos siguen el mismo flujo de cinco pasos **corpus primero, la búsqueda completa el hueco** cuando el passport lleva un `literature_corpus[]` no vacío, y las mismas cuatro Reglas de Hierro (Mismos criterios / Ningún salto silencioso / Ninguna mutación del corpus / Degradación elegante al fallar el parseo).
- **Bloque PRE-SCREENED de reproducibilidad** en los informes de Estrategia de Búsqueda: enumera entradas del corpus incluidas / excluidas / omitidas, con la nota de cero resultados F3 y el reporte de procedencia F4a–F4f que se componen con declaración parcial de `obtained_via` / `obtained_at`. `final_included = pre_screened_included[] ∪ external_included[]` se mantiene neutro: sin etiquetas de procedencia en las entradas de bibliografía ni en las filas de la matriz de literatura.
- **Referencia del protocolo de consumidores** en `academic-pipeline/references/literature_corpus_consumers.md`, con la plantilla PRE-SCREENED canónica, ejemplos BAD/GOOD, las cuatro Reglas de Hierro y instrucciones de lectura por consumidor.
- **Lint de CI** `scripts/check_corpus_consumer_protocol.py`, que aplica nueve invariantes de protocolo con una lista de consumidores gobernada por manifiesto (`scripts/corpus_consumer_manifest.json`).
- **La advertencia del Schema 9 queda retirada**: `shared/handoff_schemas.md` retira la advertencia de v3.6.4 «Integración en el lado consumidor aplazada a v3.6.5+» y la sustituye por un apuntador al protocolo de consumidores.
- Detección por presencia, sin cambio de esquema y sin flag nuevo. Los fallos de parseo recurren al flujo solo con bases externas, con una superficie `[CORPUS PARSE FAILURE]`. La integración con el corpus de `citation_compliance_agent` queda aplazada (versión objetivo por determinar, posterior a v3.8).
- Sin cambios incompatibles. Los adaptadores existentes del usuario funcionan sin modificación.

### v3.6.4 (2026-04-25) — Puerto de entrada `literature_corpus[]` del Material Passport

- **Campo `literature_corpus[]`** añadido al Schema 9 como puerto de entrada opcional para la literatura propia del usuario. Cada entrada conforme a `shared/contracts/passport/literature_corpus_entry.schema.json` (autores en CSL-JSON, año, título, source_pointer + `abstract` / `user_notes` opcionales y privadas).
- **Contrato de adaptador neutro en lenguaje** en `academic-pipeline/references/adapters/overview.md`: cualquier programa (en cualquier lenguaje) que lea una fuente de corpus del usuario puede producir un `passport.yaml` y un `rejection_log.yaml` conformes. Errores a nivel de entrada tolerados, errores a nivel de adaptador que abortan, ordenación determinista.
- **Tres adaptadores de referencia en Python** bajo `scripts/adapters/`: `folder_scan.py` (sistema de archivos con PDFs), `zotero.py` (exportación JSON de Better BibTeX) y `obsidian.py` (frontmatter de una vault). Solo puntos de partida; se espera que cada usuario escriba sus propios adaptadores para fuentes que no sean las de referencia.
- **Contrato del registro de rechazos** en `shared/contracts/passport/rejection_log.schema.json`, con un enum cerrado de valores categóricos de motivo; siempre se emite (vacío si no hay rechazos).
- **Puertas de CI**: `scripts/check_literature_corpus_schema.py` valida esquemas y ejemplos de adaptadores; `scripts/sync_adapter_docs.py --check` evita la deriva esquema→documentación; el nuevo workflow `pytest.yml` ejecuta `scripts/adapters/tests/` con disparadores filtrados por ruta.
- **Solo puerto de entrada en v3.6.4**: v3.6.4 publicó el esquema y el contrato de adaptador sin integración de consumidores. `bibliography_agent` y `literature_strategist_agent` se conectaron en v3.6.5.
- Sin cambios incompatibles.

### v3.6.3 (2026-04-23) — Frontera de reinicio de passport opcional

- **Frontera de reinicio de passport opcional** (`ARS_PASSPORT_RESET=1`). Promueve cada checkpoint FULL a frontera de reinicio de contexto. El nuevo modo `resume_from_passport=<hash>` permite reanudar en una sesión nueva de Claude Code solo desde el registro del Material Passport. Con el flag ACTIVADO, el modo `systematic-review` hace obligatorio el reinicio en cada checkpoint FULL; los demás modos tratan el reinicio como el valor por defecto gobernado por el flag. Con el flag DESACTIVADO se preserva byte a byte el comportamiento previo a v3.6.3.
- El Schema 9 gana un registro append-only `reset_boundary[]` con dos tipos de entrada (`kind: boundary` + `kind: resume`). El hash usa JSON Canonical Form + SHA-256 con un marcador canónico para la seguridad de la autorreferencia. El campo opcional `pending_decision` gestiona las elecciones de rama OBLIGATORIAS.
- Nuevo lint de CI `scripts/check_passport_reset_contract.py`: toda mención del flag debe co-localizar un apuntador al documento de protocolo autoritativo.
- Documento de protocolo: `academic-pipeline/references/passport_as_reset_boundary.md`.
- `docs/PERFORMANCE.md` se actualiza con guías para sesiones largas.
- Sin cambios incompatibles. El valor por defecto del flag es OFF.

### v3.6.2 (2026-04-23) — Puerta dura de contrato de sprint del revisor

v3.6.2 introduce los contratos de sprint de Schema 13 y una orquestación con puerta dura que obliga a los revisores a precomprometer su plan de puntuación antes de leer el artículo. Primera prueba solo con revisores; writer y evaluador aplazados a v3.6.4. Consulta el CHANGELOG.

- **Contrato de sprint de Schema 13** con `panel_size`, `acceptance_dimensions`, `failure_conditions` (con precedencia por `severity` + `cross_reviewer_quantifier` relativo al panel), `measurement_procedure`, `override_ladder` opcional y `agent_amendments` acotados. Validador: `scripts/check_sprint_contract.py`.
- **Puerta dura de dos llamadas.** Los revisores ejecutan una Fase 1 a ciegas del contenido del artículo + una Fase 2 con el artículo visible; la salida de la Fase 1 se envuelve en el delimitador de datos `<phase1_output>...</phase1_output>` para estrechar la superficie de auto-inyección.
- **Protocolo mecánico de tres pasos del sintetizador.** Construir la matriz entre revisores → evaluar cada `failure_condition` con el cuantificador relativo al panel y un vocabulario de expresiones reconocido → resolver la precedencia por `severity`. La lista de operaciones prohibidas queda explícita en `editorial_synthesizer_agent`.
- **Se publican dos plantillas de revisor** (`shared/contracts/reviewer/full.json`, panel 5; `shared/contracts/reviewer/methodology_focus.json`, panel 2). `reviewer_re_review`, `reviewer_calibration` y `reviewer_guided` quedan reservados en el enum del esquema pero se publican sin plantillas de contrato en v3.6.2; conservan el comportamiento previo a v3.6.2. `reviewer_quick` queda fuera del enum por completo.
- Versión del SKILL de `academic-paper-reviewer`: `1.8.1 → 1.9.0`. Versión del SKILL de `academic-pipeline`: `3.5.1 → 3.6.2` (invariante de versión de la suite). Versión de la suite: `3.6.2`.
- Consulta la especificación [`docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md`](docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md) y el protocolo [`academic-paper-reviewer/references/sprint_contract_protocol.md`](academic-paper-reviewer/references/sprint_contract_protocol.md).

### v3.5.1 (2026-04-22) — Sonda opcional de comprobación de lectura en modo socrático

v3.5.1 añade una sonda de honestidad opcional al Socratic Mentor (`ARS_SOCRATIC_READING_PROBE=1`). Desactivada por defecto. Consulta el CHANGELOG.

- **Sonda de comprobación de lectura opcional**: cuando está definido `ARS_SOCRATIC_READING_PROBE=1`, el Socratic Mentor lanza una sonda de honestidad única en sesiones orientadas a un objetivo donde el usuario ha citado un artículo concreto. Declinar se registra sin penalización. El resultado fluye al Research Plan Summary y al Informe de Auto-Reflexión de IA de la Etapa 6. Sin agentes nuevos y sin cambios de esquema.
- Versión del SKILL de `deep-research`: `2.9.0 → 2.9.1`. Versión del SKILL de `academic-pipeline`: `3.5.0 → 3.5.1`. Versión de la suite: `3.5.1`.

### v3.5.0 (2026-04-21) — Collaboration Depth Observer

- **Agente nuevo**: `collaboration_depth_agent` en `academic-pipeline` (el Agent Team pasa de 3 a 4). Se invoca en cada checkpoint FULL/SLIM y al completar el pipeline; puntua la colaboración entre usuario e IA contra una rúbrica de 4 dimensiones. **Solo advisory: nunca bloquea el avance.** Los checkpoints OBLIGATORIOS (las puertas de integridad de las Etapas 2.5 / 4.5) NO invocan el observador.
- **Rúbrica nueva**: [`shared/collaboration_depth_rubric.md`](shared/collaboration_depth_rubric.md) v1.0. Dimensiones: Delegation Intensity, Cognitive Vigilance, Cognitive Reallocation y Zone Classification (Zona 1 / Zona 2 / Zona 3). Basada en Wang, S., & Zhang, H. (2026). "Pedagogical partnerships with generative AI in higher education: how dual cognitive pathways paradoxically enable transformative learning." *International Journal of Educational Technology in Higher Education*, 23:11. DOI [10.1186/s41239-026-00585-x](https://doi.org/10.1186/s41239-026-00585-x).
- **La divergencia entre modelos se señala, no se promedia**: cuando está definido `ARS_CROSS_MODEL`, el observador se ejecuta con los dos modelos; un desacuerdo superior a 2 puntos en una dimensión se reporta en lugar de suavizarse en silencio. Existe la salida `ARS_CROSS_MODEL_SAMPLE_INTERVAL` para el intercambio de coste.
- **Guarda de etapas cortas**: las etapas con menos de 5 turnos de usuario inyectan un bloque estático `insufficient_evidence` en lugar de despachar el observador completo.
- **Disciplina anti-sycophancy**: las puntuaciones ≥ 7 exigen citas concretas de turnos del diálogo; la Zona 3 dispara una re-auditoría; sin encuadres motivacionales.
- Versión del SKILL de `academic-pipeline`: `3.3.0 → 3.4.0`. Versión de la suite: `3.5.0`. Nuevo lint `scripts/check_collaboration_depth_rubric.py` + 10 tests.

### v3.4.0 (2026-04-20) — Compliance Agent + Schema 12

- **Compliance Agent** (compartido): un único agente consciente del modo que ejecuta los 17 ítems de PRISMA-trAIce (solo en modo SR) + los 4 principios y la matriz de 8 roles de RAISE. Se engancha a las puertas de integridad existentes de las Etapas 2.5 / 4.5; bloqueo por nivel (Mandatory → bloquea, HR → avisa, R/O → informa). Las entradas que no son de revisión sistemática ejecutan solo los principios y solo avisan.
- **Schema 12 compliance_report** añadido al Material Passport mediante `compliance_history[]` (append-only).
- **Escalera de 3 rondas de anulación por el usuario** que inyecta automáticamente `disclosure_addendum` en el manuscrito. No hay forma de evadir la detección.
- **Calibración con reporte transparente**, sin puerta dura de FNR/FPR: coherente con `task_type: open-ended`.
- **CI de frescura aguas arriba** avisa (sin bloquear) cuando PRISMA-trAIce deriva.
- **Documentación de sesiones largas**: el Material Passport como mecanismo de reanudación entre sesiones.

### v3.3.6 (2026-04-15) — Simplificación del README + documento de ARQUITECTURA

- Se añade `docs/ARCHITECTURE.md` como única fuente de verdad de la estructura del pipeline (flujo, matriz, acceso a datos, grafo de dependencias, puertas de calidad, modos). Se integró en main mediante la PR #18.
- Se añaden `docs/SETUP.md` (prerrequisitos, claves de API, Pandoc/tectonic, verificación entre modelos, métodos de instalación) y `docs/PERFORMANCE.md` (presupuestos de tokens, ajustes recomendados de Claude Code). El README enlaza a ambos en lugar de incluirlos en línea.
- README simplificado: se eliminaron el diagrama ASCII del pipeline y la lista de 16 funciones clave (sustituidos por ARCHITECTURE.md); la sección Detalle de las skills ahora ancla los números de versión y remite a ARCHITECTURE.md §3 para los rosters de agentes.
- Nota: ningún cambio funcional en ninguna skill. Solo reorganización de la documentación. Versión de la suite: `3.3.6`.

### v3.3.5 (2026-04-15)
- Se añaden `benchmark_report.schema.json` y el bloque opcional `repro_lock` en el Material Passport. Ambos se publican con documentos de patrón, lints y ejemplos. Primer manifiesto formal de dependencias de desarrollo en Python (`requirements-dev.txt`).

### v3.3.4 (2026-04-15) — Parche de sincronización del changelog del README

- Sincronizadas las secciones de changelog incrustadas en `README.md` y `README.zh-TW.md` para que incluyan los resúmenes que faltaban de los releases `v3.3.3` y `v3.3.2`.
- Ampliado `scripts/check_spec_consistency.py` para que la futura deriva del changelog del README falle en CI.
### v3.3.3 (2026-04-15) — Preparación del release + endurecimiento del lint

- El lint del frontmatter de SKILL se endurece: ahora un `---` de cierre ausente falla limpiamente en lugar de parsearse como YAML válido.
- Un frontmatter que parsea como YAML válido pero no como un mapeo reporta un error legible en lugar de petar.
- Corregido el enlace roto del escaparate al informe de auditoría posterior a la publicación en ambos README.
- Añadida la validación de enlaces relativos del README a la comprobación de consistencia de especificación, para que los enlaces muertos fallen en CI.
- Alineado el contrato de salida DOCX en toda la documentación: la generación directa de `.docx` depende de Pandoc, con Markdown + instrucciones de conversión como respaldo.
- Preparado el release `v3.3.3`: bump de la suite, `academic-paper` -> v3.0.2, `academic-pipeline` -> v3.2.2.

### v3.3.2 (2026-04-15) — Niveles de acceso a datos y metadatos de tipo de tarea

- Añadido `metadata.data_access_level` a todos los `SKILL.md` de nivel superior, con vocabulario forzado: `raw`, `redacted`, `verified_only`.
- Añadido `metadata.task_type` a todos los `SKILL.md` de nivel superior, con vocabulario forzado: `open-ended`, `outcome-gradable`.
- Añadidos scripts de lint y tests unitarios para ambos campos de metadatos, conectados al workflow de consistencia de especificación de GitHub Actions.
- Añadido `shared/ground_truth_isolation_pattern.md` y enlazado el vocabulario nuevo desde `shared/handoff_schemas.md`.

### v3.3.1 (2026-04-14) — Parche de consistencia de especificación

- Sincronizados README, `.claude/CLAUDE.md`, `MODE_REGISTRY.md` y los archivos `SKILL.md` con los conteos de modos y las versiones publicadas de las skills.
- **Nota histórica (sustituida por v3.16):** en este release se implementaron comprobaciones muestrales de integridad y una crítica DA ejecutada de forma separada y a ciegas, mientras que un sexto revisor estaba solo planificado. Ese diseño del sexto revisor se retiró después; la revisión completa sigue siendo un panel fijo de cinco plazas.
- Aclarada la semántica de los checkpoints adaptativos: los checkpoints SLIM también esperan una confirmación explícita del usuario.
- Reafirmado que las puertas de integridad de las Etapas 2.5 y 4.5 no se pueden saltar.
- Añadida una comprobación ligera de consistencia de especificación y un workflow de GitHub Actions para detectar derivas futuras.

### v3.3 (2026-04-09) — Mejoras inspiradas en PaperOrchestra

Integra técnicas de [PaperOrchestra](https://arxiv.org/abs/2604.05018) (Song, Song, Pfister & Yoon, 2026, Google).

- **Verificación con la API de Semantic Scholar** — Comprobación programática de existencia de referencias de Nivel 0 mediante la API de S2. Coincidencia de títulos con Levenshtein >= 0.70, detección de desajuste de DOI, deduplicación de bibliografía por IDs de S2. Degradación elegante si la API no está disponible.
- **Protocolo anti-fuga** — La Directiva de Aislamiento de Conocimiento prioriza los materiales de la sesión sobre la memoria paramétrica del LLM. Marca `[MATERIAL GAP]` cuando falta contenido en lugar de completarlo desde la memoria. Reduce el riesgo de fallo de los Modos 5/6.
- **Verificación de figuras con VLM** (opcional) — Verificación en bucle cerrado de las figuras renderizadas mediante un LLM con visión. Lista de 10 puntos, máximo 2 iteraciones de refinement.
- **Protocolo de trayectorias de criterios** — Comparaciones de juicio por dimensión ancladas en evidencia entre rondas de revisión (7 dimensiones). Las regresiones que llevan decisión disparan un checkpoint obligatorio; no se calcula ningún delta de puntuación.
- **Paralelización de la Etapa 2** — La visualización y la construcción del argumento pueden ejecutarse en paralelo después de completar el esquema.
- Versiones nuevas: deep-research v2.8, academic-paper v3.0, academic-pipeline v3.2

### v3.2 (2026-04-09) — Integración de Lu 2026 (Nature)

Integra las ideas de Lu et al. (2026, *Nature* 651:914-919), el primer sistema autónomo de investigación por IA de extremo a extremo que superó la revisión ciega por pares.

- **Lista de 7 modos de fallo de investigación con IA** — bloquea el pipeline en las Etapas 2.5/4.5 ante sospecha de errores de implementación, resultados alucinados, dependencia de atajos, bug-como-hallazgo, fabricación de metodología o frame-lock. Amplía la taxonomía existente de 5 tipos de alucinación de citas.
- **Modo de calibración del revisor** (academic-paper-reviewer v1.8) — medición opcional de FNR/FPR/exactitud balanceada contra un gold set del usuario. Ensamblado 5×, entre modelos activado por defecto y divulgación de confianza acotada a la sesión.
- **Modo Disclosure** (academic-paper v2.9) — la ruta de venue por defecto devuelve una aplicabilidad `REQUIRED`, `ACTION_ONLY`, `NOT_REQUIRED` o `UNKNOWN`, más un estado de parada tipada explícito cuando hace falta; las invocaciones con anclas de política usan su renderizador propio específico de ancla. v1 cubre ICLR, NeurIPS, Nature, Science, ACL y EMNLP. (Ampliado desde entonces: la base de datos v2 (#596) añade 9 destinos de política de publicaciones médicas — ICMJE, NEJM, The Lancet, JAMA, BMJ, PLOS y Frontiers, más los dos primeros destinos en chino de la base de datos: la entrada de editora completa de 中华护理杂志社 y la de la revista 国际眼科杂志.)
- **Criterio de parada temprana** (academic-pipeline v3.1) — comprobación de convergencia y transparencia de presupuesto al inicio del pipeline.
- **Espectro Fidelidad-Originalidad** — clasifica todos los modos de 3 skills según Lu 2026 Fig 1c.
- Versiones nuevas: academic-paper v2.9, academic-paper-reviewer v1.8, academic-pipeline v3.1

### v3.1.1 (2026-04-09) — IS Senior Scholars' Basket of 11

Contribuciones externas: [@mchesbro1](https://github.com/mchesbro1) propuso y redactó originalmente la IS Basket of 8 journals ([Issue #5](https://github.com/Imbad0202/academic-research-skills/issues/5)); [@cloudenochcsis](https://github.com/cloudenochcsis) la amplió a la completa Senior Scholars' Basket of 11 ([Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7), [PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8)). Se actualizó `academic-paper-reviewer/references/top_journals_by_field.md`, Sección 7, añadiendo *Decision Support Systems*, *Information & Management* e *Information and Organization*. Fuente: [AIS Senior Scholars' List of Premier Journals](https://aisnet.org/research/seniorscholarsbasket/).

### v3.1 (2026-04-06) — Anti-context-rot + marcos cognitivos + tamaño contenido

Inspirado en patrones de [aspi6246/Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics).

**Oleada 1: anclas anti-context-rot**
- 29 anti-patrones explícitos en las 4 skills (7-8 por skill, formato de tabla con «Por qué falla» + «Comportamiento correcto»)
- 22 marcadores IRON RULE sobre reglas críticas que no se pueden violar ni siquiera en conversaciones largas
- Restricción de solo lectura en academic-paper-reviewer (los revisores no pueden modificar el manuscrito)

**Oleada 2: trazabilidad + marcos cognitivos + refuerzo**
- Matriz de trazabilidad R&R (Schema 11): añade a la salida de la re-revisión las columnas «Afirmación del autor» y «¿Verificada?», lo que permite verificar de forma independiente las afirmaciones de revisión
- 3 archivos de referencia de marcos cognitivos que enseñan a los agentes «cómo pensar» y no solo «qué hacer»:
  - `argumentation_reasoning_framework.md` — modelo de Toulmin, razonamiento causal de Bradford Hill, inferencia a la mejor explicación, clasificación de estado epistémico
  - `review_quality_thinking.md` — tres lentes (validez interna, validez externa, contribución), trampas frecuentes del revisor, preguntas de calibración
  - `writing_judgment_framework.md` — prueba de claridad, recorrido del lector, voz según la disciplina, matriz de decisiones de revisión
- Protocolo de refuerzo a mitad de conversación: recordatorios de IRON RULE y anti-patrones específicos de cada etapa en cada transición del pipeline
- Preguntas de auto-comprobación en cada checkpoint FULL (integridad de las citas, concesión por sycophancy, trayectoria de calidad, disciplina de alcance, completitud)

**Oleada 3: tamaño contenido de las skills**
- El tamaño total de los SKILL.md se reduce de 142KB a 85KB (−40 %) al extraer los protocolos detallados a archivos en `references/`
- Se crean unos 15 archivos de referencia nuevos (protocolo de re-revisión, modo guiado, revisión sistemática, resumen de proceso, revisión externa, etc.)
- Todos los marcadores IRON RULE se conservan en el SKILL.md; el contenido detallado se carga bajo demanda
- Versiones nuevas: deep-research v2.7, academic-paper v2.8, academic-paper-reviewer v1.7, academic-pipeline v3.0

### v3.0 (2026-04-03) — Anti-sycophancy + detección de intención + salud del diálogo
- **Umbral de concesión del Devil's Advocate** (deep-research + academic-paper-reviewer): el DA debe puntuar las réplicas de 1 a 5 antes de responder. Concesión solo con ≥4. Sin concesiones consecutivas. Seguimiento de la tasa de concesión. Detección de frame-lock después de cada checkpoint.
- **Preservación de la intensidad de ataque** (academic-paper-reviewer): el DA no suaviza bajo presión. Protocolo de evaluación de réplicas con detección explícita de evasivas. Las reglas anti-sycophancy impiden que una insistencia del usuario se trate como evidencia válida.
- **Capa de detección de intención** (deep-research socratic): clasifica la intención del usuario como exploratoria u orientada a un objetivo. El modo exploratorio desactiva la auto-convergencia, sube el máximo de rondas y prohíbe cierres prematuros. Re-clasifica cada 3 turnos.
- **Indicador de salud del diálogo** (deep-research socratic): comprobación silenciosa cada 5 turnos de acuerdo persistente, evitación del conflicto y convergencia prematura. Inyecta desafíos automáticamente cuando detecta un patrón de acuerdo.
- **Entrada histórica de verificación entre modelos (sustituida por v3.16):** este release introdujo las comprobaciones muestrales de integridad y una crítica DA ejecutada de forma separada y a ciegas. Su diseño planificado de sexto revisor se retiró después; la revisión entre modelos actual cambia el sustrato de una de las plazas dentro del panel fijo de cinco. Consulta `shared/cross_model_verification.md` para el contrato actual de consentimiento y enrutamiento.
- **Informe de auto-reflexión de IA** (academic-pipeline, Etapa 6): autoevaluación posterior al pipeline de los patrones de comportamiento de la IA: tasa de concesión del DA, tasa de checkpoints saltados, alertas de salud, riesgo de sycophancy (LOW/MEDIUM/HIGH), incidentes de frame-lock y análisis del patrón de convergencia. Incluye la advertencia de ironía: «esta auto-reflexión la produce la misma IA que puede haber sido servil».
- Origen: descubierto en un experimento dialéctico de 4 rondas en el que el DA cedía demasiado rápido, el Socratic Mentor intentaba converger antes de tiempo y todo el debate quedaba encerrado en un marco definido por el humano.
- Versiones: deep-research v2.5, academic-paper-reviewer v1.5, academic-pipeline v2.8

### v2.9.1 (2026-04-03) — Metadatos de las skills
- Añadidos `status: active` y referencias cruzadas `related_skills` a los 4 frontmatters de SKILL.md.
- Permite herramientas de descubrimiento de skills y navegación entre skills a través de `deep-research` ↔ `academic-paper` ↔ `academic-paper-reviewer` ↔ `academic-pipeline`.

### v2.9 (2026-03-27) — Style Calibration + Writing Quality Check
- **Style Calibration** (paso 10 de la toma de datos de academic-paper, opcional): facilita 3 o más artículos anteriores y el pipeline aprende tu voz escrita: ritmo de las frases, preferencias de vocabulario y estilo de integración de citas. Se aplica como guía suave durante la redacción; las convenciones de la disciplina siempre tienen prioridad. Sistema de prioridades: normas de la disciplina (dura) > convenciones de la revista (fuerte) > estilo personal (suave). Consulta `shared/style_calibration_protocol.md`
- **Writing Quality Check** (`academic-paper/references/writing_quality_check.md`): lista de comprobación de calidad de escritura aplicada durante la auto-revisión del borrador. 5 categorías: avisos de términos frecuentes en IA (25 términos), control de patrones de puntuación (raya ≤3), detección de aperturas de preámbulo, avisos de patrones estructurales (regla de tres, párrafos uniformes, rotación de sinónimos) y comprobaciones de variación (longitud de frase variable). Son reglas de buena escritura, no evasión de detectores
- El **Style Profile** viaja con el Material Passport de academic-pipeline (Schema 10 en `shared/handoff_schemas.md`)
- El compilador de informes de **deep-research** también consume opcionalmente ambas funciones
- Versiones: academic-paper v2.5, deep-research v2.4, academic-pipeline v2.7

### v2.8 (2026-03-22) — Fase 1 del bucle SCR: State-Challenge-Reflect
- **Agente Socratic Mentor** (deep-research + academic-paper): integración del protocolo SCR (State-Challenge-Reflect)
  - **Puertas de compromiso**: recopilar las predicciones del usuario antes de presentar la evidencia en cada transición de capa o de capítulo
  - **Contradicción desencadenada por la certeza**: detectar lenguaje de alta confianza («obviously», «clearly») e introducir contraargumentos
  - **Intensidad adaptativa**: hacer un seguimiento de la exactitud de los compromisos y ajustar dinámicamente la frecuencia de los desafíos
  - **Señal de auto-calibración (S5)**: señal de convergencia nueva que mide el crecimiento de la auto-calibración del usuario a lo largo del diálogo
  - **Interruptor SCR**: el usuario puede decir «skip the predictions» para desactivarlo o «turn predictions back on» para reactivarlo a mitad del diálogo; el cuestionamiento socrático continúa con normalidad
- `deep-research/references/socratic_questioning_framework.md`: superposición SCR que mapea las fases de SCR a funciones socráticas
- Añadido `CHANGELOG.md`

### v2.7 (2026-03-09) — Verificación de integridad v2.0: renovación anti-alucinación
- **integrity_verification_agent v2.0**: mandato anti-alucinación (ninguna verificación desde la memoria de la IA), eliminadas las clasificaciones en zona gris (solo VERIFIED/NOT_FOUND/MISMATCH), rastro de auditoría obligatorio con WebSearch para cada referencia, verificación fresca e independiente en la Etapa 4.5 y regla de prevención de zona gris
- **Patrones conocidos de alucinación**: taxonomía de 5 tipos (TF/PAC/IH/PH/SH) del estudio GPTZero × NeurIPS 2025, 5 patrones de engaño compuesto, un caso real y estadísticas de la literatura
- **Auditoría posterior a la publicación**: la verificación completa con WebSearch de las 68 referencias encontró 21 problemas (31 % de tasa de error) que habían pasado 3 rondas de comprobaciones de integridad; demuestra la necesidad de la verificación externa
- **Correcciones al artículo**: retiradas 4 referencias fabricadas, corregidos 6 errores de autoría, 7 errores de metadatos y 2 problemas de formato

### v2.6.2 (2026-03-09) — Activación de modos por intención
- **deep-research**: el modo Socratic usa ahora **activación por intención** en lugar de coincidencia de palabras clave. Funciona en cualquier idioma: detecta el significado (por ejemplo, «el usuario quiere pensar guiado») en lugar de cadenas concretas.
- **academic-paper**: el modo Plan usa ahora **activación por intención**. Detecta señales como «el usuario no sabe por dónde empezar» o «el usuario quiere guía paso a paso» en cualquier idioma.
- Ambos modos tienen ahora una **regla por defecto**: cuando la intención es ambigua, se prefiere `socratic`/`plan` frente a `full`; es más seguro guiar primero.
- Arquitectura de dos capas: la Capa 1 (activación de la skill) usa palabras clave bilingües para dar confianza a la coincidencia; la Capa 2 (enrutamiento de modos) usa señales de intención independientes del idioma.

### v2.6.1 (2026-03-09) — Palabras clave de trigger bilingües
- **deep-research**: añadidas palabras clave en chino tradicional para la activación general y para el modo Socratic.
- **academic-paper**: añadidas palabras clave en chino tradicional y una sección de activación del modo Plan.
- Ambas guías de selección de modos incluyen ahora ejemplos bilingües y escenarios de selección errónea propios del chino.

### v2.6 / v2.4 / v1.4 (2026-03-08) — Más de 15 mejoras
- **deep-research v2.3**: modo nuevo de revisión sistemática / PRISMA (el séptimo); 3 agentes nuevos (risk_of_bias, meta_analysis, monitoring); plantillas de protocolo e informe PRISMA; criterios de convergencia socrática (4 señales + fin automático); guía rápida de selección de modos
- **academic-paper v2.4**: 2 agentes nuevos (visualization, revision_coach); plantilla de seguimiento de revisiones con 4 tipos de estado; conversión de formato de cita (APA↔Chicago↔MLA↔IEEE↔Vancouver); estándares de visualización estadística; criterios de convergencia socrática; ejemplo de recuperación de una revisión; **endurecimiento de la salida LaTeX**: clase de documento `apa7` obligatoria, corrección de la justificación del texto (`ragged2e` + `etoolbox`), fórmula de ancho de columnas de tablas, resumen bilingüe centrado, pila de fuentes estandarizada (Times New Roman + Source Han Serif TC VF + Courier New) y PDF solo mediante tectonic
- **academic-paper-reviewer v1.4 (histórico)**: introdujo la rúbrica numérica y el mapeo de decisiones que existían entonces. Las versiones actuales retiraron ese mecanismo en favor de juicios narrativos atados a criterios; las revisiones en vivo siguen siendo `NOT_CALIBRATED` y la aplicación de perfiles medidos todavía no está conectada. Se conserva la guía rápida de selección de modos.
- **academic-pipeline v2.6**: sistema de checkpoints adaptativos (FULL/SLIM/MANDATORY); verificación de afirmaciones de la Fase E dentro de las comprobaciones de integridad; Material Passport para procedencia en entradas parciales; asesor de modos entre skills (14 escenarios); protocolo de colaboración del equipo; esquemas de traspaso ampliados (9 esquemas); ejemplo de recuperación ante fallos de integridad

### v2.4 / v1.3 (2026-03-08)
- **academic-pipeline v2.4**: etapa nueva Stage 6 PROCESS SUMMARY: genera automáticamente un registro estructurado del proceso de creación del artículo (MD → LaTeX → PDF, bilingüe); capítulo final obligatorio: **Evaluación de la Calidad de la Colaboración** con 6 dimensiones puntuadas de 1 a 100 (definición de la dirección, contribución intelectual, custodia de la calidad, disciplina de iteración, eficiencia de la delegación, meta-aprendizaje), comentarios honestos y recomendaciones de mejora; el pipeline pasa de 9 a 10 etapas

### v2.3 / v1.3 (2026-03-08)
- **academic-pipeline v2.3**: Stage 5 FINALIZE ahora pregunta por el estilo de formateo (APA 7.0 / Chicago / IEEE); el PDF debe compilar desde LaTeX con `tectonic` (nada de HTML a PDF); APA 7.0 usa la clase de documento `apa7` (modo `man`) con XeCJK para soporte bilingüe de CJK; pila de fuentes: Times New Roman + Source Han Serif TC VF + Courier New

### v2.2 / v1.3 (2025-03-05)
- **Alineación de calidad entre agentes**: definiciones unificadas (peer-reviewed, regla de vigencia, severidad CRITICAL, nivel de la fuente) en todos los agentes
- **deep-research v2.2**: anti-patrones de síntesis, condiciones de fin automático del socrático, verificación con DOI + WebSearch, comprobación de ética e integridad reforzada y matriz de transición entre modos
- **academic-paper v2.2**: puntuación de argumentos en 4 niveles, detección de plagio, 2 rutas de fallo nuevas (F11 recuperación de desk-reject, F12 de congreso a revista) y conversión de modo Plan→Full
- **academic-paper-reviewer v1.3**: fronteras de rol entre el DA y el R3, criterios de hallazgo CRITICAL, clasificación del consenso (4/3/SPLIT/DA-CRITICAL), ponderación por puntuación de confianza y referencia de revistas asiáticas y regionales
- **academic-pipeline v2.2**: semántica de confirmación de checkpoints, matriz de cambio de modo, matriz de respaldo ante fallos, protocolo de propiedad del estado y control de versiones de materiales

### v2.0.1 (2026-03)
- **Simplificación de los 4 SKILL.md** (−371 líneas, −16,5 %): eliminada la duplicación entre skills, plantillas en línea → referencias a archivos, tablas de enrutamiento redundantes y secciones duplicadas de selección de modo
- Corregida la contradicción del límite del bucle de revisión entre academic-paper y academic-pipeline

### v2.0 (2026-02)
- **academic-pipeline v2.0**: 5→9 etapas, verificación de integridad obligatoria, revisión en dos fases, coaching socrático de revisiones y garantías de reproducibilidad
- **academic-paper-reviewer v1.1**: + Devil's Advocate Reviewer (7.º agente), + modo re-review (verificación) + coaching socrático posterior a la revisión
- Agente nuevo: `integrity_verification_agent` — verificación del 100 % de referencias y datos con rastro de auditoría
- Agente nuevo: `devils_advocate_reviewer_agent` — desafío de la tesis en 8 dimensiones
- Orden de salida: MD → DOCX mediante Pandoc cuando está disponible (si no, instrucciones) → se pregunta por LaTeX → confirmación → PDF

### v1.0 (2026-02)
- Publicación inicial
- deep-research v2.0 (10 agentes, 6 modos incluido socratic)
- academic-paper v2.0 (10 agentes, 8 modos incluido plan)
- academic-paper-reviewer v1.0 (6 agentes, 4 modos incluido guided)
- academic-pipeline v1.0 (orquestador)
