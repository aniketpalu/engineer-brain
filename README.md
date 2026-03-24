# Developer Brain

A structured knowledge system for engineering thinking, documentation, and planning. Works as a personal second brain for software development — designed to be used alongside AI coding assistants.

## What It Is

The Brain is a directory of markdown files organized by project, feature, and workflow stage. Instead of losing context across chat sessions, Jira tickets, and scattered notes, everything lives here in a structure that both humans and AI agents can navigate.

## Quick Start

```bash
# Start a session (interactive — generates a ready-to-paste AI prompt)
python3 brain.py start

# Or create structures directly:
python3 brain.py project feast
python3 brain.py feature feast oidc
python3 brain.py bug feast registry-crash
```

Run all commands from the brain root directory (same level as `projects/` and `prompts/`).

## Directory Structure

```
brain/
  brain.py                  # CLI tool for scaffolding and session setup
  prompts/                  # AI agent prompts (start.prompt, develop.promt)
  projects/
    <project_name>/
      technical/
        features/           # Feature work (design, implementation, tracking)
          <feature_name>/
            checkpoint.md   # Session state — phase, summary, next steps
            intent.md       # Goal, motivation, constraints, source repos
            exploration.md  # Code analysis, findings, gap analysis
            architecture.md # Design options, decisions, tradeoffs
            tasks.md        # Work breakdown, status tracking
            tests.md        # Test strategy, test cases, results
            implementation.md # Summary of changes, code flow
            artifacts.md    # Docker images, PRs, configs, outputs
        bugfix/             # Bug investigations and fixes
          <bug_name>/
            checkpoint.md   # Session state
            problem.md      # Description, expected vs actual behavior
            investigation.md
            fix_plan.md
            fix_summary.md
            tests.md
        playbooks/          # Repeatable workflows (build, test, deploy)
        system/             # Architecture diagrams, system maps
        knowledge/          # Reference material, learnings
      non_technical/        # Non-engineering docs
```

## Feature Documentation Stages

Each feature follows a thinking progression:

1. **intent.md** — What are we building and why? Source repositories, constraints, open questions.
2. **exploration.md** — What did we find in the code? Gap analysis, existing infrastructure, key findings.
3. **architecture.md** — What approach did we choose? Options considered, tradeoffs, flow diagrams.
4. **tasks.md** — What work needs to be done? Prioritized breakdown, status tracking, scope decisions.
5. **tests.md** — How do we verify it works? Test strategy, test cases, edge cases, results.
6. **implementation.md** — What did we actually change? Files modified, design decisions, commit history.
7. **artifacts.md** — What did we produce? Docker images, PRs, config examples, scripts.

## checkpoint.md — Session Continuity

Every feature and bugfix includes a `checkpoint.md` file that tracks:

- **Current phase** (intent, exploration, architecture, implementation, etc.)
- **Last updated** date
- **Summary** of progress so far
- **Active focus** — what to work on next
- **Next steps** — concrete actions for the next session

This is the handoff between sessions. Instead of the agent reading all 7 docs every time, it reads `checkpoint.md` first to orient itself, then pulls specific docs as needed. The agent updates `checkpoint.md` before every session ends.

## Using with AI Agents

The Brain is designed to work with AI coding assistants (Cursor, Copilot, etc.). The `prompts/` directory contains system prompts that teach the agent how to operate within the Brain.

### brain.py start (recommended)

The interactive session setup command. It:

1. Asks whether you're continuing existing work or starting something new
2. If new — creates the project/feature/bug structure automatically
3. Auto-discovers repos from `intent.md`, task progress from `tasks.md`, available playbooks and knowledge files
4. Assembles a complete prompt from `start.prompt` rules + your session context
5. Copies the prompt to clipboard — just paste into your AI agent

No tokens wasted on setup questions. The agent starts with full context immediately.

### start.prompt

The rules file. Contains operating principles, approval system, documentation discipline, testing requirements, playbook usage, role-specific behavior, and transparency rules. `brain.py start` reads this file and includes it in the generated prompt.

### develop.promt

A supplementary prompt for active development sessions. Adds principles like:

- Test before theorize, one change at a time
- Don't assume existing code is correct — prove it
- Optimize for minimal API/database calls

Optionally included when running `brain.py start`.

### Multi-Agent Workflow

Different agents can work on the same feature because the Brain is the shared context:

- Agent 1 explores code → writes to `exploration.md` → updates `checkpoint.md`
- Agent 2 reads `checkpoint.md` → proposes architecture in `architecture.md`
- Agent 3 implements → updates `implementation.md`, `tasks.md`, and `tests.md`

Each agent reads `checkpoint.md` first, so context isn't lost between sessions.

## Commands

| Command | What It Does |
|---------|-------------|
| `python3 brain.py start` | Interactive session setup — generates a ready-to-paste AI prompt |
| `python3 brain.py project <name>` | Create a new project with full directory structure and starter playbooks |
| `python3 brain.py feature <project> <name>` | Create a feature directory with all documentation templates |
| `python3 brain.py bug <project> <name>` | Create a bugfix directory with investigation templates |

## Key Rules

- **`intent.md` is the starting point.** Every feature must have one. It includes a "Source Repositories" table — the single source of truth for where code lives.
- **`checkpoint.md` is the handoff.** The agent reads it first to know where things stand and updates it before ending every session. This is what makes multi-session work seamless.
- **Playbooks capture repeatable workflows.** If you discover a useful process, document it as a playbook. You can teach the skill to an agent and let it document for future use by other agents.
- **Artifacts are tracked.** Docker images, PRs, configs — anything produced goes in `artifacts.md`.
- **Documentation is for future-you.** Write so another developer (or your future self) can understand the reasoning.
