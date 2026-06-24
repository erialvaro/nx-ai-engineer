# Documento de Arquitetura — AIES Plataforma (2.0 → 4.0)

> **Status:** APROVADO (2026-06-21) — implementação incremental autorizada.
> **Versão do documento:** 2.0 (incorpora os 9 ajustes estruturais do solicitante)
> **Base auditada:** AIES 1.0.0 (ver [AUDIT.md](../AUDIT.md))
> **Marca:** permanece **AIES** (sem rename para AIOS nesta versão — decisão #1).
> **Regra-mãe:** implementação em PRs **pequenos, testados, documentados e 100%
> compatíveis** com as versões anteriores.

---

## Changelog desta revisão (2.0)
Ajustes aprovados incorporados:
1. **Nome mantido: AIES** (sem AIOS). Rebranding futuro = decisão independente.
2. **Dry Run obrigatório** para toda nova Engine: ciclo **Dry Run → Test →
   Execute**. Nenhuma Engine altera nada real sem passar pelos três modos.
3. Nova camada **Workflow** entre **Kernel** e **Schedulers** (pipelines
   reutilizáveis).
4. Novo módulo **Governance** (ADRs, políticas, quality gates, checklists, regras
   arquiteturais, segurança).
5. Novo módulo **Intelligence** (Planner, Dependency, Risk, Estimation e demais
   raciocínios).
6. **Project Brain** baseado em **diretórios especializados** (não monolítico).
7. Novo módulo **Experience** (métricas de execução/qualidade/retrabalho/
   performance/tempo/falhas/sucesso → aprendizado contínuo).
8. Nova camada **Semantic Knowledge** (preparada para indexação vetorial/busca
   semântica; implementação plena em versão futura).
9. **SDK** estendido para Agents, Engines, Workflows, Adapters, **Plugins** e
   **Tools** — extensível sem alterar o núcleo.

---

## Índice
1. Visão arquitetural (camadas)
2. Princípios e decisões
3. Estrutura de módulos (layout alvo dentro de `aies/`)
4. Contrato de Engine e o modo obrigatório Dry Run → Test → Execute
5. Camada Workflow
6. Kernel — domínio, estados, ciclo de vida
7. Schedulers — Execution Engine + Agent Dispatcher
8. Intelligence — Planner, Dependency, Risk, Estimation
9. Memory — Context, Learning, Project Brain (dir-based), Semantic Knowledge
10. Governance — ADR, políticas, quality gates, checklists, regras, segurança
11. Experience — métricas e aprendizado de uso
12. Observability — event bus, logs, telemetria
13. Adapters — independência de modelo de IA
14. Delivery Engine
15. SDK e pontos de extensão
16. Modelo de eventos
17. Comunicação entre módulos
18. Fluxo completo (Pipeline único 4.0)
19. Compatibilidade retroativa
20. Evolução por versão (2.0/3.0/4.0)
21. Roadmap de PRs
22. Mapa "ajuste → onde foi atendido"

---

## 1. Visão arquitetural (camadas)

AIES evolui de framework para **plataforma de engenharia assistida por IA**,
organizada em camadas com fronteiras nítidas. Dependências apontam para baixo;
as camadas transversais (Governance, Observability, Experience) só **escutam**
eventos — não são importadas pelo núcleo.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ SDK — Agents · Engines · Workflows · Adapters · Plugins · Tools            │
│       (terceiros estendem sem tocar no núcleo)                             │
├──────────────────────────────────────────────────────────────────────────┤
│ TRANSVERSAIS (via eventos, nunca importadas pelo núcleo):                  │
│   Governance   — ADR, políticas, quality gates, checklists, regras, sec.   │
│   Observability— event bus, logs, telemetria                              │
│   Experience   — métricas de uso: tempo, retrabalho, falhas, sucesso, qual.│
├───────────────────────────────┬──────────────────────────────────────────┤
│ KERNEL                        │ MEMORY                                     │
│  domain · states · lifecycle  │  Context Engine                            │
│  Engine base (Dry/Test/Exec)  │  Learning Engine                           │
│         │                     │  Project Brain (diretórios especializados) │
│         ▼                     │  Semantic Knowledge (preparado p/ vetorial) │
│ WORKFLOW                      │                                            │
│  pipelines reutilizáveis      │                                            │
│         │                     │                                            │
│         ▼                     │                                            │
│ SCHEDULERS                    │ INTELLIGENCE                               │
│  Execution Engine             │  Planner · Dependency · Risk · Estimation  │
│  Agent Dispatcher             │                                            │
├───────────────────────────────┴──────────────────────────────────────────┤
│ ENGINES de domínio: Audit · Architecture · Review · Delivery               │
├──────────────────────────────────────────────────────────────────────────┤
│ ADAPTERS — DryRun (default) · ClaudeCode · (futuros modelos/CLIs)          │
└──────────────────────────────────────────────────────────────────────────┘
```

**Posição da Workflow (decisão #3):** o Kernel fornece os primitivos
(domínio/estados/ciclo de vida/contrato de Engine); a **Workflow** compõe engines
em **pipelines reutilizáveis**; os **Schedulers** executam os nós de um workflow.
Logo: `Kernel → Workflow → Schedulers`.

---

## 2. Princípios e decisões

1. **Compatibilidade total.** CLI, comandos e `.ai-project-assistant/` atuais intactos;
   tudo novo é aditivo.
2. **Stdlib-only.** Sem dependências externas (Python 3.8+).
3. **Independência de modelo.** Núcleo fala com `AgentAdapter`, nunca com um
   provedor.
4. **Dry Run obrigatório** (decisão #2): toda Engine implementa o contrato de
   modos; `EXECUTE` exige passagem prévia por `DRY_RUN` e `TEST`.
5. **Orientado a eventos.** Engines publicam eventos; Governance/Observability/
   Experience escutam. Baixo acoplamento.
6. **Brain como conhecimento, nunca código.** Estrutura por diretórios.
7. **Aberto/Fechado.** Extensão via SDK (Agents/Engines/Workflows/Adapters/
   Plugins/Tools) e Strategy Pattern.
8. **Segurança preservada.** `protected_paths`, locks, enforcement de escopo e
   quality gates de Governance.

---

## 3. Estrutura de módulos (layout alvo dentro de `aies/`)

Como o nome permanece **AIES**, a reestruturação acontece **dentro** de `aies/`.
`aies/__init__.py` mantém os imports atuais (`from aies import analyzer, planner,
…`) válidos via reexport — **compatibilidade total**. As engines de domínio
existentes ganham um **lar lógico** por reexport já no PR-0; a relocação física
fica para o PR de consolidação (PR-10), mantendo cada PR pequeno e sem quebra.

```
framework/tools/aies/
├── __init__.py            # FACHADA: reexporta a superfície pública atual + nova
├── foundation/            # primitivos compartilhados
│   ├── util.py  config.py
├── kernel/
│   ├── domain.py          # Plan, Subtask, Run, Node, AgentContext, AgentResult…
│   ├── states.py          # ExecutionState (9 estados) + transições válidas
│   ├── lifecycle.py       # TaskGraph: deps, prontidão, progresso
│   └── engine.py          # Engine base + ExecutionMode (Dry/Test/Execute)
├── workflow/
│   ├── workflow.py        # Workflow + Step + WorkflowRegistry (pipelines reusáveis)
│   └── builtin.py         # pipelines padrão (ex.: full-dev, plan-only, review-only)
├── schedulers/
│   ├── execution.py       # Execution Engine (2.0-S1)
│   └── dispatcher.py      # Agent Dispatcher + strategies (2.0-S2)
├── intelligence/
│   ├── planner.py         # (reexporta/loga p/ engine de planejamento)
│   ├── dependency.py      # análise/ordenação de dependências
│   ├── risk.py            # análise de risco
│   └── estimation.py      # estimativa de esforço/impacto
├── memory/
│   ├── context.py         # Context Engine + resolvers (3.0-S1)
│   ├── learning.py        # Learning Engine (3.0-S2)
│   ├── brain.py           # Project Brain (diretórios especializados) (3.0-S2)
│   ├── cache.py           # cache + invalidação de contexto
│   └── semantic.py        # Semantic Knowledge (interfaces; impl. futura)
├── governance/
│   ├── adr.py             # geração automática de ADR
│   ├── policies.py        # políticas + regras arquiteturais
│   ├── quality_gates.py   # gates (testes, protected paths, cobertura…)
│   └── checklists.py      # checklists por etapa/agente
├── experience/
│   └── metrics.py         # KPIs de uso: tempo, retrabalho, falhas, sucesso, qual.
├── observability/
│   ├── events.py          # EventBus + tipos de evento
│   ├── logging.py         # logs estruturados JSONL
│   └── telemetry.py       # coleta/exportação de telemetria
├── adapters/
│   ├── base.py            # AgentAdapter (Protocol) + AgentResult
│   ├── dryrun.py          # adapter sem efeitos (default)
│   └── claude_code.py     # adapter Claude Code (opcional, isolado)
├── engines/               # engines de domínio (lar lógico; relocação física no PR-10)
│   ├── audit.py architecture.py review.py delivery.py
│   ├── analyzer.py tasks.py locks.py worktree.py agents.py
├── sdk/
│   └── __init__.py        # register_agent/engine/workflow/adapter/plugin/tool
└── tests/                 # unittest stdlib (cresce a cada PR)
```

Artefatos em disco (todos aditivos sob `.ai-project-assistant/`):
```
.ai-project-assistant/
├── tasks/ reviews/ locks/ memory/          # já existem
├── runs/                                    # estado de execução (2.0)
├── brain/  (diretórios especializados — §9.3)
├── knowledge/  bugs/ decisions/ adr/ retrospectives/ patterns/ lessons-learned/
├── context-cache/                           # Context Engine (3.0)
├── experience/                              # métricas de uso (3.0/4.0)
├── logs/  metrics/                          # observabilidade (4.0)
└── governance/  policies/ checklists/       # políticas versionadas (opcional)
```

---

## 4. Contrato de Engine e o modo obrigatório Dry Run → Test → Execute (decisão #2)

`kernel/engine.py`. **Toda** nova Engine herda `BaseEngine` e implementa os três
modos. O modo real (`EXECUTE`) é **bloqueado** até que `DRY_RUN` e `TEST` tenham
sido executados com sucesso para a mesma entrada (registro em memória do ciclo).

```python
class ExecutionMode(Enum):
    DRY_RUN = "dry_run"   # simula; nenhum efeito colateral; retorna plano de ação
    TEST    = "test"      # valida em ambiente seguro/sandbox; sem efeito em produção
    EXECUTE = "execute"   # efeito real (só após DRY_RUN+TEST aprovados)

class EngineResult:        # dataclass
    mode: ExecutionMode; ok: bool; actions: list[dict]
    diagnostics: list[str]; error: str | None

class BaseEngine(ABC):
    name: str
    def dry_run(self, ctx) -> EngineResult: ...   # obrigatório
    def test(self, ctx)    -> EngineResult: ...   # obrigatório
    def execute(self, ctx) -> EngineResult: ...   # obrigatório
    # Gate central: garante a progressão; emite eventos; nunca pula etapa.
    def run(self, ctx, mode: ExecutionMode) -> EngineResult
```
- O **gate** em `run()` recusa `EXECUTE` se o par (engine, hash do ctx) não tiver
  `DRY_RUN`+`TEST` ok no ciclo atual → cumpre "nenhuma Engine executa alterações
  reais sem passar pelos três modos".
- Cada modo publica eventos (`engine.dry_run`, `engine.test`, `engine.execute`).
- Engines existentes (Audit/Review/etc.) são **read-only** e adaptadas ao
  contrato de forma trivial (dry_run = test = execute = análise), sem quebra.

---

## 5. Camada Workflow (decisão #3)

`workflow/`. Define **pipelines reutilizáveis** como dados (lista ordenada de
steps), desacoplados de quem os executa.

```python
class Step:                 # uma etapa do pipeline
    name: str; engine: str; mode: ExecutionMode; depends_on: list[str]
class Workflow:
    name: str; steps: list[Step]
class WorkflowRegistry:
    def register(self, wf: Workflow) -> None
    def get(self, name: str) -> Workflow
```
- **Builtins** (`workflow/builtin.py`): `full-dev` (Audit→Architecture→Plan→
  Context→Dispatch→Execute→Review→Deliver→Learn), `plan-only`, `review-only`.
- A **Execution Engine** (Schedulers) recebe um `Workflow` + grafo de nós e o
  executa respeitando estados/deps. Workflows novos via SDK (`register_workflow`).
- Posição: consome o Kernel (domain/states), é consumido pelos Schedulers.

---

## 6. Kernel — domínio, estados, ciclo de vida

`kernel/`. Primitivos da plataforma.

### 6.1 Domínio (`domain.py`)
`Plan, Subtask, Run, Node, AgentContext, AgentResult, Event, KnowledgeRecord`
(dataclasses imutáveis; nenhum carrega código-fonte do projeto).

### 6.2 Estados (`states.py`) — máquina de estados
```
PENDING ─deps ok─► READY ─► RUNNING ─► COMPLETED            (terminal ✓)
   │                 ▲          │  │
   │ deps/lock       │          │  └─► FAILED ─attempts<max─► RETRYING ─► READY
   ▼                 │          │            └attempts≥max─► FAILED (terminal)
BLOCKED ─liberado────┘          └─► CANCELLED (terminal ✗)
   └─ não necessário ─► SKIPPED (terminal)
```
| Estado | Saídas válidas |
|--------|----------------|
| PENDING | READY, BLOCKED, CANCELLED, SKIPPED |
| READY | RUNNING, CANCELLED |
| RUNNING | COMPLETED, FAILED, CANCELLED |
| BLOCKED | READY, CANCELLED |
| FAILED | RETRYING, (terminal) |
| RETRYING | READY |
| COMPLETED / SKIPPED / CANCELLED | terminais |

`states.transition(node, to)` centraliza e valida; toda mudança emite
`task.state_changed`.

### 6.3 Ciclo de vida (`lifecycle.py`)
`TaskGraph` constrói o DAG a partir das subtasks, calcula nós **prontos** (deps
COMPLETED + sem lock), progresso e detecção de ciclos.

---

## 7. Schedulers — Execution Engine + Agent Dispatcher

### 7.1 Execution Engine (`schedulers/execution.py`, 2.0-S1)
Controla execução; **nunca** implementa código. Recebe `runner` injetado (um
Adapter) — genérica, sem conhecer agentes nem Claude Code.
```python
class ExecutionEngine(BaseEngine):
    def __init__(self, *, workflow, graph, runner, lock_provider, bus, policy,
                 context_provider=None): ...
    def schedule(self) -> list[Node]      # nós READY
    def step(self) -> Node | None         # executa 1 nó pronto
    def run(self, ctx, mode) -> EngineResult   # drena o grafo; respeita modos
    def cancel(self, node_id=None) -> None
    def progress(self) -> dict
```
- Persiste `Run` em `.ai-project-assistant/runs/<id>.json` (retomável/auditável).
- Retries/falhas/cancelamento/progresso via estados (§6.2).
- Comando: `orchestrator.py run --plan <task-id> [--mode dry_run|test|execute]`
  (default `dry_run`).
- **Núcleo compartilhado (`NodeExecutor`):** a lógica de execução de um nó
  (lock-check, transições+eventos, chamada do runner, retry) vive em um único
  `NodeExecutor`, reutilizado pelo engine sequencial e pelo Cluster (§7.1.1) —
  zero duplicação. Aceita um `threading.Lock` opcional (transições/emissões
  atômicas; a chamada do runner roda **fora** do lock).

### 7.1.1 Execution Cluster (`schedulers/cluster.py`) — execução concorrente
Evolução concorrente do engine (ADR-0010), também um `BaseEngine` com o mesmo gate
Dry Run → Test → Execute. Reutiliza `NodeExecutor`, `TaskGraph`, estados e o
adapter; adiciona **apenas** o escalonador concorrente:
```python
class WorkerState(Enum): CREATED, IDLE, BUSY, STOPPING, STOPPED
class ClusterPolicy:  max_workers:int=4; max_retries:int=1
class ExecutionCluster(BaseEngine):
    def cancel(self); def progress(self); def workers_status(self) -> list[dict]
```
- **Worker Pool** — N threads, cada Worker com **ciclo de vida próprio**
  (CREATED→IDLE→BUSY→STOPPING→STOPPED), com `processed`/`current`.
- **Queue interna** — heap de prioridade; `node_priority(agente, prioridade_do_plano)`
  ordena os nós prontos (contratos/dados primeiro; planos `high` recebem boost).
- **Scheduler de Workers** — enfileira nós prontos respeitando **dependências**
  (`TaskGraph`) e **locks**, aguarda via `Condition` e reavalia a prontidão a cada
  conclusão. **Controle de concorrência** = tamanho do pool.
- **Retry / Cancelamento / Prioridades / Dependências** — reusados do
  `NodeExecutor`/`TaskGraph`/máquina de estados; `cancel()` é um `threading.Event`
  que também cancela o adapter (mata processo em andamento).
- Compatível: `max_workers=1` ⇒ comportamento sequencial. CLI:
  `run/pipeline --workers N` (default **1 = engine sequencial**).

### 7.2 Agent Dispatcher (`schedulers/dispatcher.py`, 2.0-S2)
Seleciona **apenas** os agentes necessários (OAuth → backend, database, security,
qa, reviewer, delivery; **nunca** frontend) via **Strategy Pattern**
(`RuleBasedStrategy` hoje; `MLStrategy` no futuro, mesma interface). Não
selecionados viram `SKIPPED`.

---

## 8. Intelligence — raciocínio e decisão (decisão #5; Decision Engine: ADR-0011)

`intelligence/`. Concentra o **raciocínio** e a **tomada de decisão**.
- **planner.py** — decompõe objetivo em subtasks (evolui o atual).
- **dependency.py** — resolve e ordena dependências (DAG, topo-sort).
- **risk.py** — `analyze/score/level` + **`RiskEngine`** (risco: segurança,
  dados, compat, tenant/PII).
- **estimation.py** — `estimate` (esforço/blast) + **`EstimationEngine`**
  (**custo** em tokens e **tempo** estimado, ciente de paralelismo).
- **strategy.py** — **`StrategyEngine`**: *quais agentes* (reusa o Agent
  Dispatcher) e *qual workflow* (política sobre o registry).
- **reasoning.py** — **`ReasoningEngine`**: necessidade de **Review**, de **QA**,
  **paralelizável?**, confiança e **rationale** legível.
- **decision.py** — **`DecisionEngine`**: compõe Strategy + Risk + Estimation +
  Reasoning e calcula **ordem de execução** e **camadas de paralelismo**
  (camadas topológicas dos agentes — mesma camada ⇒ independentes ⇒ concorrentes).
  Retorna um `Decision` único e emite `decision.made` (+ `decision.recorded` →
  ADR via Governance). O **grau de paralelismo** alimenta o `--workers` do Cluster.

O `DecisionEngine` decide automaticamente: agentes, workflow, ordem, riscos,
impacto, custo, tempo, Review, QA e paralelismo. O **Pipeline** conduz a seleção
de agentes a partir dele (expondo `PipelineResult.decision`). CLI: `decide`.

---

## 9. Memory — Context, Learning, Project Brain, Semantic Knowledge

### 9.0 Knowledge — Engine, Providers e as três memórias (ADR-0013/14/15)
**As três memórias do projeto:** **Project Brain** = memória *operacional*
(estado atual), **Obsidian** = memória *organizacional* (visão navegável), **Git**
= memória *histórica* (registro imutável). O **Knowledge Engine** (`knowledge/
engine.py`) é o **ponto único** que coordena e **mantém as três sincronizadas**, e
é o **ponto de acesso** por onde o Context Engine recupera conhecimento. Fluxo
canônico:

```
Project Brain → Knowledge Engine → Knowledge Providers → Obsidian
              → Context Engine → Agentes
```

**Nenhuma fonte é acoplada diretamente ao Context Engine** — tudo passa por um
`KnowledgeProvider` (camada abaixo de Memory; Brain **injetado** → **não importa**
Memory → sem ciclo). Um provider só **indexa/cataloga/recupera/enriquece/cria
relacionamentos**; **nunca decide, interpreta código ou gera respostas**.
Built-ins: **Filesystem, Git, Markdown, ADR, Project-Brain, Obsidian**;
`KnowledgeRegistry` os agrupa. CLI: `knowledge index|list|retrieve|sync|status`
(`sync`/`status` operam sobre as três memórias; `sync --commit` faz snapshot
opt-in no Git histórico).

**Knowledge Graph (ADR-0017):** o Knowledge Engine constrói automaticamente um
grafo tipado relacionando os elementos do projeto — `Service → API → Database →
Migration → Test → ADR → Bug → Feature → Sprint → Documentação → Obsidian` —
inferido do conhecimento estruturado (co-ocorrência por execução, bugs→features,
sprints, refs de ADR, links de docs; **nunca lendo código**). `graph()` e
`enrich_context(paths)`; o Context Engine adiciona os elementos relacionados ao
`AgentContext`. Serve **apenas para enriquecer o contexto** — **nunca decide,
interpreta código ou substitui o raciocínio do modelo**. CLI: `knowledge graph
[--format mermaid|json] [--query <path>]`.

**Obsidian como representação visual (ADR-0014):** além do provider leitor, o
`ObsidianSync` projeta o **estado atual do Project Brain** num vault navegável
(`.ai-project-assistant/obsidian/`) — uma nota por categoria (ADRs, Architecture, Roadmap,
Features, Services, APIs, Modules, Dependencies, Known Bugs, Decisions,
Retrospectives, Lessons Learned), **índice de navegação** (Home/MOC), **mapa de
relacionamentos** (Mermaid) e **backlinks** entre ADRs. **Nunca é fonte da
verdade** (reflete o Brain), **não duplica** (linka/sumariza), é **incremental**
(manifesto: só notas alteradas; notas do usuário intactas) e **automático** em
`pipeline.completed`/`adr.created`. CLI: `obsidian sync|status`.

### 9.1 Context Engine (`memory/context.py`, 3.0-S1)
Nenhum agente recebe o projeto inteiro. A **lista de arquivos vem do Filesystem
Provider** (§9.0, sem `os.walk` no engine); `ContextBuilder` + resolvers (Files,
Services, APIs, Tests, Docs, Dependencies) + **ranking de relevância** + **cache**
(`.ai-project-assistant/context-cache/`, chave = agent+hash(subtask)+versão) + **invalidação**
(HEAD/mtime). Docs são enriquecidos pelos providers Markdown/ADR e patterns pelo
Project-Brain. Publica `context.built` com `estimated_reduction`.

### 9.2 Learning Engine (`memory/learning.py`, 3.0-S2)
Assina `run.completed`/`review.completed`/`delivery.completed`; extrai
conhecimento (arquivos, padrões, agentes, deps, tempo, problemas, correções,
decisões) e atualiza o Brain (merge incremental + versão). **Nunca grava código.**
*No Pipeline é superado pela camada de Autonomous Learning (§9.5), que captura
um retrospecto mais rico.*

### 9.3 Project Brain — diretórios especializados (decisão #6)
Substitui o `architecture.json` monolítico por uma árvore:
```
.ai-project-assistant/brain/
├── architecture/   # visão de arquitetura (snapshots versionados)
├── modules/        # módulos/workspaces descobertos
├── services/       # serviços e seus contratos
├── apis/           # endpoints/contratos de API
├── database/       # schema, entidades, migrações conhecidas
├── workflows/      # workflows aprendidos/usados
├── patterns/       # padrões recorrentes do projeto
├── history/        # histórico de execuções (append-only, versionado)
├── knowledge/      # conhecimento consolidado
├── bugs/           # bugs e correções (conhecimento, não código)
├── decisions/      # decisões (resumos)
├── retrospectives/ # retrospectivas por execução
└── adr/            # ADRs (também referenciados por Governance)
```
```python
class ProjectBrain:
    def get(self, facet: str, key: str | None = None) -> dict
    def put(self, facet: str, key: str, record: dict) -> None   # incremental
    def append(self, facet: str, record: dict) -> str           # history/append-only
    def version(self) -> str
```
Migração compatível: ao subir, o `brain.py` lê o antigo `memory/architecture.json`
e popula `brain/architecture/` (sem perder dados).

### 9.4 Semantic Knowledge (decisão #8)
`memory/semantic.py` — **interfaces preparadas** para indexação vetorial/busca
semântica sobre arquitetura, decisões, padrões e histórico:
```python
class SemanticIndex(Protocol):
    def index(self, doc_id: str, text: str, meta: dict) -> None
    def search(self, query: str, k: int = 5) -> list["Hit"]
class NullSemanticIndex(SemanticIndex):   # default agora: no-op + fallback keyword
    ...
```
Implementação completa (embeddings/vetor) fica para versão futura, **sem** alterar
o núcleo — basta registrar um `SemanticIndex` real via SDK.

### 9.5 Autonomous Learning (`evolution/`, ADR-0012)
A plataforma **evolui com o próprio uso**. Após cada execução do Pipeline, aprende
automaticamente: **tempo, falhas, retrabalho, agentes utilizados, arquivos
alterados, padrões recorrentes, decisões e sucesso da estratégia** — gravando
**conhecimento, nunca código**. Reusa Brain/Experience/Semantic. Sete engines:
- **SelfImprovementEngine** — orquestra; assina o bus, acumula sinais por run
  (`pipeline.started`→`pipeline.completed`) e dispara o aprendizado. Emite
  `improvement.learned`/`brain.updated`. Expõe `insights()` e `recommendations()`.
- **ProjectEvolutionEngine** (ADR-0016) — após cada execução, **enriquece o
  conhecimento estruturado**: classifica os **caminhos/metadados** dos arquivos
  alterados (nunca lê código) nas facetas do Brain — **módulos, serviços, APIs,
  entidades (database), testes, integrações, dependências, padrões, bugs
  corrigidos, decisões técnicas, lições e arquivos relacionados** (paths). **Nunca
  armazena código nem respostas do modelo**; o guard `looks_like_code` é defesa
  secundária. `insights` mostra as contagens por faceta.
- **KnowledgeEvolution** — consolidação incremental/versionada no Brain
  (retrospecto + stats de sucesso por workflow + decisões + falhas).
- **PatternDiscovery** — minera conjuntos de agentes recorrentes, agentes
  propensos a falha e áreas quentes → facet `patterns`.
- **SimilarTaskDetector** — tarefas passadas similares via Semantic (reconstruído
  dos retrospectos; índice vetorial plugável via SDK).
- **RecommendationEngine** — recomenda agentes/workflow do que funcionou antes,
  com avisos (ex.: retrabalho histórico alto).
- **ExperienceAnalyzer** — agrega KPIs/tendências do Brain.
- **BrainOptimizer** — limita os logs append-only (`Brain.trim_log`) → Brain enxuto.

O Pipeline usa o `SelfImprovementEngine` no lugar do `LearningEngine` básico. CLI:
`insights`, `recommend "<goal>"`.

---

## 10. Governance — ADR, políticas, quality gates, checklists, regras, segurança (decisão #4)

`governance/`. Camada transversal que **escuta eventos** e aplica regras.
- **adr.py** — gera `.ai-project-assistant/brain/adr/ADR-NNNN-*.md` a cada decisão
  (eventos `*.decided`/`adr.created`).
- **policies.py** — regras arquiteturais e `domain_rules` (tenant/PII), versionadas.
- **quality_gates.py** — gates booleanos: testes presentes, `protected_paths`
  intactos, cobertura mínima, sem mudança crítica sem review. Um gate reprovado
  **bloqueia** o avanço do Workflow.
- **checklists.py** — checklists por etapa/agente (alimenta task/PR).
Governance nunca é importada pelo núcleo; o Workflow **consulta** os gates como
pré-condições de step.

---

## 11. Experience — métricas e aprendizado de uso (decisão #7)

`experience/metrics.py`. Registra, por execução, indicadores que permitem ao
framework **aprender com o próprio uso**:
tempo por etapa/agente, **retrabalho** (reexecuções/retries), performance, taxa
de falhas/sucesso, qualidade (cobertura, findings de review), precisão da seleção
de agentes (selecionados vs. usados), redução de contexto.
Persistência em `.ai-project-assistant/experience/` (séries append-only). Alimentado **só
por eventos**. Distingue-se de Observability: Observability = encanamento de
runtime (bus/logs/telemetria); Experience = **indicadores agregados ao longo do
tempo** para aprendizado.

---

## 12. Observability — event bus, logs, telemetria

`observability/`. `events.py` (EventBus pub/sub stdlib, síncrono, nunca lança),
`logging.py` (JSONL em `.ai-project-assistant/logs/<run_id>.jsonl`), `telemetry.py`
(exportação/snapshot de métricas). Assinantes padrão: logging (tudo), Experience,
Governance, Learning.

---

## 13. Adapters — independência de modelo de IA

`adapters/base.py`:
```python
class AgentResult:  ok: bool; changed_files: list[str]; notes: str; error: str|None; duration_ms: int
class AgentAdapter(Protocol):
    name: str
    # `mode` é opcional (keyword); só é passado a adapters que o declaram.
    def run(self, *, agent, context, instructions, mode=ExecutionMode.EXECUTE) -> AgentResult: ...
```
`DryRunAdapter` (default; não altera nada) · **`ClaudeCodeAdapter`** (implementado,
ver ADR-0009) · futuros modelos via `register_adapter`. A Execution Engine recebe
o adapter por injeção → trocar de modelo não toca o núcleo.

**ClaudeCodeAdapter** (`adapters/claude_code.py`): encapsula toda a comunicação
com o CLI do Claude Code e é **mode-aware**:
- **DRY_RUN** — compõe o prompt, não invoca nada, zero efeito colateral.
- **TEST** — passada de validação (instrui o modelo a só avaliar viabilidade e
  NÃO modificar arquivos; pode receber `test_args` read-only).
- **EXECUTE** — execução real que pode alterar arquivos; detecta `changed_files`
  via git (best-effort).
Recursos: **timeout** por invocação, **retry** (`max_retries`), **cancel()**
(aborta tentativas e mata o processo em andamento), `AgentResult` padronizado. A
chamada ao CLI é injetável (`command_runner`) → 100% testável sem invocar o
modelo. O Kernel nunca conhece este adapter. CLI: `run/pipeline --adapter
claude-code` (default permanece `dry-run`, seguro).

---

## 14. Delivery Engine

`engines/delivery.py` + `orchestrator.py deliver --task <id>`: consolida lanes/
worktrees, gera `pull_request.md` (impacto/riscos/rollback), valida quality gates
(Governance), libera locks, atualiza status. Publica `delivery.completed`.

---

## 15. SDK e pontos de extensão (decisão #9)

`sdk/__init__.py` — superfície pública estável para estender **sem tocar no
núcleo**:
```python
register_agent(spec)        register_engine(name, factory)
register_workflow(workflow) register_adapter(name, adapter)
register_plugin(plugin)     register_tool(name, tool)
on(event_type, handler)     # assinar o event bus
```
- **Agents** — `config.json > extra_agents` ou `register_agent`.
- **Engines** — herdam `BaseEngine` (contrato de modos) + `register_engine`.
- **Workflows** — `Workflow` + `register_workflow`.
- **Adapters** — `AgentAdapter` + `register_adapter` (independência de modelo).
- **Plugins** — pacotes que registram um conjunto coeso (agents+engines+workflows)
  via hook `setup(sdk)`.
- **Tools** — utilitários invocáveis por agentes (ex.: busca, formatação),
  registrados e descobertos por nome.

---

## 16. Modelo de eventos

`dominio.acao` (namespacing). Principais: `run.started|completed|failed`,
`task.created|state_changed|ready|blocked|started|completed|failed|retrying|
cancelled|skipped`, `engine.dry_run|test|execute`, `agent.selected|dispatched`,
`context.built`, `gate.passed|failed`, `review.completed`, `delivery.completed`,
`brain.updated`, `adr.created`, `*.decided`. Cada evento: `type, ts, run_id,
node_id, payload`.

---

## 17. Comunicação entre módulos

1. **Chamada direta por interface** (dados): Workflow/Schedulers chamam engines,
   que retornam `EngineResult`/dataclasses.
2. **Eventos** (efeitos transversais): Governance, Observability, Experience e
   Learning **apenas escutam**. Nenhuma engine de domínio importa essas camadas.

Resultado: adicionar gate/telemetria/aprendizado **não altera** as engines
(Aberto/Fechado).

---

## 18. Fluxo completo (Pipeline único 4.0)

Workflow `full-dev`, cada step com gate de Governance e modo (Dry/Test/Execute):
```
request → Audit → Architecture → Intelligence(Plan/Dependency/Risk/Estimation)
        → Context → Dispatcher → Execution(runner=Adapter) → Review → Delivery
        → Learning → Brain.update → Experience.record
```
Nenhuma etapa pode ser pulada; cada uma é observável e passa por quality gate.
Comando: `orchestrator.py pipeline "<objetivo>" [--mode dry_run|test|execute]`.

---

## 19. Compatibilidade retroativa

| Risco | Mitigação |
|-------|-----------|
| `from aies import …` | `aies/__init__.py` reexporta tudo (atual + novo) |
| Comandos do CLI | preservados; `run/deliver/pipeline` são **adicionados** |
| `.ai-project-assistant/` | inalterado; novas pastas são aditivas |
| `brain/` dir-based vs. `memory/architecture.json` | migração automática lê o antigo e popula o novo; antigo mantido |
| `config.json` | novas chaves opcionais com default |
| Mutação acidental de código | **Dry Run default** + gate de modos (decisão #2) |
| Versionamento | SemVer; remoções só em major, com deprecation + warnings |

Cada PR **adiciona**; nenhuma remoção de superfície pública no mesmo PR.

---

## 20. Evolução por versão
- **2.0 (Execução):** S1 Execution Engine (Kernel+Workflow+Schedulers+modos+
  Adapter+governance/adr+events); S2 Agent Dispatcher.
- **3.0 (Memória):** S1 Context Engine; S2 Learning Engine + Project Brain
  (dir-based) + Semantic stub + Experience.
- **4.0 (Plataforma):** Pipeline único + Observability/telemetria completa +
  Governance gates no pipeline + SDK (plugins/tools) + consolidação.

---

## 21. Roadmap de PRs (pequenos, testados, documentados, compatíveis)

| PR | Conteúdo | Depende |
|----|----------|---------|
| **PR-0** | `foundation/` + skeleton de pacotes + fachada `aies/__init__` + reexports de compat + testes de compat | — |
| **PR-1** | Kernel (`domain`,`states`,`lifecycle`,`engine`+modos) + `observability/events` (EventBus) + testes | PR-0 |
| **PR-2** | **Execution Engine** + `adapters/base`+`dryrun` + `workflow` mínimo + `governance/adr` (ADR-0001) + comando `run` + testes | PR-1 |
| **PR-3** | **Agent Dispatcher** + Strategy + ADR-0002 + testes | PR-2 |
| **PR-4** | **Context Engine** + resolvers + cache + métrica de redução + testes | PR-1 |
| **PR-5** | **Project Brain (dir-based)** + Learning + Semantic stub + Experience + migração compat + testes | PR-1, PR-4 |
| **PR-6** | **Delivery Engine** (`deliver`) + quality gates (Governance) + testes | PR-1 |
| **PR-7** | **Pipeline único** (`pipeline`) integrando tudo + ADR | PR-2..6 |
| **PR-8** | **Observability/telemetria** completa + KPIs (Experience) | PR-7 |
| **PR-9** | **SDK** (agents/engines/workflows/adapters/plugins/tools) + docs de extensão | PR-7 |
| **PR-10** | Consolidação: relocação física, remover duplicação/código morto, suíte completa, docs finais | todos |

Suíte `aies/tests/` (unittest) cresce a cada PR.

---

## 22. Mapa "ajuste aprovado → onde foi atendido"
| # | Ajuste | Seções |
|---|--------|--------|
| 1 | Manter nome AIES | cabeçalho, §2, §3 |
| 2 | Dry Run obrigatório (Dry→Test→Execute) | §4, §7.1, §19 |
| 3 | Camada Workflow entre Kernel e Schedulers | §1, §5 |
| 4 | Governance | §10 |
| 5 | Intelligence | §8 |
| 6 | Brain dir-based | §9.3 |
| 7 | Experience | §11 |
| 8 | Semantic Knowledge (preparado) | §9.4 |
| 9 | SDK (Agents/Engines/Workflows/Adapters/Plugins/Tools) | §15 |
