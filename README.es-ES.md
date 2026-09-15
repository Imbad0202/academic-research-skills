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

[**Wang, Li et al.**](https://arxiv.org/abs/2609.07713) (2026-09, *The Emerging AI Paper-Review Arms Race: Adversarial Co-Evolution in Scholarly Publishing*, una revisión de 230 fuentes) aporta una quinta ancla, y la primera que trata la producción de investigación y la revisión por pares como un único sistema acoplado. Su escalera de autoridad evaluativa (§4.1) va desde la retroalimentación dirigida al autor, pasando por la asistencia al revisor y las reseñas oficiales por IA, hasta la puntuación y el apoyo a la decisión, con la observación de que la capacidad en un peldaño no justifica el uso en el siguiente; el panel simulado de ARS se sitúa por diseño en el peldaño más bajo (consulta `POSITIONING.md`). Dos de sus hallazgos dan forma a la hoja de ruta del revisor. Primero, según la revisión resume a Dycke & Gurevych (2026, §4.5), 391 ediciones que rompen las relaciones de soporte científico de un artículo no produjeron diferencias estadísticamente significativas en los aspectos, el sentimiento ni las puntuaciones de los revisores automáticos probados, en comparación con 540 controles neutrales respecto a la solidez, mientras que reescrituras solo de presentación, con la ciencia fija, movieron las puntuaciones de las reseñas por IA (§5.2); la conclusión del §9.2 es que una evaluación estática puede sobreestimar la fiabilidad de un revisor por IA una vez que los autores pueden observarlo y adaptarse a él. ARS sigue los controles pareados de la Ronda 1 correspondientes en #871 y los controles de señales de identidad del autor (§7.2) en #872; ambos son mediciones, no mecanismos nuevos. Segundo, su §9.1 cita a Brodeur et al. (2026, *PNAS* 123(22):e2524747123), un estudio aleatorizado en el que 288 investigadores en 103 equipos reprodujeron resultados publicados de ciencias sociales cuantitativas bajo tres condiciones: solo humanos, asistidos por IA (ChatGPT como herramienta colaborativa) y dirigidos por IA (ChatGPT con supervisión humana mínima). Los equipos solo humanos y los asistidos por IA reprodujeron el 94 % y el 91 %, los equipos dirigidos por IA el 37 %, y los equipos asistidos por IA detectaron menos errores de código graves que los equipos solo humanos. En ese estudio, por tanto, la asistencia de IA no verificó mejor que los humanos solos y la verificación dirigida por IA lo hizo mucho peor; ARS lo lee como una razón para mantener la verificación dirigida por humanos en cada punto de control, no como evidencia de que sus propios puntos de control o puertas de integridad sean eficaces. La revisión es una síntesis y no un experimento, su búsqueda estructurada se detiene el 2026-07-01 y la actualización dirigida posterior no repitió todas las consultas (§10), su evidencia de despliegue se concentra en un pequeño número de conferencias de IA/CS, entornos basados en OpenReview y revistas seleccionadas y su marco de «carrera armamentística» es una lente, no un hallazgo; ARS la cita como justificación de diseño, no como evidencia sobre la salida de ARS.

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
- *Opcional (Python real):* solo lo necesitan el guard de write-scope y algunos comandos opcionales; las skills principales están guiadas por prompts. Los detalles, incluidas las notas para Windows sobre Git Bash y el marcador de posición de Python de la Microsoft Store, están en [docs/SETUP.md § Python (optional)](docs/SETUP.md#python-optional) (en inglés).

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

Aquí solo se resumen las tres versiones más recientes. El historial completo está en [CHANGELOG.md](CHANGELOG.md) (en inglés). Los resúmenes en español hasta la v3.21.2 se conservan congelados en [docs/changelog-archive/es-ES.md](docs/changelog-archive/es-ES.md) y no se actualizarán.

### v3.21.2 (2026-09-06) — Actualización de modelos a Fable 5.1 y GPT-6 Astra, procedencia de las decisiones en checkpoints y reparaciones de coincidencia de títulos CJK

> **Actualidad y procedencia, no capacidad nueva:** v3.21.2 alinea el conjunto con las dos system cards de vendor de septiembre de 2026. `gpt-6-astra` entra en la tabla de modelos cruzados como provisional en ambos transportes y pasa a ser el verificador de OpenAI recomendado según la política de actualidad de generación; `gpt-5.6-sol` conserva su estado validated en el transporte de citas con suscripción a ChatGPT, y no se reclama ningún resultado nuevo de bakeoff. El conjunto de reasoning-effort del transporte Codex contenido gana `ultra`. Se añaden dos salvaguardas, ambas a nivel de prompt y motivadas por el vendor y no por mediciones de ARS: la procedencia de las decisiones en checkpoint (solo un turno de usuario es una decisión; las decisiones se retransmiten a los subagentes literalmente; riesgo R11) y la monitorización del proveedor o las intervenciones de seguridad del proveedor, que se nombran como fallo del transporte y nunca como veredicto. La auditoría de retirada de harness contra ambas cards no retira nada (0 retiradas de texto de prompt; 8 elementos keep-as-debt pasan a llevar cita de la card). Correcciones: los títulos CJK ya no fallan la puerta de título exacto en los cuatro resolutores de índices (#798) y las marcas de envoltorio se eliminan solo como una unidad balanceada (#800); el test de ida y vuelta de autolinks declara su dependencia (#801); `check_surface_form_parity` señala un entorno roto en lugar del manifiesto; un lint de paridad del inventario de skills (#809); la brecha residual R10 se actualiza (#813); y se corrige una línea de reglas clave de MLA (#805). Suite/pipeline → v3.21.2; deep-research → v2.12.1; academic-paper → v3.3.1; academic-paper-reviewer → v1.11.1.

### v3.21.1 (2026-08-24) — Sustratos de workflow acotados, bakeoffs sellados y endurecimiento del transporte

> **Medido donde se indica; en otro caso, acotado:** v3.21.1 repara el transporte de citas con suscripción a ChatGPT contenido para codex-cli 0.147.0 y registra el primer Promotion Bakeoff: `gpt-5.6-sol` queda validado solo para ese transporte de suscripción y sigue siendo provisional en la ruta de API first-party. Los futuros bakeoffs requieren preregistro sellado. El release añade además un sustrato de perfil de workflow de investigación desactivado por defecto (solo conformidad determinista sin conexión; sin hook en el pipeline ni perfiles publicados por familia), un alpha de opt-in inquiry-ledger (`ARS_INQUIRY_LEDGER=1`) y un registro de alternativas solo de diseño que no está implementado. Su evidencia conductual sigue siendo `NOT_RUN`; no se reclama ningún beneficio en usabilidad, recuperación, novedad, corrección ni resultados de investigación. El registro de criterios de revisión gana un conjunto probatorio ilustrativo de perfil exacto para MSR 2027, respaldado por la fuente: no es cobertura de venues ni de disciplinas, ni una atestación de autores reales, ni evidencia de revisión constructiva, y la evaluación humana independiente obligatoria que lo acompaña sigue pendiente. Los cambios adicionales alinean `data_access_level`, consolidan la gramática del lint de markdown, registran las degradaciones del lanzador de la guarda y listan OrcaRouter como integración comunitaria sin aval. Suite/pipeline → v3.21.1; deep-research → v2.12.1; academic-paper → v3.3.1; academic-paper-reviewer → v1.11.1.

### v3.21.0 (2026-08-18) — Transparencia, verificabilidad y pista de viabilidad al estilo ISO/IEC 42001

> **Transparencia que puedes comprobar:** v3.21.0 completa la pista de auditoría al estilo ISO/IEC 42001 (#753–#760). Las afirmaciones hacia fuera se alinean con el registro de evidencia, y cuatro artefactos permanentes responden ahora a las preguntas que de verdad hacen los usuarios: qué controles operan en tu canal de instalación (`docs/CONTROL_AVAILABILITY.md`), qué sale de tu máquina y qué se almacena (`docs/DATA_FLOWS.md`), con qué fuerza aplica realmente cada workflow de CI (`docs/ARCHITECTURE.md` §7.1) y a qué riesgo responde cada mecanismo, con qué evidencia y qué brecha residual (`docs/RISK_REGISTER.md`); cada uno defendido por su propio lint de CI. `GOVERNANCE.md` explicita la autoridad de decisión, qué aporta y qué no aporta la revisión entre modelos (un control de detección de errores, no independencia organizativa) y la postura de fin de vida; `SECURITY.md` gana un procedimiento de triage por severidad ejecutable por una sola persona. Son principios operativos destilados con anclas informativas a ISO/IEC 42001, no una reclamación de certificación, y no se reclaman cifras nuevas de eficacia. Suite/pipeline → v3.21.0; deep-research → v2.12.1; academic-paper → v3.3.1; academic-paper-reviewer → v1.11.1.
