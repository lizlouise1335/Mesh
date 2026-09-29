# Mesh — Capstone Plan v2

Repo: https://github.com/lizlouise1335/Mesh

**Deadline:** January 31, 2027
**Goal:** Learn systems/cloud engineering for data-intensive applications, and learn to build agentic systems (LangChain / LangGraph / MCP), by building an explainable college-lacrosse fit engine (usable alongside NCSA / SportsRecruits / ConnectLAX, not instead of them) and evolving it from a monolith to a distributed, agentic, production-hardened system.

**Two rules**

> Only P0 issues are required for January 31. P1/P2 never delay a milestone.
> Shipping fewer concepts deeply beats shipping more features.

---

## What changed from v1

- **Scale is manufactured on purpose.** The dataset is ~1M athletes / 50k recruiting needs, and full match recomputation is a batch job that takes minutes. Every distributed-systems and performance issue optimizes *that* workload, so caching, queues, and profiling have real reasons to exist.
- **Cloud infrastructure is a thread, not a checkbox.** Terraform from week 1; managed Postgres, queue, cache, and container runtime are provisioned, not hand-clicked.
- **Cut:** interest state machine, real-time updates, coach agent, RAG, architecture-evolution doc (merged into final design doc). None of them taught systems or agents anything the remaining issues don't.
- **Moved:** auth/RBAC to November (needed before agents, not before matching). Prompt-injection tests to December (they belong next to the agent).
- **Niched to lacrosse.** Programs are real (public rosters, positional needs by grad year, academic profiles); athletes stay synthetic (minors, PII). The product wedge is explainable fit for athletes and club coaches — single-player value that needs no college coach to log in.
- **Result:** 38 issues, ~120 points. October is 12 issues / ~36 points.

---

## GitHub Project setup

**Fields**

| Field | Values |
|---|---|
| Status | Backlog / Ready / In Progress / Review / Done |
| Milestone | Oct Foundations / Nov Distributed / Dec Agents / Jan Production |
| Sprint | Oct W1 … Jan W4 |
| Type | Feature / Infrastructure / Data / Test / Documentation |
| Area | Backend / Data / Matching / Infra / Distributed / MCP / Agents / Security / Observability / Frontend |
| Priority | P0 / P1 / P2 |
| Estimate | 1 / 2 / 3 / 5 |
| Learning Target | short text |

**Milestones (with due dates)**

- Oct Foundations — 2026-10-31
- Nov Distributed — 2026-11-30
- Dec Agents — 2026-12-31
- Jan Production — 2027-01-31

**Views**

- Roadmap — grouped by Milestone
- Current Sprint — filter: Sprint = current, Priority = P0
- Learning Targets — grouped by Area
- Icebox — Status = Icebox, hidden from everything else

**Labels:** one per Area, one per Priority, one per Type. Every issue gets exactly one of each.

**Issue template:** Deliver / Done when / Learning. If an issue lacks any of the three, it stays in Backlog.

---

# Milestone 1 — Foundations & Infrastructure as Code
**Due Oct 31**

Definition of done for the month:

> `terraform apply` from an empty cloud account produces a running platform. Athlete profile → coach recruiting need → ranked, explainable matches. A full batch recompute over 1M athletes runs end-to-end and its runtime is recorded.

### Oct W1 (Oct 1–7) — Decide and provision

#### #1 Architecture v0 + ADRs
**P0 · Documentation · 2**
Deliver: architecture diagram, module boundaries, ADRs for cloud provider, IaC tool, language/framework, ORM/query layer, container runtime, deployment target.
Done when: you can explain the request path browser → API → DB, and the batch path scheduler → worker → DB.
Learning: system boundaries, ADRs.

#### #2 Infrastructure v0 (Terraform)
**P0 · Infrastructure · 5**
Deliver: Terraform for network, managed PostgreSQL, container runtime (ECS/Cloud Run/etc.), secrets, IAM roles, a deployed hello-world service. Separate dev/prod state.
Done when: `terraform destroy` then `terraform apply` yields a reachable service backed by a fresh database. No console clicks.
Learning: IaC, cloud networking/IAM basics, environment separation.

#### #3 Domain model + ER diagram
**P0 · Data · 3**
Model: User, Athlete, Coach, Program, RecruitingNeed, AthletePreference, Match, Interest. Document cardinalities and ownership.
Done when: every relationship is explainable and drawn.
Learning: relational modeling, normalization.

### Oct W2 (Oct 8–14) — Data at scale

#### #4 PostgreSQL schema + migrations
**P0 · Data · 3**
PKs/FKs, constraints, indexes, migrations.
Done when: DB can be destroyed and rebuilt from migrations alone.
Learning: PostgreSQL fundamentals.

