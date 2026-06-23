# nx-ai-engineer — Auditoria Completa + Arquitetura Consolidada

> **Documento único** com a arquitetura da plataforma e **todas as observações**
> da auditoria.
> **Data:** 2026-06-22 · **Versão auditada:** AIES `5.0.0-rc1` (+ extensões de
> conhecimento) · **Método:** inspeção de código, suíte `unittest`, grafo de
> importações (AST), detecção de ciclos, varredura de imports/dead-code, Quality
> Gate automatizado.
> **Auditorias anteriores:** [AUDIT.md](AUDIT.md) (1.0), [AUDIT-PLATFORM.md](AUDIT-PLATFORM.md)
> (4.0), [RC1_AUDIT.md](RC1_AUDIT.md) (RC). Este é o consolidado atual.

---

## 1. Sumário executivo

A plataforma está **estável, coesa, segura e madura**. Genérica, **stdlib-only
(zero dependências)**, com **205 testes (100% verdes)**, **nenhum ciclo de
importação**, **0 marcadores de dívida (TODO/FIXME)** e **Quality Gate aprovando
os 6 portões**. A camada de conhecimento foi consolidada num modelo claro de três
memórias com grafo de relacionamentos, sob uma doutrina enforçada por teste.

- **Estado geral:** **Pronta para uso assistido e evolução de longo prazo.**
- **Maturidade global:** **4,7 / 5.**
- **Risco de adoção:** **Baixo** — execução é *dry-run por padrão*; o núcleo nunca
  altera código de produto sem um adapter real explícito; só escreve em `.ai-project/`.

| Dimensão | Nota |
|----------|------|
| Arquitetura (coesão/acoplamento/ciclos) | ★★★★★ |
| Qualidade de código (stdlib/hygiene/SOLID) | ★★★★★ |
| Testes (205 verdes; APIs públicas cobertas) | ★★★★☆ |
| Documentação (18 ADRs + guias + doutrina) | ★★★★★ |
| Extensibilidade (SDK + contratos + guardrails) | ★★★★★ |
| Segurança (isolamento/dry-run/escrita restrita) | ★★★★★ |
| Profundidade operacional (adapters reais, semântica vetorial) | ★★★☆☆ |

---

## 2. Metodologia e verificações executadas

1. **Quality Gate** (`scripts/quality_gate.py`) → **ALL GATES PASSED**:
   - tests (205), import-cycles (none), unused-imports (none), public-cli (all),
     public-api (version), docs-present (all).
2. **Grafo de importações (AST)** entre camadas → **sem ciclos**; direção de
   dependências validada.
3. **Varredura de dependências** → **100% stdlib** (nenhuma lib de terceiros).
4. **Dead code / dívida** → 0 ocorrências de TODO/FIXME/XXX/HACK no código.
5. **Doutrina do conhecimento** → teste-guardrail confirma que `aies/knowledge/`
   não importa nenhuma camada de raciocínio.

---

## 3. Métricas (estado atual)

- **Código:** 78 arquivos Python (~7.558 LOC, sem testes) + 22 arquivos de teste
  (~2.532 LOC). Orquestrador CLI: 680 LOC (glue fino).
- **Total no skill:** 110 `.py`, 69 `.md`, 185 arquivos.
- **ADRs:** 18 (ADR-0001…0018). **Comandos CLI:** 19. **Exemplos:** 10.
- **Dependências externas:** **0**.

### LOC por camada (`aies/`)
| Camada | Arq | LOC | Camada | Arq | LOC |
|--------|----:|----:|--------|----:|----:|
| foundation | 1 | 14 | knowledge | 12 | 1481 |
| kernel | 6 | 592 | evolution | 9 | 631 |
| workflow | 3 | 108 | governance | 5 | 201 |
| schedulers | 4 | 756 | experience | 2 | 78 |
| intelligence | 8 | 439 | observability | 4 | 166 |
| memory | 6 | 600 | adapters | 4 | 260 |
| engines | 2 | 96 | sdk | 1 | 134 |

---

## 4. Arquitetura consolidada

Plataforma multi-agente, genérica, instalável em qualquer repositório como uma
pasta `.ai-project/`. Camadas com dependências apontando para baixo; transversais
(Governance/Observability/Experience) só **escutam eventos**.

