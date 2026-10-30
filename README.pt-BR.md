# Academic Research Skills para Claude Code

[![Version](https://img.shields.io/badge/version-v3.24.0-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v3.24.0)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20696614-blue)](https://doi.org/10.5281/zenodo.20696614)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Sponsor](https://img.shields.io/badge/sponsor-Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/crucify020v)

[English](README.md) | [简体中文版](README.zh-CN.md) | [繁體中文版](README.zh-TW.md) | [日本語版](README.ja-JP.md) | [한국어](README.ko-KR.md) | [Español](README.es-ES.md)

Um conjunto completo de skills do Claude Code para pesquisa acadêmica, que cobre todo o fluxo, da pesquisa à publicação.

**Instale em 30 segundos** (Claude Code CLI / VS Code / JetBrains, v3.7.0+):

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

Depois experimente `/ars-plan` para planejar a estrutura do seu artigo por meio de um diálogo socrático, ou vá direto para [Instalação rápida](#instalação-rápida) para ver os pré-requisitos e o fluxo tradicional com links simbólicos.

> **A IA é sua copiloto, não a piloto.** Ela pode redigir textos, inclusive um artigo inteiro no modo full, mas as decisões continuam sendo suas, e o pipeline para em cada etapa para pedir sua confirmação. Ela cuida do trabalho braçal (caçar referências, formatar citações, verificar dados, checar a coerência lógica) para que você se concentre no que realmente exige a sua cabeça: definir a pergunta, escolher o método, interpretar o que os dados significam e decidir o que vem depois de "defendo que". A autoria continua sendo sua, e você responde por cada afirmação que submeter.
>
> Diferentemente de um "humanizador", esta ferramenta não ajuda você a esconder que usou IA. Ela ajuda você a escrever melhor. O Style Calibration aprende a sua voz a partir de trabalhos anteriores. O Writing Quality Check identifica os padrões que fazem um texto parecer gerado por máquina. O objetivo é qualidade, não trapaça.

### Por que um humano no circuito, e não automação total?

Lu et al. (2026, *Nature* 651:914-919) criaram **The AI Scientist**, o primeiro sistema de pesquisa totalmente autônomo a publicar um artigo após revisão por pares cega em um evento de ponta de machine learning (workshop da ICLR 2025, nota 6,33/10 contra uma média de 4,87 no workshop). A seção de Limitações enumera os modos de falha que qualquer pipeline de pesquisa totalmente autônomo herda: bugs de implementação, resultados alucinados, dependência de atalhos, bugs reinterpretados como descobertas, fabricação de metodologia, frame-lock e citações alucinadas.

O ARS parte da premissa de que **um pesquisador humano ampliado pela IA evita esses modos de falha melhor do que qualquer um dos dois sozinho**. Os gates de integridade da Etapa 2.5 e da Etapa 4.5 aplicam uma checklist bloqueante de 7 modos (veja [`academic-pipeline/references/ai_research_failure_modes.md`](academic-pipeline/references/ai_research_failure_modes.md)); o revisor oferece um modo de calibração opcional que mede o próprio FNR/FPR em relação a um gold set fornecido pelo usuário.

[**Zhao et al.**](https://arxiv.org/abs/2605.07723) (2026-05) auditaram 111 milhões de referências em 2,5 milhões de artigos do arXiv, bioRxiv, SSRN e PMC. A estimativa conservadora é de 146.932 citações alucinadas só em 2025, com um ponto de inflexão observado em meados de 2024; para o par bioRxiv-PMC, relatam persistência de 85,3% do preprint até a versão publicada. O artigo descreve como desafio em aberto o uso de "citações reais empregadas para sustentar afirmações que as referências citadas não fazem de fato". O ARS v3.7.1 acrescentou frontmatter de cadeia de confiança (trust-chain) para registrar a procedência das fontes; a v3.7.3 acrescentou infraestrutura de localizadores (âncoras de citação em três camadas) para futuras auditorias no nível da afirmação e passou a exibir sinais de risco consultivos no momento da citação (internamente, o ARS chama essa lacuna de fidelidade entre afirmação e fonte de "L3"; é terminologia do ARS, não do artigo). A série v3.7.x é motivada pelos achados de Zhao et al. em escala de corpus; a avaliação do próprio ARS nessa escala continua sendo trabalho futuro.

A v3.8 fecha a segunda metade da lacuna L3. A v3.7.3 fez com que toda citação carregasse uma âncora de localização; a v3.8 acrescenta uma etapa de auditoria opcional (`ARS_CLAIM_AUDIT=1`) que busca a fonte citada a partir de cada âncora e julga se a afirmação é de fato sustentada. Cinco novas classes HIGH-WARN (claim-not-supported, negative-constraint-violation, fabricated-reference, anchorless, constraint-violation-uncited) fazem o gate final rígido do formatter recusar a saída. Um runner de calibração acompanha um gold set sintético de 25 tuplas, com limiares de aceitação FNR<0,15 + FPR<0,10. O teste incluído executa o runner com um juiz simulado que devolve os rótulos do gold set, então ele verifica a ferramenta, não um juiz real; ainda não há resultado de calibração com juiz real registrado, e o plano de ativação gradual aguarda esse resultado (especificação da v3.8, §5).

[**Ren et al.**](https://arxiv.org/abs/2607.13104) (2026, *Self-Improvements in Modern Agentic Systems: A Survey*) fornecem uma terceira âncora, no nível de survey. A síntese sobre descoberta científica (§7.4) conclui que agentes de descoberta não conseguem verificar facilmente, por conta própria, novidade, correção ou reprodutibilidade, e podem recorrer a proxies fracos; precisam gerenciar evidências entre ferramentas e literaturas heterogêneas; e levantam questões de governança: "a escrita científica também pode amplificar a desinformação quando a evidência é fraca". Os capítulos sobre o ciclo de geração (§5.1–§5.2) incluem a auditoria humana e a manutenção de âncoras humanas entre as salvaguardas práticas para ciclos de avaliação autogerados, e o capítulo histórico (§2.2) registra a forma mais antiga da mesma lição: o sucesso prático do EURISKO, de Lenat, dependia muito de o usuário atuar como sinal externo de avaliação, podando a deriva improdutiva de heurísticas — uma limitação que, segundo o survey, persiste nos sistemas agênticos modernos. O ARS cita o survey como justificativa de projeto para sua postura de humano no circuito, não como prova empírica de que pipelines com humano no circuito superam os autônomos; as melhorias acionáveis que o survey sugere para o ARS são acompanhadas em #539–#541 e #547–#550.

[**Gartenberg et al.**](https://doi.org/10.1287/orsc.2026.ed.v37.n3) (2026, *Organization Science* 37(3):795-812, "More versus better") fornecem uma quarta âncora, e a primeira do lado dos periódicos. A AI Task Force da *Organization Science* pontuou todas as primeiras submissões (6.957) e todos os pareceres em formato de texto (10.389) que o periódico recebeu entre janeiro de 2021 e fevereiro de 2026, usando um classificador comercial de escrita por IA e índices padrão de legibilidade. Manuscritos classificados como fortemente escritos por IA tiveram leitura pior nesses índices e foram rejeitados sem revisão (desk reject) com mais frequência; pareceres classificados como mais escritos por IA tenderam para a teoria e se afastaram dos dados; e os editores concluem que as ferramentas de IA atuais, amplificadas pelos incentivos do "publique ou pereça", "parecem estar empurrando o sistema para um equilíbrio de mais pesquisa, e não de pesquisa melhor". A §5 contrasta a "rendição cognitiva" (Shaw & Nave, 2026, conforme citado ali) com um uso que coloca o humano em primeiro lugar e pede que os autores declarem como o manuscrito foi produzido. A evidência é observacional, agregada e de um único periódico, e o classificador é um instrumento proprietário. O ARS cita o editorial como justificativa de projeto para registrar o volume como não objetivo (veja `POSITIONING.md`) e para o Collaboration Depth Observer e a escala de força das afirmações, não como evidência sobre a saída do ARS; as melhorias acionáveis são acompanhadas em #829–#833.

[**Wang, Li et al.**](https://arxiv.org/abs/2609.07713) (2026-09, *The Emerging AI Paper-Review Arms Race: Adversarial Co-Evolution in Scholarly Publishing*, uma revisão de 230 fontes) fornecem uma quinta âncora, e a primeira que trata a produção de pesquisa e a revisão por pares como um único sistema acoplado. A escala de autoridade avaliativa (§4.1) vai do feedback voltado ao autor, passando pela assistência ao revisor e por pareceres oficiais de IA, até a pontuação e o apoio à decisão, com o argumento de que a capacidade em um degrau não justifica o uso no seguinte; o painel simulado do ARS fica, por projeto, no degrau mais baixo (veja `POSITIONING.md`). Dois achados orientam o roteiro do revisor. Primeiro, conforme a revisão resume Dycke & Gurevych (2026, §4.5), 391 edições que quebram as relações de sustentação científica de um artigo não produziram diferença estatisticamente significativa nos aspectos, no sentimento ou nas notas dos revisores automáticos testados, em comparação com 540 controles neutros quanto à solidez, enquanto reescritas apenas de apresentação, com a ciência mantida fixa, alteraram as notas dos pareceres de IA (§5.2); a conclusão da §9.2 é que uma avaliação estática pode superestimar a confiabilidade de um revisor de IA quando os autores podem observá-lo e se adaptar a ele. O ARS acompanha os controles pareados correspondentes da Rodada 1 em #871 e os controles de indícios de identidade do autor (§7.2) em #872; ambos são medições, não mecanismos novos. Segundo, a §9.1 cita Brodeur et al. (2026, *PNAS* 123(22):e2524747123), um estudo randomizado em que 288 pesquisadores, em 103 equipes, reproduziram resultados publicados de ciências sociais quantitativas em três condições: só humanos, assistidos por IA (ChatGPT como ferramenta colaborativa) e conduzidos por IA (ChatGPT com supervisão humana mínima). As equipes só de humanos e as assistidas por IA reproduziram 94% e 91%, as conduzidas por IA, 37%, e as equipes assistidas por IA detectaram menos erros graves de código do que as equipes só de humanos. Nesse estudo, portanto, a assistência da IA não verificou melhor do que os humanos sozinhos, e a verificação conduzida por IA se saiu muito pior; o ARS lê isso como um motivo para manter a verificação conduzida por humanos em cada checkpoint, não como evidência de que seus próprios checkpoints ou gates de integridade sejam eficazes. A revisão é uma síntese, não um experimento; sua busca estruturada vai até 2026-07-01, e a atualização direcionada posterior não repetiu todas as consultas (§10); sua evidência de uso real se concentra em poucas conferências de IA/Computação, ambientes baseados no OpenReview e periódicos selecionados; e o enquadramento de "corrida armamentista" é uma lente, não um achado. O ARS a cita como justificativa de projeto, não como evidência sobre a saída do ARS.

[**King & Worthington**](https://gking.harvard.edu/peerless) (2026-10, *AI Article Reviews Dominate Human Peer Reviews at Their Best: Evidence and Policy Choices*) fornecem uma sexta âncora, e a primeira que compara diretamente pareceres de IA e pareceres humanos sobre os mesmos manuscritos. Com 124 manuscritos e 134 pareceres pagos de especialistas de um serviço de revisão pré-submissão, muito bem avaliados pelos autores, o Claude Opus 4.8 escreveu um parecer por manuscrito em cada uma de duas condições, com esforço máximo de raciocínio. Um juiz GPT-5.5 preferiu o parecer da IA em todos os pares decididos, com cada par julgado nas duas ordens de apresentação, e três ex-editores de periódicos o preferiram em 26 de 30 julgamentos cegos. Em uma replicação que usou as duas famílias de modelos como revisoras e como juízas, o parecer da IA foi preferido em 404 de 416 comparações (97,1%) pelo juiz Opus e em 392 de 416 (94,2%) pelo juiz GPT. Dois resultados dizem respeito ao revisor do ARS. Na área de fontes adicionais (dados, teoria ou literatura alternativos), o parecer da IA venceu 62% dos pares decididos sem busca na web (n=85) e 100% com ela (n=99), e o revisor de domínio do ARS recomenda literatura sem buscá-la nem verificá-la (#1001). Os pareceres da IA também não estavam livres de erros: na condição sem ferramentas, 5,5% das avaliações de afirmações da IA foram julgadas contraditas pelo manuscrito, contra 15,9% nos pareceres humanos, e 37,1% dos pareceres de IA tinham pelo menos uma afirmação assim; o ARS não confronta as afirmações do seu painel com o manuscrito (#1002). A seção de políticas do artigo descreve autores que iteram com um prompt de revisão por IA publicado e respondem a ele em uma carta, algo próximo do uso para o qual o ARS foi projetado, e alerta que autores que revisam pensando em um prompt publicado podem acabar otimizando para ele, deixando vieses alheios à qualidade da ciência. Os limites do estudo enquadram a forma como o ARS o lê: um único serviço de revisão, um único modelo juiz na análise principal, editores que julgaram apenas a partir dos pareceres, nenhuma medida de se os artigos revisados melhoraram, e resultados que, nas palavras dos autores, "do not speak to" (não tratam de) como os editores devem tomar decisões de publicação. Este último limite coincide com o lugar que o `POSITIONING.md` atribui ao painel do ARS. Este artigo e o resultado de Dycke & Gurevych citado acima tratam de perguntas diferentes: aqui, a preferência entre pareceres e sua fundamentação factual; lá, a sensibilidade a mudanças na solidez do manuscrito; por isso, nenhum dos dois resultados responde ao outro. O ARS cita o artigo como justificativa de projeto, não como evidência sobre a saída do ARS.

A v3.3 foi inspirada no [**PaperOrchestra**](https://arxiv.org/abs/2604.05018) (Song, Song, Pfister & Yoon, 2026, Google): verificação pela API do Semantic Scholar, protocolo antivazamento, verificação de figuras com VLM e acompanhamento da trajetória das revisões. Hoje o ARS implementa esta última ideia por meio de trajetórias de critérios categóricas e ancoradas em evidências, em vez de diferenças de nota.

---

## Arquitetura e pipeline

**👉 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — a visão completa do pipeline: diagrama de fluxo, matriz etapa por etapa, fluxo de acesso a dados, grafo de dependências entre skills, gates de qualidade e lista de modos.

O documento de arquitetura substitui a longa descrição do pipeline que ficava aqui. Tudo sobre *o que roda em cada etapa* agora está em um só lugar.

## Instalação rápida

**Pré-requisitos**

- [Claude Code](https://docs.claude.com/en/docs/claude-code/setup) (versão mais recente; o empacotamento como plugin exige versões recentes)
- `ANTHROPIC_API_KEY` exportada, ou definida na primeira execução do `claude`
- *Opcional:* Pandoc para DOCX, tectonic + Source Han Serif TC para PDF em APA 7.0 (a saída em Markdown funciona sem nenhum dos dois)
- *Opcional (Python de verdade):* necessário apenas para o guard de write-scope e alguns comandos opcionais; as skills principais são guiadas por prompts. Os detalhes, incluindo as observações para Windows sobre o Git Bash e o atalho falso de Python da Microsoft Store, estão em [docs/SETUP.md § Python (optional)](docs/SETUP.md#python-optional) (em inglês).

> **Quais controles estão ativos no *seu* canal de instalação?** A disponibilidade varia conforme o canal de instalação. Veja o mapa por canal: [docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md).

**Instalação como plugin (v3.7.0+, recomendada):**

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

**Confira se funciona:** execute `/ars-plan` e descreva um artigo em que você esteja trabalhando; o ARS vai iniciar um diálogo socrático para mapear a estrutura dos capítulos. Para um teste de uma só vez, experimente `/ars-lit-review "your topic"`.

**👉 [docs/SETUP.md](docs/SETUP.md)** — guia completo: instalar o Claude Code, configurar chaves de API, Pandoc/tectonic opcionais para DOCX/PDF, verificação entre modelos (`ARS_CROSS_MODEL`) e seis métodos de instalação (plugin, skills de projeto, skills globais, claude.ai Project, repositório clonado e importação no Claude Science).

**👉 [docs/DATA_FLOWS.md](docs/DATA_FLOWS.md)** — o que sai da sua máquina (resolvedores bibliográficos, chamadas opcionais entre modelos que exigem consentimento, a verificação de atualização do plugin), o que fica em cache localmente, por quanto tempo e como desativar cada caminho.

**👉 [docs/RISK_REGISTER.md](docs/RISK_REGISTER.md)** — os riscos permanentes conhecidos pelo conjunto, quais controles existentes tratam de cada um, o estado das evidências por trás desses controles e o que continua em aberto.

**Usa o Claude Science?** As cinco skills podem ser importadas diretamente: **Skills → Import from GitHub**, cole `https://github.com/Imbad0202/academic-research-skills`, clique em **Preview** e depois em **Import** (exige a v3.14.0+ deste repositório: o importador lê os caminhos explícitos das skills no manifesto do marketplace). As importações são retratos de um momento: importe de novo depois que o ARS for atualizado. As skills importadas trazem a metodologia do ARS (protocolos de pesquisa / escrita / revisão); a maquinaria específica do Claude Code — comandos de barra, hooks, orquestração de subagentes — não é transferida. Veja o Método 5 em [docs/SETUP.md](docs/SETUP.md) para mais detalhes.

**Usa o Pi?** Instale o wrapper mantido pela comunidade dentro deste repositório com `pi install git:github.com/Imbad0202/academic-research-skills`. Ele mantém o conteúdo original do ARS como referência oficial e documenta a orquestração específica do Pi e as limitações de hooks. Veja [`pi/README.md`](pi/README.md).

**Usa o Codex CLI?** Instale, em vez disso, a distribuição irmã: [`Imbad0202/academic-research-skills-codex`](https://github.com/Imbad0202/academic-research-skills-codex) — o mesmo conteúdo de fluxo de trabalho, empacotado de forma nativa para o Codex como uma única skill `$academic-research-suite` com aliases `ars-*`.

**Plataformas e integrações de terceiros** que encapsulam ou hospedam o ARS estão listadas em [THIRD_PARTY.md](THIRD_PARTY.md) — enviadas pela comunidade e não revisadas nem endossadas pelo mantenedor.

**Governança:** quem decide, o que a revisão entre modelos oferece e o que não oferece, e a postura de fim de vida do projeto estão descritos em [GOVERNANCE.md](GOVERNANCE.md); a comunicação e a triagem de problemas de segurança, em [SECURITY.md](SECURITY.md).

## Desempenho e custo

**👉 [docs/PERFORMANCE.md](docs/PERFORMANCE.md)** — orçamentos de tokens por modo, estimativa do pipeline completo (cerca de US$ 3–7 para um artigo de 15 mil palavras, a preços de tabela de 2026-09, antes dos descontos de cache) e configurações recomendadas do Claude Code (Auto mode; Agent Team opcional).

## Guias e artigos

- [Academic Writing Shouldn't Be a Solo Act](https://open.substack.com/pub/edwardwu223235/p/academic-writing-shouldnt-be-a-solo?r=4dczl&utm_medium=ios) — passo a passo completo do pipeline (em inglês)
- [學術寫作不該是一個人的事：一套開源 AI 協作工具如何改變研究者的工作流](https://open.substack.com/pub/edwardwu223235/p/ai?r=4dczl&utm_medium=ios) — 完整使用指南（繁體中文）

---

## Recursos em resumo

- **Deep Research** — equipe de pesquisa com 13 agentes, com modo guiado socrático, revisão sistemática PRISMA, detecção de intenção, monitoramento da saúde do diálogo, DA opcional entre modelos e verificação pela API do Semantic Scholar.
- **Academic Paper** — escrita de artigos com 12 agentes, com Style Calibration, Writing Quality Check, LaTeX reforçado, visualização, orientação para revisões, conversão de citações, protocolo antivazamento e verificação de figuras com VLM.
- **Academic Paper Reviewer** — revisão por pares com múltiplas perspectivas e 7 agentes, com julgamentos narrativos vinculados a critérios e ancorados em evidências (Journal-Fit Reviewer + 3 revisores dinâmicos + Devil's Advocate), protocolo de limiar de concessão, preservação da intensidade de ataque, crítica / calibração opcional do DA entre modelos, matriz de rastreabilidade de R&R e restrição de somente leitura. As revisões em produção continuam `NOT_CALIBRATED`; a calibração completa gera um perfil candidato delimitado, mas a aplicação desse perfil em produção ainda não está conectada.
- **Academic Pipeline** — orquestrador de pipeline de 10 etapas, com checkpoints adaptativos, verificação de afirmações, Material Passport, `repro_lock` opcional, verificação de integridade opcional entre modelos, reforço no meio da conversa e verificações narrativas de regressão critério a critério (o portador tipado de trajetórias foi adiado).
- **SR-Screener** — triagem de estudos guiada por protocolo para revisões sistemáticas, de escopo e rápidas: dois revisores de IA cegos mais um terceiro revisor que resolve divergências, códigos de exclusão ordenados, nenhuma decisão padrão silenciosa, execuções em lote retomáveis, controle de qualidade (estudos-semente, rechecagem de casos limítrofes, kappa e PABAK), contagens PRISMA 2020, grupos RIS para EndNote/Zotero e entrega de um `literature_corpus[]` ao `academic-paper`. As decisões da IA são apoio à decisão; a equipe de revisão as verifica.
- **Metadados de nível de acesso a dados** (v3.3.2+) — cada skill declara `data_access_level` (`raw` / `redacted` / `verified_only`); a regra é aplicada por `scripts/check_data_access_level.py`. Padrão adaptado do automated-w2s-researcher da Anthropic (2026). Veja [`shared/ground_truth_isolation_pattern.md`](shared/ground_truth_isolation_pattern.md).
- **Anotação de tipo de tarefa** (v3.3.2+) — cada skill declara `task_type` (`open-ended` ou `outcome-gradable`). Todas as skills atuais do ARS são `open-ended`.
- **Schema de relatório de benchmark** (v3.3.5+) — JSON Schema + lint para comparações de benchmark honestas. Veja [`shared/benchmark_report_pattern.md`](shared/benchmark_report_pattern.md).
- **Lockfile de reprodutibilidade de artefatos** (v3.3.5+) — sub-bloco `repro_lock` opcional no Material Passport. **É documentação de configuração, não garantia de repetição exata**: as saídas de LLMs não são reproduzíveis byte a byte. Veja [`shared/artifact_reproducibility_pattern.md`](shared/artifact_reproducibility_pattern.md).
- **Níveis de modelo** (#517, v3.16+) — chave opcional `ARS_MODEL_TIERING` com duas direções: `economy` (agentes de execução rodam um nível abaixo do modelo da sessão, com piso na classe Opus) e `quality-boost` (agentes de julgamento nos gates de integridade e na revisão final sobem para o nível de fronteira). Sem valor definido = comportamento idêntico, byte a byte, ao anterior a #517. Veja [`shared/model_tiering.md`](shared/model_tiering.md).
- **Envelope canônico de transferência entre modelos** (#527, v3.17+) — o caminho de transporte dos checkpoints cegos owner→dispatcher→owner (#523) agora tem um envelope `[CROSS-MODEL-HANDOFF v1]` estável e legível por máquina, com uma gramática normativa em Python (`scripts/cross_model_handoff.py`) em vez de regras só em texto, fixando o roteamento de concordância / divergência / resultado malformado entre os três responsáveis por checkpoints. Veja [`shared/cross_model_verification.md`](shared/cross_model_verification.md), §"Cross-model handoff envelope".
- **Registro de procedência de experimentos** (#260) — o campo opcional `experiment_provenance[]` do Material Passport registra experimentos que o pesquisador executou **externamente** (o ARS nunca executa experimentos), e as afirmações do manuscrito se ligam a eles por meio de `claim_intent_manifest.planned_experiment_ids[]`. O gate de integridade (Etapa 2.5/4.5) audita cada afirmação apoiada em experimento em relação à procedência declarada — `ALIGNED` / `OVERSTATED` / `NOT_SUPPORTED_BY_PROVENANCE` / `PROVENANCE_INSUFFICIENT` — **sem julgar se o experimento em si estava correto**. Um `experiment_intake_declaration` fail-closed transforma "você executou experimentos?" em uma decisão explícita que o pesquisador toma depois da Etapa 1, ou na entrada, quando uma execução começa mais adiante (até execuções só com literatura declaram `no_experiments_declared`). Veja [`shared/handoff_schemas.md`](shared/handoff_schemas.md), §"Experiment Provenance Intake (#260)".

**Limite da integridade e da verificação:** o ARS verifica o manuscrito e o processo relatado — incluindo a existência das citações, o alinhamento entre afirmação e fonte, a metodologia relatada, o alinhamento declarado entre experimento e resultado, a fidelidade de figuras e tabelas e a conformidade de relato, processo e pacote. Algumas verificações são feitas por amostragem ou por meio de LLM. O ARS **não** comprova que os procedimentos foram de fato realizados, que os dados brutos são autênticos ou que os resultados se reproduzem; uma fabricação relatada de forma coerente pode passar por essas verificações. Veja [POSITIONING.md § Integrity checks and the empirical-work boundary](POSITIONING.md#integrity-checks-and-the-empirical-work-boundary).

---

## Vitrine: saída real do pipeline

Veja os artefatos completos de uma execução real do pipeline, incluindo pareceres de revisão por pares, relatórios de verificação de integridade e o artigo final:

> **Um registro de março de 2026, não o desempenho atual.** Esta execução (de 2026-03-07 a 03-08) usou o academic-pipeline v2.3, antes de o ARS acrescentar a verificação pelo Semantic Scholar na v3.3 e o gate determinístico de citações com quatro índices na v3.11. Os números descrevem aquela versão; os gates atuais não foram medidos com este artigo. A autoria aparece em nome do Claude (Anthropic) porque o pesquisador pediu isso durante o experimento. O artigo não é uma publicação da Anthropic, e a posição do ARS é que a ferramenta não substitui o pesquisador nem reivindica autoria ([POSITIONING.md](POSITIONING.md#what-this-is-not)).

**[Ver todos os artefatos do pipeline →](examples/showcase/)**

| Artefato | Descrição |
|---|---|
| [Final Paper (EN)](examples/showcase/full_paper_apa7.pdf) | Formatado em APA 7.0, compilado em LaTeX |
| [Final Paper (ZH)](examples/showcase/full_paper_zh_apa7.pdf) | Versão em chinês, APA 7.0 |
| [Integrity Report — Pre-Review](examples/showcase/integrity_report_stage2.5.pdf) | Etapa 2.5: apontou 15 referências com problemas (8 com erros bibliográficos, 6–8 provavelmente fabricadas) + 3 erros estatísticos |
| [Integrity Report — Final](examples/showcase/integrity_report_stage4.5.pdf) | Etapa 4.5: zero regressões confirmadas |
| [Peer Review Round 1](examples/showcase/stage3_review_report.pdf) | Journal-Fit Reviewer + 3 revisores + Devil's Advocate |
| [Re-Review](examples/showcase/stage3prime_rereview_report.pdf) | Verificação após as revisões |
| [Peer Review Round 2](examples/showcase/stage3_review_report_r2.pdf) | Revisão de acompanhamento |
| [Response to Reviewers](examples/showcase/response_to_reviewers_r2.pdf) | Resposta ponto a ponto dos autores |
| [Post-Publication Audit Report](examples/showcase/post_publication_audit_2026-03-09.pdf) | Auditoria de todas as referências feita à parte com Claude Code + WebSearch: 21 das 68 referências finais ainda tinham problemas após 3 rodadas de verificação de integridade |

---

## Complemento: Experiment Agent

Se a sua pesquisa envolve executar experimentos (código ou estudos com pessoas) antes da escrita, a skill [Experiment Agent](https://github.com/Imbad0202/experiment-agent) preenche a lacuna entre a Etapa 1 (RESEARCH) e a Etapa 2 (WRITE) do ARS.

```
ARS Stage 1 RESEARCH  →  RQ Brief + Methodology Blueprint
        ↓
  experiment-agent     →  run/manage experiments → validate results
        ↓
ARS Stage 2 WRITE     →  write paper with verified experiment results
```

**O que ele faz**: executa experimentos em código (Python, R etc.) com monitoramento em tempo real, gerencia protocolos de estudos com seres humanos com uma checklist de ética IRB, interpreta estatísticas detectando 11 tipos de falácia e verifica a reprodutibilidade.

**Como usar os dois juntos**: pause o pipeline do ARS depois da Etapa 1, execute os experimentos em uma sessão separada do experiment-agent e traga os resultados (com o Material Passport) de volta para a Etapa 2 do ARS. O ARS não exige nenhuma modificação. Veja o [README do experiment-agent](https://github.com/Imbad0202/experiment-agent) para as instruções de configuração.

**Declaração de entrada na Etapa 1 (#260, #925)**: no checkpoint depois da Etapa 1, ou na entrada, quando uma execução começa depois da Etapa 1, o ARS pergunta se o artigo relata experimentos ou análises de dados que você mesmo executou e registra sua resposta, com as suas palavras, em um `experiment_intake_declaration` fail-closed no Material Passport. O ARS não deduz a resposta a partir do manuscrito. Se você executou experimentos externamente, o pesquisador registra uma entrada `experiment_provenance[]` por experimento (`experiment_id`, `repro_lock` aninhado, `planned_vs_executed[]`, `negative_results[]`, `known_limitations[]`) e a declaração fica como `experiments_declared`; caso contrário, fica como `no_experiments_declared`. A declaração é **obrigatória em todo passport posterior a #260** — uma execução que não envolve experimentos também declara `no_experiments_declared`, de modo que o gate de integridade nunca pode ser contornado em silêncio por um bloco de procedência esquecido. Os `experiment_id`s ficam congelados nesse ponto de entrada, que se fecha antes de o primeiro agente de escrita da Etapa 2 ser acionado (ou antes do primeiro gate de integridade, quando não há Etapa 2 pela frente); assim, você pode pausar depois da Etapa 1, executar os experimentos e registrá-los quando voltar. Mais tarde, os agentes de escrita fazem referência a eles por meio de `planned_experiment_ids[]`.

**Complemento do lado do ensino**: [Teaching Skills](https://github.com/YujxZJCN/teaching-skills) aplica a arquitetura do ARS (conjuntos de skills, contratos compartilhados, gates por etapa, um Course Passport) ao lado docente da vida acadêmica — planejamento de curso → aulas → avaliação → execução → reflexão; seu modo `sotl` encaminha projetos de investigação em sala de aula para o deep-research / academic-paper do ARS na fase de publicação.

---

## Uso

### Início rápido

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

### Skills individuais

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

#### Academic Pipeline (orquestrador)

```
"I want to write a complete research paper"           → full pipeline from Stage 1
"I already have a paper, review it"                   → mid-entry at Stage 2.5 (integrity first)
"I received reviewer comments"                        → mid-entry at Stage 4
```

> O pipeline termina com a **Etapa 6: Process Summary**, que gera automaticamente um registro do processo de criação do artigo com uma Avaliação da Qualidade da Colaboração em 6 dimensões (notas de 1 a 100).

#### SR-Screener (8 modos)

```
"Turn my proposal into a screening protocol"          → protocol mode
"Is this abstract eligible for my review?"            → quick mode (single-reviewer triage)
"Pilot the screening with my seed studies"            → pilot mode
"Screen these database exports"                       → ta-screen mode
"Screen the full texts of the advanced records"       → ft-screen mode
"Adjudicate the conflicts in my Rayyan export"        → adjudicate mode
"Double-check my exclusions"                          → audit mode
"Give me the PRISMA numbers for the screening"        → report mode
```

### Idiomas suportados

- **Chinês tradicional** (繁體中文) — padrão quando o usuário escreve em chinês
- **Inglês** — padrão quando o usuário escreve em inglês
- Resumos bilíngues (chinês + inglês) para artigos acadêmicos

> **Usa outro idioma?** O modo Socratic (deep-research) e o modo Plan (academic-paper) usam **ativação por intenção**: eles detectam o significado do seu pedido, não palavras-chave específicas. Por isso funcionam em **qualquer idioma** sem modificações.
>
> No entanto, a seção geral `Trigger Keywords` (que determina se a skill é ativada ou não) ainda lista palavras-chave em inglês e em chinês tradicional. Se a skill não estiver sendo ativada de forma confiável no seu idioma, você pode acrescentar palavras-chave do seu idioma à seção `### Trigger Keywords` de cada arquivo `SKILL.md` para aumentar a confiança da correspondência.

### Formatos de citação suportados

- APA 7.0 (padrão, incluindo as regras de citação em chinês)
- Chicago (Notas e Autor-Data)
- MLA
- IEEE
- Vancouver

### Estruturas de artigo suportadas

- IMRaD (pesquisa empírica)
- Revisão de literatura temática
- Análise teórica
- Estudo de caso
- Policy brief
- Artigo de conferência

---

## Detalhes das skills

As responsabilidades de cada agente e os artefatos de cada etapa agora estão em [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Os números de versão ficam ancorados aqui para que os metadados de cada release fiquem em um só lugar.

### Deep Research (v2.12.1)

Equipe de pesquisa com 13 agentes. Modos: full, quick, review, lit-review, three-way-scan, fact-check, socratic, systematic-review. Lista completa de agentes e artefatos: veja ARCHITECTURE.md §3.

### Academic Paper (v3.3.1)

Pipeline de escrita de artigos com 12 agentes. Modos: full, plan, outline-only, revision, revision-coach, abstract-only, lit-review, format-convert, citation-check, disclosure, rebuttal-audit. Saída: MD + DOCX (via Pandoc quando disponível) + LaTeX (classe `apa7` da APA 7.0 / IEEE / Chicago) → PDF via tectonic. Lista completa de agentes e responsabilidades por fase: veja ARCHITECTURE.md §3.

### Academic Paper Reviewer (v1.11.1)

Revisão com múltiplas perspectivas e 7 agentes, com **julgamentos narrativos vinculados a critérios**. Modos: full, re-review, quick, methodology-focus, guided, calibration. As revisões em produção e os pacotes Schema 6 continuam `NOT_CALIBRATED`; a calibração completa pode gerar um perfil candidato delimitado, mas a aplicação dele a uma revisão em produção não está conectada. Nenhuma nota total é mapeada para Accept, Minor Revision, Major Revision ou Reject. Fronteira entre o painel da primeira rodada e o acionamento da re-revisão regido por contrato: veja ARCHITECTURE.md §3, Stage 3 / Stage 3'.

### Academic Pipeline (v3.24.0)

Orquestrador de 10 etapas com verificação de integridade, revisão em duas fases, orientação socrática e avaliação da colaboração. Regras do pipeline (protocolo que os agentes seguem, não garantias em tempo de execução): toda etapa exige um checkpoint de confirmação do usuário; a verificação de integridade (Etapas 2.5 + 4.5) é OBRIGATÓRIA e não admite desvio sem registro (toda exceção exige que a justificativa do usuário seja registrada para a Etapa 6); a Matriz de Rastreabilidade de R&R (Schema 11) liga cada observação dos revisores à alteração que o autor declara ter feito e registra se a re-revisão a verificou. A v3.4 acrescentou o Compliance Agent (PRISMA-trAIce + RAISE) nas Etapas 2.5 / 4.5. A v3.5 acrescenta o **Collaboration Depth Observer** (`collaboration_depth_agent`, apenas consultivo — nunca bloqueia) em todo checkpoint FULL/SLIM e ao final do pipeline. Os gates de integridade OBRIGATÓRIOS (2.5 / 4.5) pulam explicitamente o observador para que as verificações de conformidade não sejam diluídas. Baseado em Wang & Zhang (2026), IJETHE 23:11. Matriz etapa por etapa com agentes, artefatos e gates: veja ARCHITECTURE.md §3.

### SR-Screener (v1.0.0)

Triagem de estudos com 4 agentes entre o `deep-research` (pergunta, protocolo, busca) e o `academic-paper` (redação da revisão). Modos: protocol, quick, pilot, ta-screen, ft-screen, adjudicate, audit, report. Dois subagentes revisores cegos (apenas Read e Grep) avaliam cada registro com base no protocolo confirmado pelo usuário, um terceiro revisor resolve os conflitos entre avançar e excluir, e scripts em Python que usam só a biblioteca padrão leem exportações RIS / PubMed .nbib / Web of Science / CSV, removem duplicatas, dividem em lotes, combinam e geram o registro da triagem, os grupos RIS, as contagens PRISMA 2020, um rascunho da seção de métodos com campos `[TO COMPLETE]` e um arquivo `literature_corpus[]`. Regras que os agentes seguem (não garantias em tempo de execução): nenhum registro é triado antes de o usuário confirmar o protocolo, nenhuma chamada com falha vira uma "exclusão" padrão, e a equipe de revisão verifica as decisões antes que os números sejam relatados. Veja [`sr-screener/SKILL.md`](sr-screener/SKILL.md).

---

## Otimizações da v3.0: o que descobrimos sobre os limites estruturais da IA

### O que aconteceu

Enquanto usava o ARS para escrever um artigo de reflexão sobre IA no ensino superior, esbarrei em três problemas estruturais que nenhuma quantidade de prompt engineering conseguia resolver:

1. **Frame-lock**: pedi à IA que conduzisse um debate de advogado do diabo (devil's advocate) contra a própria tese. Ela conduziu — quatro rodadas, cada uma mais refinada que a anterior. Mas todas as rodadas ficaram dentro do enquadramento que eu tinha definido. O DA atacava argumentos, nunca premissas. Nunca perguntou "estamos discutindo a pergunta certa?". É o mesmo padrão que causou a taxa de 31% de erros em citações no teste de estresse da v2.7: a IA que verifica e a IA que gera compartilham o mesmo enquadramento cognitivo.

2. **Bajulação (sycophancy) diante de contestação**: toda vez que eu contestava os ataques do DA, ele cedia rápido demais. Recuava das conclusões mais depressa do que as lançava. O treinamento do modelo recompensa a harmonia na conversa — então "o usuário contestou" era tratado como evidência de que o ataque estava errado, quando muitas vezes só significava que o usuário era insistente.

3. **Detecção errada de intenção**: o Socratic Mentor insistia em convergir e produzir entregáveis ("Quer que eu escreva isso?") enquanto eu ainda estava explorando. Ele não conseguia distinguir "o usuário quer uma discussão filosófica profunda" de "o usuário quer um resumo da pergunta de pesquisa". As duas coisas parecem engajamento, mas exigem comportamentos opostos da IA.

### O que mudamos (v3.0)

**Devil's Advocate — Protocolo de limiar de concessão** (`deep-research` + `academic-paper-reviewer`)
- O DA agora precisa dar uma nota de 1 a 5 a cada réplica antes de responder
- Só pode ceder com nota ≥4 (a réplica responde diretamente ao ataque central, com evidências)
- Nota ≤3: manter a posição e reformular o ataque original
- Regras contra bajulação: nada de concessões consecutivas, acompanhamento da taxa de concessão e detecção de frame-lock após cada checkpoint

**Socratic Mentor — Camada de detecção de intenção** (`deep-research`)
- Classifica a intenção do usuário como exploratória ou orientada a objetivo no início do diálogo e a cada 3 turnos
- Modo exploratório: desativa a convergência automática, aumenta o máximo de rodadas para 60 e proíbe perguntas do tipo "quer que eu resuma?"
- Modo orientado a objetivo: comportamento de convergência padrão
- Regras contra encerramento prematuro: no modo exploratório, é o usuário quem decide quando parar

**Socratic Mentor — Indicador de saúde do diálogo** (`deep-research`)
- Autoavaliação silenciosa a cada 5 turnos em três dimensões: concordância persistente, evitação de conflito e convergência prematura
- Insere automaticamente perguntas desafiadoras quando detecta um padrão de concordância
- Invisível para o usuário (para evitar manipulação), mas o log fica disponível para análise após a sessão

### Por que isso importa

Essas otimizações não resolvem os limites estruturais da IA — elas tornam esses limites visíveis e administráveis. O DA ainda vai acabar cedendo se for pressionado o bastante. O Socratic Mentor ainda vai ter algum viés de convergência. Mas agora existem checkpoints explícitos que freiam a bajulação, obrigam o DA a justificar suas concessões e impedem o Mentor de encerrar antes de o usuário estar pronto.

A lição mais profunda: letramento em IA não é aprender a usar a IA como ferramenta, seguir regras de ética ou ter medo dos riscos da IA. É se envolver com a IA a fundo o bastante para descobrir você mesmo os limites estruturais dela — e, no processo, os limites do seu próprio pensamento.

---

## Licença

Este trabalho está licenciado sob a [CC-BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

**Você tem o direito de:**
- Compartilhar — copiar e redistribuir o material
- Adaptar — remixar, transformar e criar a partir do material

**De acordo com os seguintes termos:**
- **Atribuição** — você deve dar o crédito apropriado
- **NãoComercial** — você não pode usar o material para fins comerciais

**Formato de atribuição:**
```
Based on Academic Research Skills by Cheng-I Wu
https://github.com/Imbad0202/academic-research-skills
```

---

## Colaboradores

**Cheng-I Wu** (吳政宜) — Autor e mantenedor

**[aspi6246](https://github.com/aspi6246)** — Colaborador. A otimização da v3.1 foi inspirada em padrões do [Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics): o padrão de restrição de somente leitura, a codificação de antipadrões como elemento central do projeto, a abordagem de marcos cognitivos (ensinar "como pensar", e não só procedimentos) e a filosofia de skills enxutas.

**[mchesbro1](https://github.com/mchesbro1)** — Colaborador. Propôs e redigiu originalmente a lista IS Basket of 8 de periódicos para `academic-paper-reviewer/references/top_journals_by_field.md` ([Issue #5](https://github.com/Imbad0202/academic-research-skills/issues/5)).

**[cloudenochcsis](https://github.com/cloudenochcsis)** — Colaborador. Ampliou a seção de SI da *Basket of 8* para a *Senior Scholars' Basket of 11* completa — acrescentando *Decision Support Systems*, *Information & Management* e *Information and Organization* ([Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7), [PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8)). Fonte: [AIS Senior Scholars' List of Premier Journals](https://aisnet.org/research/seniorscholarsbasket/).

**[eltociear](https://github.com/eltociear)** (Ikko Eltociear Ashimine) — Colaborador. Traduziu o README para o japonês ([`README.ja-JP.md`](README.ja-JP.md)) ([PR #161](https://github.com/Imbad0202/academic-research-skills/pull/161)).

**[xpfo-go](https://github.com/xpfo-go)** (xpfo) — Colaborador. Traduziu o README para o chinês simplificado ([`README.zh-CN.md`](README.zh-CN.md)) ([PR #181](https://github.com/Imbad0202/academic-research-skills/pull/181)).

**[devCharlotte](https://github.com/devCharlotte)** — Colaboradora. Traduziu o README para o coreano ([`README.ko-KR.md`](README.ko-KR.md)) ([PR #469](https://github.com/Imbad0202/academic-research-skills/pull/469)).

**[Yaobin29](https://github.com/Yaobin29)** — Colaborador. Propôs ferramentas de resposta a revisores no [PR #433](https://github.com/Imbad0202/academic-research-skills/pull/433); o modo `three-way-scan` do `deep-research` e o modo `rebuttal-audit` do `academic-paper` (recuperado do conceito `audit` daquele PR) foram integrados a partir dessa contribuição na v3.12.1.

**[ktao732084-arch](https://github.com/ktao732084-arch)** — Colaborador. Ampliou o sistema de declaração (disclosure) do `academic-paper` com nove alvos de políticas de publicação médica, coleta de informações obrigatórias específica para cada alvo e renderização autônoma fail-closed ([Issue #596](https://github.com/Imbad0202/academic-research-skills/issues/596), [PR #599](https://github.com/Imbad0202/academic-research-skills/pull/599)); ampliou a referência de relato clínico EQUATOR com orientações condensadas do CARE, STARD e TRIPOD+AI, além de uma sequência de roteamento fail-closed por desenho de estudo ([Issue #594](https://github.com/Imbad0202/academic-research-skills/issues/594), [PR #601](https://github.com/Imbad0202/academic-research-skills/pull/601)); e projetou e contribuiu com o resolvedor autônomo de literatura em chinês, o protocolo de API e o conjunto sintético de fixtures de transporte ([Issue #595](https://github.com/Imbad0202/academic-research-skills/issues/595), [PR #600](https://github.com/Imbad0202/academic-research-skills/pull/600)).

**[didacrios](https://github.com/didacrios)** — Colaborador. Traduziu o README para o espanhol ([`README.es-ES.md`](README.es-ES.md)).

**[laqueiroz](https://github.com/laqueiroz)** (Laís Queiróz) — Colaboradora. Traduziu o README para o português brasileiro ([`README.pt-BR.md`](README.pt-BR.md)).

---

## Registro de alterações

Aqui resumimos apenas as três versões mais recentes. O histórico completo está em [CHANGELOG.md](CHANGELOG.md) (em inglês).

### v3.24.0 (2026-10-27) — Verificações consultivas das referências sugeridas pelo painel e de seus achados, um lançador do guard com um só processo e correções nas regras de integridade

> **Duas verificações consultivas do revisor e correções; nenhuma skill nova, e a precisão das verificações em revisões reais não foi medida:** a v3.24.0 acrescenta dois anexos à Editorial Decision Letter. O primeiro busca ao vivo, nos quatro índices do gate de citações, cada obra que o Reviewer 2 e o Reviewer 3 recomendam, e informa se existe um registro, não se a obra sustenta a recomendação (#1001). O segundo envia cada ponto fraco e cada linha CRITICAL ou MAJOR do Devil's Advocate, sem o rótulo de quem a escreveu, a um subagente do modelo da sessão, que diz se o manuscrito a contradiz. Uma contradição só é listada quando a citação do juiz passa pela verificação do script em relação ao manuscrito; os demais veredictos de falsidade são listados como não confirmados (#1002). A verificação vem ativada por padrão, e `ARS_PANEL_CLAIM_CHECK=0` a desativa. Nenhum dos anexos alimenta a decisão, o roteiro de revisão ou os critérios da re-revisão. Antes de a segunda verificação ser lançada, uma auditoria pré-registrada e com dados reservados (held-out) de 805 afirmações do painel situou a taxa de afirmações falsas entre 1,5% e 12,9%, e o Claude Opus 5.5 e o Claude Fable 5.1 passaram no teste de contraste como juízes. O lançador do guard de write-scope inicia um processo Python por chamada de ferramenta, em vez de três, o que deve reduzir o vazamento do AppXSvc no Windows para cerca de um terço, embora o comportamento no Windows não tenha sido testado aqui (#1015), e as notas do guard informam quais nomes de ferramenta ele verifica (#1022). Três regras das verificações de integridade agora concordam sobre a entrada na Stage 5, a validade dos relatórios e a Stage 4′ (#1011), e o aviso de inicialização só aparece quando há atualização disponível (#1027). Usuários externos relataram #1015, #1022 e #1027.

### v3.23.2 (2026-10-24) — As verificações de integridade leem só a versão citada, a Stage 2.5 sempre é executada e correções nos adaptadores, no aviso de inicialização e no Windows

> **Correções; nenhuma skill nova. Uma mudança nos prompts tem uma pequena verificação de comportamento, e as demais não foram medidas:** a v3.23.2 faz com que as verificações de afirmações das Stages 2.5 e 4.5 comparem cada afirmação apenas com a versão da obra que o manuscrito cita (#1006). Quando essa versão não pode ser lida, a verificação registra uma nota de acesso e pede o PDF, em vez de ler um working paper ou um preprint. Em um caso sintético executado seis vezes (três sessões com o Claude Opus 5.5 e três com o Claude Fable 5.1, sem ferramentas web), todas as sessões seguiram a regra. Um relatório de integridade anterior não permite mais que o pipeline pule a Stage 2.5; ele é anexado como contexto (#995). A falta de uma entrada obrigatória bloqueia a transição de etapa em todos os documentos de regras (#990), e o exemplo do mentor socrático não classifica mais as ideias do usuário (#992). O aviso de SessionStart mostra ao usuário o lembrete de atualização, e o aviso voltado ao modelo ficou cerca de 2,1 KB mais curto (#999). O adaptador do Obsidian aceita datas ISO sem aspas e rejeita anos booleanos ou com dígitos sobrescritos (#988, #989); seis lints comparam caminhos no formato POSIX no Windows (#964, #978); o wrapper do Pi se combina com as seções estruturadas de prompt do Pi (#985); e o `CITATION.cff` traz o ORCID iD do autor (#1007). #978, #985 e #988 são contribuições externas.

### v3.23.1 (2026-10-16) — Correções no guard de write-scope, leitura de CSV conforme a RFC 4180 no sr-screener e Gemini 4 Argon como verificador provisório

> **Correções e atualização de modelos; nenhuma skill nova e nenhuma alegação de precisão ou desempenho:** a v3.23.1 fecha dois caminhos do guard de write-scope que deixavam gravações passarem sem verificação, um para agentes acionados pelo plugin e outro para o `timeout.exe` do Windows (#972), e a documentação agora indica onde o guard atua (#974). O `sr-screener` lê exportações CSV seguindo as regras de aspas da RFC 4180, em vez de regras deduzidas de uma amostra (#979). O Gemini 4 Argon passa a constar como verificador provisório do Google e como o id do Google recomendado; o `gemini-3.1-pro-preview` continua validado (#980). O núcleo de roteamento informa que um token `[direct-mode]` no meio da mensagem não é a válvula de escape (#892); em um teste rápido com instalação via plugin, o Claude Fable 5.1 ainda obedeceu ao token em 3 de 6 sessões (6 de 6 antes), então o critério de aceitação não foi atingido e a #892 continua aberta. Correções menores de lint e de Windows vêm de colaboradores externos (#956, #963, #965, #977), e o `THIRD_PARTY.md` passa a listar o md-to-word (#969).