#### #5 Real program ingestion + synthetic athletes at scale
**P0 · Data · 5**
Deliver: (a) ingestion pipeline for every NCAA D1/D2/D3 + MCLA lacrosse program (~900 men's + women's): school, division, conference, region, roster by position and grad year, academic profile from public sources (IPEDS / Common Data Set). Idempotent re-runs. (b) Streaming generator producing ~1M synthetic athletes and ~50k recruiting needs derived from real roster gaps, with realistic distributions (position, grad year, GPA, test scores, region, club, athletic level). Loads via COPY/bulk insert.
Done when: one command builds the full dataset; program data is real and re-ingestable; a naive unindexed query over athletes is measurably slow; a 10k dev subset exists.
Learning: ingestion pipelines, bulk loading, why indexes matter.

#### #6 API foundation
**P0 · Backend · 3**
Routing, validation, standardized errors, service layer, repository layer, health check.
Done when: health check + one full resource flow works end-to-end in the deployed environment.
Learning: backend architecture.

### Oct W3 (Oct 15–21) — Resources and matching spec

#### #7 Athlete / Program / RecruitingNeed CRUD
**P0 · Backend · 3**
Done when: integration tests cover valid and invalid operations; expired needs cannot enter new matches.

#### #8 Match v1 specification
**P0 · Matching · 2**
Separate hard constraints, soft preferences, missing information, ranking signals. Define weights.
Done when: scoring model is written down. No matching code before this closes.

#### #9 Candidate generation + deterministic ranking
**P0 · Matching · 5**
Candidate generation filters incompatible pairs (gender/division, position, grad year, hard academics) in SQL against real programs. Ranking is weighted, deterministic, no LLM.
Done when: tests pin known ranking outcomes; ranking for one need over 1M athletes completes and its latency is recorded.
Learning: retrieval vs ranking, query planning.

### Oct W4 (Oct 22–31) — Batch workload and ship

#### #10 Explainable match output
**P0 · Matching · 2**
Return Strong / Weak / Missing factors per match.
Done when: "Why did A rank above B?" is answerable without reading scores.

#### #11 Full batch match recompute
**P0 · Data · 3**
A job that recomputes matches for every active recruiting need against the full dataset and persists results.
Done when: it runs to completion on the deployed platform; runtime, rows written, and DB load are recorded. This number is the baseline for everything in November.
Learning: batch processing, write throughput.

#### #12 Deploy October MVP + CI
**P0 · Infrastructure · 3**
CI runs tests and builds/deploys on merge.
Done when: the October definition of done is demonstrable on the deployed environment.

#### #13 Thin UI
**P1 · Frontend · 2**
Edit athlete, edit need, browse matches, view explanation. No design work.

---

# Milestone 2 — Distributed & Data Pipeline
**Due Nov 30**

Definition of done:

> Recruiting-need updates trigger asynchronous match recomputation through a managed queue and horizontally scaled workers. Duplicate/delayed events and worker restarts don't corrupt state. Batch recompute is measurably faster than the October baseline.

### Nov W1 (Nov 1–7)

#### #14 Authentication + RBAC
**P0 · Security · 5**
Roles ATHLETE / COACH / ADMIN; resource ownership enforced.
Done when: tests prove cross-athlete and cross-program mutation is rejected.
Learning: authn vs authz, least privilege. (Prerequisite for agent authorization in December.)

#### #15 Domain event model
**P0 · Distributed · 2**
AthleteProfileUpdated, RecruitingNeedCreated/Updated, MatchesRecomputed, etc. Schema-versioned.
Learning: domain events, async boundaries.

### Nov W2 (Nov 8–14)

#### #16 Queue infrastructure (Terraform)
**P0 · Infrastructure · 3**
Managed broker (SQS/PubSub/etc.) plus DLQ, provisioned in Terraform. Producer → broker → consumer proven.

#### #17 Async match recomputation
**P0 · Distributed · 5**
Update → event → worker → matches recomputed. API responds immediately.
Done when: p95 API latency for need updates drops to the write-only cost; recompute completes in the background.

### Nov W3 (Nov 15–21)

#### #18 Idempotency, retries, dead-letter handling
**P0 · Distributed · 3**
Deliver the same event twice; inject failing messages.
Done when: duplicates don't corrupt state; poison messages land in the DLQ without blocking.
Learning: at-least-once semantics.

#### #19 Redis caching (Terraform)
**P0 · Infrastructure · 3**
Choose what deserves caching and document why. Managed Redis in Terraform.
Done when: before/after latency measured and written down; cache invalidation on relevant events.

### Nov W4 (Nov 22–30)

#### #20 Partitioned batch + horizontal workers
**P0 · Distributed · 3**
Split full recompute into partitions; scale workers out.
Done when: recompute runtime vs worker count is plotted; a clear speedup over the October baseline is shown, with the point of diminishing returns identified.
Learning: work partitioning, scaling limits, DB as the bottleneck.

#### #21 Distributed failure tests
**P0 · Test · 3**
Duplicate/delayed events, consumer restart mid-batch, cache down, broker down.

#### #22 Architecture v1 → v2 retrospective
**P0 · Documentation · 1**
What sync v1 looked like, why async, what new failure modes appeared. Interview material.

---