```
SDK            register Agents/Engines/Workflows/Adapters/Plugins/Tools
──────────────────────────────────────────────────────────────────────────
Governance · Observability · Experience       (transversais; event subscribers)
──────────────────────────────────────────────────────────────────────────
Kernel        domain · states(9) · lifecycle(DAG) · BaseEngine(Dry→Test→Execute)
  └ Pipeline  composition root (única que importa "tudo")
Workflow      pipelines reutilizáveis (full-dev, plan-only, execute-plan)
Schedulers    Execution Engine (sequencial) · Execution Cluster (concorrente) · Dispatcher
Intelligence  Planner · Dependency · Risk · Estimation · Strategy · Reasoning · Decision
Memory        Context · Learning · Project Brain (dir) · Semantic
Knowledge     Knowledge Engine + Providers + Graph + ObsidianSync   (← abaixo de Memory)
Evolution     Autonomous Learning + Project Evolution
Engines       Audit · Review · Delivery
──────────────────────────────────────────────────────────────────────────
Adapters      DryRunAdapter (default) · ClaudeCodeAdapter · (futuros modelos)
Foundation    util · config
```

### Fluxo de conhecimento (canônico)
```
Project Brain → Knowledge Engine → Knowledge Providers → Obsidian
              → Context Engine → Agentes
```

### Pipeline de execução (4.0)
```
request → Audit → Decide(agentes/workflow/ordem/risco/custo/paralelismo) →
Context(enriquecido pelo grafo) → Execute(engine|cluster) → Review → Deliver →
Learn → Project Evolution → Knowledge sync (Brain/Obsidian/Git)
```

### Grafo de dependências entre camadas (resumo, sem ciclos)
- `adapters → foundation, kernel`
- `schedulers → kernel, adapters, agents, foundation`
- `intelligence → schedulers, workflow` (composição; sem ciclo)
- `memory → kernel, knowledge, agents, foundation`
- `knowledge → foundation, agents` (+ internos) — **não importa Memory** (acíclico)
- `evolution → memory`
- `engines → governance` (delivery usa gates)
- `kernel(pipeline) → todas` (composition root)
- **Ciclos: NENHUM** (verificado por AST).

---

## 5. Inventário de componentes

- **Kernel:** domain, states(9 estados + transições validadas), lifecycle(DAG +
  detecção de ciclo), `BaseEngine` (gate **Dry Run → Test → Execute**), pipeline.
- **Workflow:** Workflow/Step/Registry + builtins (full-dev, plan-only, execute-plan).
- **Schedulers:** Execution Engine (sequencial), **Execution Cluster** (worker
  pool, fila de prioridade, scheduler, concorrência), Agent Dispatcher (Strategy).
- **Intelligence:** Planner, Dependency, Risk, Estimation, Strategy, Reasoning,
  **Decision Engine** (decide agentes/workflow/ordem/risco/impacto/custo/tempo/
  Review/QA/paralelismo).
- **Memory:** Context Engine (consome o Knowledge Engine), Learning, **Project
  Brain** (dir-based, versionado, *knowledge-only*), Semantic (stub), cache.
- **Knowledge:** **Knowledge Engine** (3 memórias + 5 responsabilidades),
  Providers (Filesystem, Git, Markdown, ADR, Project-Brain, Obsidian),
  **Knowledge Graph**, **ObsidianSync** (vault visual incremental).
- **Evolution:** Autonomous Learning (self-improvement, experience-analyzer,
  pattern-discovery, similarity, recommendation, knowledge-evolution,
  brain-optimizer) + **Project Evolution** (conhecimento estruturado por execução).
- **Engines de domínio:** Audit, Review, Delivery.
- **Governance:** ADR, policies, quality-gates, checklists.
- **Observability/Experience:** EventBus, logging JSONL, telemetry, KPIs.
- **Adapters:** DryRun (default seguro), **ClaudeCode** (execução real, mode-aware,
  timeout/retry/cancel).
- **SDK:** registries para Agents/Engines/Workflows/Adapters/Plugins/Tools + eventos.
- **CLI (19):** audit, plan, decide, dispatch, context, run, review, deliver,
  pipeline, metrics, insights, recommend, knowledge, obsidian, worktree, tasks,
  locks, unlock, status.

---

## 6. Modelo de conhecimento (consolidado)

### Três memórias
| Memória | Papel | Backing |
|---------|-------|---------|
| **Project Brain** | operacional (estado atual) | `.ai-project/brain/` (17 facetas) |
| **Obsidian** | organizacional (visão navegável) | `.ai-project/obsidian/` |
| **Git** | histórica (registro imutável) | repositório |

