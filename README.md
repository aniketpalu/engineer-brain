# Developer Brain

A structured thinking and operating model for AI agents. Instead of giving agents memory, it teaches them how to approach engineering work: how to explore a codebase, make architecture decisions, break down tasks, document reasoning, and hand off context to the next session.

Works as a personal second brain for software development — designed to be used alongside AI coding assistants like Cursor, Copilot, and Claude.

## What It Is

The Brain is a directory of markdown files organized by project, feature, and workflow stage. Instead of losing context across chat sessions, Jira tickets, and scattered notes, everything lives here in a structure that both humans and AI agents can navigate.

## Quick Start

```bash
# Start a session (interactive — generates a ready-to-paste AI prompt)
python3 brain.py start

# Full prompt with all rules embedded (for non-Cursor tools)
python3 brain.py start --full

# Create structures directly:
python3 brain.py project feast
python3 brain.py feature feast oidc
python3 brain.py bug feast registry-crash
python3 brain.py task setup-ci                     # brain-level task
python3 brain.py task feast add-retry-logic         # project-level task
python3 brain.py research compare-graph-dbs         # brain-level research
python3 brain.py research feast auth-patterns       # project-level research
python3 brain.py review oidc-pr-6089                # brain-level PR review
python3 brain.py review feast oidc-pr-6089          # project-level PR review

# Security audit:
python3 brain.py check
```

Run all commands from the brain root directory (same level as `projects/` and `prompts/`).

## Directory Structure

```
brain/
  brain.py                    # CLI tool for scaffolding and session setup
  .cursor/rules/              # Persistent behavioral rules for AI agents (auto-generated)
    developer-brain.mdc       # System rules, principles, documentation discipline
    checkpoint.mdc            # Mandatory checkpoint enforcement (per-response)
    brain-evolution.mdc       # Self-evolution: persona, pattern recognition
    brain-security.mdc        # Credential protection (highest priority)
  shared/                     # Cross-project resources
    playbooks/                # Reusable workflows
    knowledge/                # General reference material
    persona.md                # User preferences, shortcuts, learned patterns
  prompts/
    start.prompt              # Full rules file (used by --full mode)
  projects/
    <project_name>/
      technical/
        features/             # Feature work (design, implementation, tracking)
          <feature_name>/
            checkpoint.md     # Session state — READ FIRST, UPDATE LAST
            intent.md         # Goal, motivation, constraints, source repos
            exploration.md    # Code analysis, findings, gap analysis
            architecture.md   # Design options, decisions, tradeoffs
            tasks.md          # Work breakdown, status tracking
            tests.md          # Test strategy, test cases, results
            implementation.md # Summary of changes, code flow
            artifacts.md      # Docker images, PRs, configs, outputs
        bugfix/               # Bug investigations and fixes
          <bug_name>/
            checkpoint.md, problem.md, investigation.md,
            fix_plan.md, fix_summary.md, tests.md
        tasks/                # Project-level lightweight tasks
          <task_name>/
            checkpoint.md, task.md
        research/             # Project-level research
          <research_name>/
            checkpoint.md, research.md
        reviews/              # Project-level PR reviews
          <review_name>/
            checkpoint.md, review.md
        playbooks/            # Repeatable workflows (build, test, deploy)
        system/               # Architecture diagrams, system maps
        knowledge/            # Reference material, learnings
      non_technical/          # Non-engineering docs
  tasks/                      # Brain-level standalone tasks
    <task_name>/
      checkpoint.md, task.md
  research/                   # Brain-level standalone research
    <research_name>/
      checkpoint.md, research.md
  reviews/                    # Brain-level standalone PR reviews
    <review_name>/
      checkpoint.md, review.md
```

## How It Works

### Cursor Rules — Persistent Agent Behavior

The `.cursor/rules/` directory contains behavioral rules that Cursor loads on **every turn** of every conversation. Unlike prompt instructions that dilute over long chats, these persist:

- **`developer-brain.mdc`** — Brain structure, operating principles, approval system, documentation discipline, testing, playbook usage, knowledge promotion, role behavior, development principles.
- **`checkpoint.mdc`** — Non-negotiable checkpoint enforcement. Agents must read `checkpoint.md` first and update it (including prompt count and session log) after every response where meaningful work was done.
- **`brain-evolution.mdc`** — Self-evolution rules. Agents read `shared/persona.md`, respect user shortcuts, and suggest additions when patterns are noticed.
- **`brain-security.mdc`** — Credential protection. Agents never persist credentials in files, use environment variable references, and warn if credentials appear in chat.

`brain.py start` auto-creates these files if they don't exist — new users get the rules automatically.

### brain.py start — Session Setup

The interactive session setup command:

1. Auto-creates `.cursor/rules/` with all brain rules if missing
2. Auto-creates `shared/` directory with persona.md if missing
3. Asks scope: project work (feature/bugfix/task/research) or standalone (task/research)
4. If new — creates the structure automatically
5. Auto-discovers repos from `intent.md`, task progress from `tasks.md`, playbooks and knowledge
6. Lists shared resources and persona alongside project resources
7. Generates a **slim prompt** (~25 lines of session context) and copies to clipboard

For non-Cursor tools, use `brain.py start --full` to generate a comprehensive prompt with all rules embedded.

### checkpoint.md — The Handoff

Every work item (feature, bugfix, task, research) includes a `checkpoint.md` that tracks:

- **Current phase** (intent, exploration, architecture, implementation, testing, complete)
- **Last updated** date and time
- **Prompt count** — incremented after every response; acts as the trigger for checkpoint updates
- **Summary** of progress so far
- **Active focus** — what to work on next
- **Next steps** — concrete actions
- **Relevant docs** — which brain docs matter for the current phase
- **Dependencies** — related projects, blocking items, playbooks
- **Session log** — append-only table with date, time, and summary per prompt

The checkpoint rule enforces updates **after every response where work was done**. The prompt count increment is the trigger — if the count goes up, the checkpoint must be updated. This matters because chat sessions degrade over time — continuous checkpointing ensures the last checkpoint is always current, even if the chat is abandoned.

### Work Types

| Type | Scope | Use Case |
|------|-------|----------|
| **Feature** | Project | Full lifecycle: intent → exploration → architecture → implementation → testing |
| **Bugfix** | Project | Problem → investigation → fix plan → fix → validation |
| **Task** | Project or Brain-level | Lightweight single-focus action (fix CI, set up hooks, refactor module) |
| **Research** | Project or Brain-level | Question-driven exploration (compare databases, evaluate auth patterns) |
| **Review** | Project or Brain-level | PR review with structured analysis (intent, impact, assumptions, edge cases, verdict) |

Tasks and research can be standalone (brain-level: `tasks/<name>/`, `research/<name>/`) or project-specific (`projects/<project>/technical/tasks/<name>/`).

### PR Reviews — Structured Code Review

PR reviews use a structured template that forces critical thinking beyond "what changed":

- **Intent** — why does this PR exist? What problem does it solve?
- **Architecture Impact** — what existing code paths are affected?
- **Assumptions vs Reality** — what the author assumed vs what can actually happen (table format)
- **Edge Cases & Failure Modes** — partial failure, concurrent access, malformed data
- **Missing** — tests not written, error handling absent, documentation gaps
- **Verdict** — ONLY set by the user. The agent presents all findings and asks for the verdict.

The Reviewer role thinks from the perspective of the system under load, under bad input, under partial failure — not just the happy path the author tested.

### Shared Directory — Cross-Project Resources

`shared/` contains resources accessible to all projects:

- **`shared/playbooks/`** — Workflows useful across multiple projects
- **`shared/knowledge/`** — General reference material and learned patterns
- **`shared/persona.md`** — User shortcuts, preferences, and patterns the brain learns over time

Knowledge promotion: when a task, research, or feature produces reusable knowledge, the agent suggests promoting it to `shared/`. Nothing moves without user approval.

### Self-Evolution

The brain learns from usage through `shared/persona.md`:

- **Shortcuts** — abbreviations you use (WDYT, LGTM, IDTS) with their intended meaning
- **Question patterns** — how you prefer to explore and understand systems
- **Preferences** — working style, communication style, depth expectations
- **Learned patterns** — behaviors observed over time, added by agent suggestion

The `brain-evolution.mdc` rule instructs agents to watch for patterns and suggest additions. The brain grows through natural conversation, not manual configuration.

### Security

Multi-layered credential protection:

1. **Behavioral** (`brain-security.mdc`) — agents never persist credentials in files, use env var references, warn about chat-history exposure
2. **Mechanical** (`brain.py check`) — regex scanner with ~15 patterns for AWS keys, GitHub tokens, private keys, Slack tokens, OpenAI keys, URL credentials, and more
3. **Pre-prompt** — `brain.py start` scans the generated prompt for credentials before copying to clipboard; warns and asks for confirmation if found

### Multi-Agent Workflow

Different agents can work on the same feature because the Brain is the shared context:

- Agent 1 explores code → writes to `exploration.md` → updates `checkpoint.md`
- Agent 2 reads `checkpoint.md` → proposes architecture in `architecture.md`
- Agent 3 implements → updates `implementation.md`, `tasks.md`, and `tests.md`

Each agent reads `checkpoint.md` first, so context isn't lost between sessions.

## Commands

| Command | What It Does |
|---------|-------------|
| `python3 brain.py start` | Interactive session setup — slim prompt (Cursor rules active) |
| `python3 brain.py start --full` | Full prompt with all rules embedded (for non-Cursor tools) |
| `python3 brain.py project <name>` | Create a new project with full directory structure and starter playbooks |
| `python3 brain.py feature <project> <name>` | Create a feature directory with all documentation templates |
| `python3 brain.py bug <project> <name>` | Create a bugfix directory with investigation templates |
| `python3 brain.py task <name>` | Create a brain-level task |
| `python3 brain.py task <project> <name>` | Create a project-level task |
| `python3 brain.py research <name>` | Create a brain-level research |
| `python3 brain.py research <project> <name>` | Create a project-level research |
| `python3 brain.py review <name>` | Create a brain-level PR review |
| `python3 brain.py review <project> <name>` | Create a project-level PR review |
| `python3 brain.py check` | Audit all brain docs for credential patterns |

## Key Rules

- **Cursor rules are the foundation.** `.cursor/rules/` files persist on every turn — agents can't forget them. `brain.py` auto-creates them for new users.
- **`checkpoint.md` is the handoff.** Read first, update after every meaningful response. Prompt count is the trigger — increment it, update the checkpoint. This is what makes multi-session and multi-agent work seamless.
- **`intent.md` is the starting point.** Every feature must have one. It includes a "Source Repositories" table — the single source of truth for where code lives.
- **Documentation is immediate.** Brain docs are updated as work happens, not deferred to the end.
- **Knowledge is promoted, not siloed.** Reusable outcomes from any work type get suggested for promotion to `shared/`.
- **Credentials never persist.** Brain docs reference env vars, never raw secrets. `brain.py check` catches violations.
- **The brain evolves.** `persona.md` captures user patterns over time. Agents suggest additions; users approve.