# Milestone 3 — MCP & Agent Engineering
**Due Dec 31**

Definition of done:

> An athlete asks a LangGraph agent a recruiting question; the agent uses MCP tools under that user's permissions, checkpoints its state, drafts outreach, and waits for human approval. An eval suite grades it.

### Dec W1 (Dec 1–7) — MCP

#### #23 Mesh MCP server
**P0 · MCP · 5**
Tools: search_programs, get_program, get_recruiting_need, get_athlete_profile, calculate_fit, explain_fit. You write the schemas, validation, error contracts, and resources yourself.
Done when: tools are callable from a generic MCP client with validated inputs and typed errors.
Learning: MCP fundamentals, tool contracts.

#### #24 MCP authorization boundaries
**P0 · Security · 3**
Agent inherits the calling user's RBAC scope, never platform-wide access.
Done when: tests show an athlete-scoped agent cannot read another athlete or mutate a program.

### Dec W2 (Dec 8–14) — First agent

#### #25 Athlete recruiting agent (LangChain) + tracing
**P0 · Agents · 5**
"Find CS programs within six hours of Arlington where a 2028 midfielder with my profile fits." Runs against real programs; must use the MCP tools. Tracing shows request → reasoning → tool → args → result → next tool → response.
Learning: tool calling, structured output, tool loops, observability of agents.

### Dec W3 (Dec 15–21) — LangGraph

#### #26 Convert to LangGraph with conditional workflow
**P0 · Agents · 5**
Explicit state, nodes, edges. Branch on "enough athlete information?" → ask user vs search → rank → explain.
Learning: graph-based agent control flow.

#### #27 Persistence / checkpointing
**P0 · Agents · 2**
Workflow survives process restart mid-conversation.

#### #28 Human approval boundary
**P0 · Agents · 2**
Agent drafts outreach; cannot send. User approves first.
Learning: human-in-the-loop.

### Dec W4 (Dec 22–31) — Evaluation and abuse

#### #29 Agent evaluation suite
**P0 · Test · 5**
50–100 synthetic cases. Measure tool selection, argument validity, retrieval correctness, ranking consistency, unsupported claims, unauthorized action attempts.
Not optional.

#### #30 Prompt-injection / tool-abuse tests
**P0 · Security · 3**
Try to make the agent leak unauthorized data, invoke forbidden tools, override role. Document what worked and the fix.

---

# Milestone 4 — Production Engineering
**Due Jan 31**

Definition of done:

> The system is observable end-to-end, has been load-tested with recorded p50/p95/p99, one real bottleneck has been found and fixed with before/after numbers, and it degrades gracefully under injected failures.

### Jan W1 (Jan 1–7)

#### #31 Threat model
**P0 · Security · 2**
Assets, actors, trust boundaries, PII, minors' data, agent attack surface, mitigations.

#### #32 End-to-end observability
**P0 · Observability · 5**
Structured logs, metrics, distributed traces, correlation IDs across API → queue → worker → agent → MCP. Dashboards: API latency, errors, queue depth, worker failures, matching duration, agent latency/errors. Alerts on the three that matter most.

### Jan W2 (Jan 8–14)

#### #33 Load testing
**P0 · Test · 3**
p50/p95/p99, requests/sec, matching jobs/sec, event throughput. Recorded, not eyeballed.

#### #34 Find and fix one real bottleneck
**P0 · Distributed · 5**
Cannot close with "seems fast." Profile, identify something measurable, change the design, compare before/after.

### Jan W3 (Jan 15–21)

#### #35 Failure-injection exercise
**P0 · Test · 3**
Kill cache, worker, LLM call, event consumer, DB failover. Document behavior and any fixes.

#### #36 Cost review
**P1 · Infrastructure · 1**
What does this cost per month? What would you cut at 10x traffic vs 0 traffic?

### Jan W4 (Jan 22–31) — Portfolio finish

#### #37 Final system design document
**P0 · Documentation · 3**
Requirements, capacity assumptions, schema, APIs, architecture, consistency, caching, queues, scaling, failure modes, security, agents/MCP, alternatives considered — plus the V1 → V2 → V3 → V4 evolution and why each transition happened.

#### #38 README + recorded demo + interview stories
**P0 · Documentation · 3**
README a hiring manager understands in ~2 minutes. Demo: coach creates need → async matching → athlete asks agent → agent uses MCP → user approves action. Five stories: architecture decision, distributed failure, hard bug, security decision, agent/eval failure.

---

## Icebox

Not part of the January capstone.

```text
Interest state machine (DISCOVERED → SAVED → …)
Real-time updates (WebSockets/SSE)
Coach recruiting agent
Knowledge retrieval / RAG
Native mobile app
Video hosting/transcoding
Social feed
Payments/subscriptions
Coach CRM
Calendar integrations
Real athlete data (any)
Other sports
Production email delivery
ML-trained recommendation model
Scraping recruiting websites
Scholarship prediction
Parent accounts
Push notifications
Profile customization / design polish
```