O **Knowledge Engine** as coordena/sincroniza (`sync`/`status`) e expõe a
**doutrina das 5 responsabilidades** — `discover`, `index`, `relate`, `update`,
`deliver_context` — e **nada mais**. Não raciocina, não aprende programação, não
melhora modelos: **toda inteligência pertence ao modelo**; o engine só reduz a
carga cognitiva (mais histórico → contexto mais rico → menos tokens).

### Knowledge Graph (relacionamentos automáticos)
Cadeia inferida (nunca lendo código): `Service → API → Database → Migration →
Test → ADR → Bug → Feature → Sprint → Documentação → Obsidian`. Usado **apenas
para enriquecer o contexto** dos agentes (`enrich_context`/`deliver_context`).

### Project Evolution
Após cada execução, classifica **paths/metadados** dos arquivos alterados nas
facetas estruturadas (módulos, serviços, APIs, entidades, testes, integrações,
dependências, padrões, bugs, decisões, lições, arquivos relacionados). **Nunca
armazena código nem respostas do modelo** (guard `looks_like_code`).

---

## 7. Rastreabilidade — ADRs

| ADR | Tema | ADR | Tema |
|-----|------|-----|------|
| 0001 | Execution Engine (gate de modos) | 0010 | Execution Cluster |
| 0002 | Agent Dispatcher (Strategy) | 0011 | Decision Engine |
| 0003 | Context Engine | 0012 | Autonomous Learning |
| 0004 | Brain/Learning/Experience/Semantic | 0013 | Knowledge Providers |
| 0005 | Governance + Delivery | 0014 | Obsidian (vault visual) |
| 0006 | Pipeline único | 0015 | Knowledge Engine (3 memórias) |
| 0007 | Observability/telemetria | 0016 | Project Evolution |
| 0008 | SDK | 0017 | Knowledge Graph |
| 0009 | ClaudeCodeAdapter | 0018 | Doutrina do Knowledge Engine |

Cada decisão arquitetural tem ADR com contexto, alternativas e consequências.

---

## 8. Qualidade e segurança

- **SOLID / baixo acoplamento / alta coesão:** cada engine com responsabilidade
  única; comunicação por dicts + eventos; transversais só escutam.
- **Aberto/Fechado:** SDK + contratos (`BaseEngine`, `AgentAdapter`,
  `SelectionStrategy`, `Resolver`, `SemanticIndex`, `KnowledgeProvider`).
- **Sem ciclos** (AST) e **stdlib-only** (zero dependências) — confirmados.
- **Segurança por construção:** Dry Run obrigatório + DryRunAdapter default;
  escrita restrita a `.ai-project/`; `subprocess` sem `shell=True`; JSON com
  try/except; commit ao Git é opt-in. Plugins são código confiável carregado
  explicitamente (sem auto/remoto).
- **Knowledge-only:** o Brain nunca armazena código; guardrail por teste impede a
  camada `knowledge` de importar raciocínio.
- **Quality Gate como merge bar:** falha o PR se testes/ciclos/imports/CLI/docs
  regredirem.

---

## 9. Observações da auditoria

### 9.1 Pontos fortes
1. **Plataforma coesa e completa**, com pipeline único e modelo de conhecimento
   maduro (3 memórias + grafo + doutrina enforçada).
2. **Zero dependências** → portabilidade máxima (Python 3.8+).
3. **Seguro por construção** (dry-run default; não muta produto sozinho).
4. **Event-driven** → camadas transversais adicionáveis sem tocar no núcleo.
5. **Extensível de verdade** (SDK + contratos) e **autodocumentado** (18 ADRs).
6. **Higiene exemplar**: 0 dívida marcada, 0 imports não usados, 0 ciclos.

### 9.2 Riscos remanescentes (não-bloqueantes)
| # | Risco | Sev. | Mitigação / Recomendação |
|---|-------|------|--------------------------|
| R1 | `ClaudeCodeAdapter` `test` valida por instrução (sem flag read-only universal) | Média | configurável por ambiente; `dry-run` default seguro |
| R2 | Semantic/Similarity é keyword (Jaccard) | Baixa | índice vetorial plugável via SDK (futuro) |
| R3 | Execution Cluster sem *resume* de `runs/<id>.json` | Baixa | execução determinística; resume no roadmap |
| R4 | Locks advisórios em granularidade de área | Média | tornar por-arquivo + expiração; enforcement em escrita |
| R5 | `kernel/pipeline.py` é composition-root que cresce | Baixa | extrair p/ `platform/` se ganhar etapas |
| R6 | Sem ferramenta de cobertura (`coverage`) — stdlib-only | Baixa | mapa módulo→teste; CI opcional fora do core |

