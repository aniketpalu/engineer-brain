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
```

Run all commands from the brain root directory (same level as `projects/` and `prompts/`).

## Directory Structure

```
brain/
  brain.py                    # CLI tool for scaffolding and session setup
  .cursor/rules/              # Persistent behavioral rules for AI agents
    developer-brain.mdc       # System rules, principles, documentation discipline
    checkpoint.mdc            # Mandatory checkpoint enforcement (per-response)
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
            checkpoint.md
            problem.md
            investigation.md
            fix_plan.md
            fix_summary.md
            tests.md
        playbooks/            # Repeatable workflows (build, test, deploy)
        system/               # Architecture diagrams, system maps
        knowledge/            # Reference material, learnings
      non_technical/          # Non-engineering docs
```

## How It Works

### Cursor Rules — Persistent Agent Behavior

The `.cursor/rules/` directory contains behavioral rules that Cursor loads on **every turn** of every conversation. Unlike prompt instructions that dilute over long chats, these persist:

- **`developer-brain.mdc`** — Brain structure, operating principles, approval system, documentation discipline, testing, playbook usage, role behavior, development principles, transparency.
- **`checkpoint.mdc`** — Non-negotiable checkpoint enforcement. Agents must read `checkpoint.md` first and update it after every response where meaningful work was done.

`brain.py start` auto-creates these files if they don't exist — new users get the rules automatically.

### brain.py start — Session Setup

The interactive session setup command:

1. Auto-creates `.cursor/rules/` with brain rules if missing
2. Asks whether you're continuing existing work or starting something new
3. If new — creates the project/feature/bug structure automatically
4. Auto-discovers repos from `intent.md`, task progress from `tasks.md`, playbooks and knowledge files
5. Generates a **slim prompt** (~25 lines of session context) and copies to clipboard

The slim prompt contains only session context (project, feature, repos, task progress, file list). All behavioral rules live in Cursor rules and persist without being pasted.

For non-Cursor tools, use `brain.py start --full` to generate a comprehensive prompt with all rules embedded.

### checkpoint.md — The Handoff

Every feature and bugfix includes a `checkpoint.md` that tracks:

- **Current phase** (intent, exploration, architecture, implementation, testing, complete)
- **Last updated** date
- **Summary** of progress so far
- **Active focus** — what to work on next
- **Next steps** — concrete actions for the next session
- **Relevant docs** — which brain docs matter for the current phase

The checkpoint rule enforces updates **after every response where work was done**, not just at session end. This matters because chat sessions degrade over time — if the agent updates checkpoint.md continuously, the last checkpoint is always current even if the chat is abandoned.

### Multi-Agent Workflow

Different agents can work on the same feature because the Brain is the shared context:

- Agent 1 explores code → writes to `exploration.md` → updates `checkpoint.md`
- Agent 2 reads `checkpoint.md` → proposes architecture in `architecture.md`
- Agent 3 implements → updates `implementation.md`, `tasks.md`, and `tests.md`

Each agent reads `checkpoint.md` first, so context isn't lost between sessions.

## Feature Documentation Stages

Each feature follows a thinking progression:

1. **intent.md** — What are we building and why? Source repositories, constraints, open questions.
2. **exploration.md** — What did we find in the code? Gap analysis, existing infrastructure, key findings.
3. **architecture.md** — What approach did we choose? Options considered, tradeoffs, flow diagrams.
4. **tasks.md** — What work needs to be done? Prioritized breakdown, status tracking, scope decisions.
5. **tests.md** — How do we verify it works? Test strategy, test cases, edge cases, results.
6. **implementation.md** — What did we actually change? Files modified, design decisions, commit history.
7. **artifacts.md** — What did we produce? Docker images, PRs, config examples, scripts.

## Commands

| Command | What It Does |
|---------|-------------|
| `python3 brain.py start` | Interactive session setup — slim prompt (Cursor rules active) |
| `python3 brain.py start --full` | Full prompt with all rules embedded (for non-Cursor tools) |
| `python3 brain.py project <name>` | Create a new project with full directory structure and starter playbooks |
| `python3 brain.py feature <project> <name>` | Create a feature directory with all documentation templates |
| `python3 brain.py bug <project> <name>` | Create a bugfix directory with investigation templates |

## Key Rules

- **Cursor rules are the foundation.** `.cursor/rules/` files persist on every turn — agents can't forget them. `brain.py` auto-creates them for new users.
- **`checkpoint.md` is the handoff.** Read first, update after every meaningful response. This is what makes multi-session and multi-agent work seamless.
- **`intent.md` is the starting point.** Every feature must have one. It includes a "Source Repositories" table — the single source of truth for where code lives.
- **Documentation is immediate.** Brain docs are updated as work happens, not deferred to the end. After exploring → update `exploration.md`. After deciding → update `architecture.md`. No "I'll document later."
- **Playbooks capture repeatable workflows.** If you discover a useful process, document it as a playbook.
- **Artifacts are tracked.** Docker images, PRs, configs — anything produced goes in `artifacts.md`.