**Nenhuma violação arquitetural crítica. Nenhum ciclo. Nenhum risco alto.**

### 9.3 Dívida técnica
- **Baixa.** Heurísticas (classificação por path, seleção de agentes, estimativa)
  são determinísticas e adequadas, porém substituíveis por ML via SDK no futuro.
- Pequenas sobreposições conscientes (ex.: `intelligence→schedulers`,
  `engines→governance`) são composição sem ciclo, documentadas.

---

## 10. Conformidade com critérios de prontidão

- [x] Todos os testes passando (205).
- [x] Sem violações arquiteturais críticas; sem ciclos.
- [x] APIs públicas documentadas (SDK/Engine/Workflow/Plugin/Knowledge).
- [x] Documentação consistente (sem duplicação; guias + doutrina).
- [x] Exemplos funcionam (10).
- [x] SDK completo; Project Brain operacional (dir-based, versionado).
- [x] Engines desacopladas (event-driven; núcleo puro).
- [x] Adapters respeitam a interface pública (`AgentAdapter`).
- [x] Knowledge Engine com doutrina das 5 responsabilidades enforçada por teste.
- [x] Evolui sem refatoração estrutural (SDK + contratos + composition-root).
- [x] Quality Gate automatizado; SemVer + CHANGELOG + MIGRATION_GUIDE.

---

## 11. Recomendações de evolução (priorizadas)

1. **ClaudeCodeAdapter**: modo `test` com sandbox read-only real + `changed_files`
   por diff pré/pós (R1).
2. **Locks por-arquivo + enforcement de escopo** em tempo de escrita (R4).
3. **Resume de runs** no Execution Cluster + métricas de utilização de worker (R3).
4. **Semantic vetorial** + `MLStrategy` plugados via SDK (R2) — fechando o ciclo
   Decision ⇄ Recommendation (decidir usando o que foi aprendido).
5. **Pesos no Knowledge Graph** (frequência de co-ocorrência) para priorizar o
   enriquecimento de contexto.
6. **CI próprio** do framework (lint + `coverage`) — sem virar dependência do core.
7. Manter o **Quality Gate** como barreira obrigatória de PR; evoluir **só via
   SDK/contratos** (não tocar no núcleo).

---

## 12. Conclusão

O `nx-ai-engineer` é uma **plataforma de engenharia assistida por IA madura e
extensível**: genérica, stdlib-only, segura por construção, orientada a eventos,
com pipeline único, três memórias de conhecimento coordenadas, grafo de
relacionamentos e uma doutrina clara — "toda inteligência pertence ao modelo; o
framework apenas entrega conhecimento estruturado e contexto enriquecido,
reduzindo a carga cognitiva e o consumo de tokens".

**Veredito: APROVADA.** Maturidade **4,7/5**, sem violações críticas, dívida
baixa e documentada. As recomendações do §11 são evolutivas e podem ser
adicionadas sem refatoração estrutural.

---

### Anexo A — Quality Gate (resultado)
```
[PASS] tests           Ran 205 tests — OK
[PASS] import-cycles   none
[PASS] unused-imports  none
[PASS] public-cli      all present (19 commands)
[PASS] public-api      version 5.0.0-rc1
[PASS] docs-present    all present
ALL GATES PASSED
```

### Anexo B — Documentos de referência
Arquitetura: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · Overview:
[framework/docs/ARCHITECTURE_OVERVIEW.md](framework/docs/ARCHITECTURE_OVERVIEW.md) ·
Conhecimento: [framework/docs/KNOWLEDGE_GUIDE.md](framework/docs/KNOWLEDGE_GUIDE.md),
[framework/docs/PROJECT_KNOWLEDGE.md](framework/docs/PROJECT_KNOWLEDGE.md),
[framework/docs/PROJECT_BRAIN.md](framework/docs/PROJECT_BRAIN.md) · ADRs:
[framework/docs/adr/](framework/docs/adr/) · Guias: SDK/Engine/Workflow/Plugin ·
Release: [CHANGELOG.md](CHANGELOG.md), [ROADMAP.md](ROADMAP.md),
[RELEASE_NOTES.md](RELEASE_NOTES.md).
