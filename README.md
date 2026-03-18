# Developer Brain

A structured knowledge system for engineering thinking, documentation, and planning. Works as a personal second brain for software development — designed to be used alongside AI coding assistants.

## What It Is

The Brain is a directory of markdown files organized by project, feature, and workflow stage. Instead of losing context across chat sessions, Jira tickets, and scattered notes, everything lives here in a structure that both humans and AI agents can navigate.

## Quick Start

```bash
# Create a new project
python3 brain.py project feast

# Create a feature inside a project
python3 brain.py feature feast oidc

# Create a bugfix inside a project
python3 brain.py bug feast registry-crash
```

## Directory Structure

```
brain/
  prompts/                  # AI agent prompts (start.prompt)
  projects/
    <project_name>/
      technical/
        features/           # Feature work (design, implementation, tracking)
          <feature_name>/
            intent.md       # Goal, motivation, constraints, source repos
            exploration.md  # Code analysis, findings, gap analysis
            architecture.md # Design options, decisions, tradeoffs
            tasks.md        # Work breakdown, status tracking
            tests.md        # Test plan, test cases, results
            implementation.md # Summary of changes, code flow
            artifacts.md    # Docker images, PRs, configs, outputs
        bugfix/             # Bug investigations and fixes
          <bug_name>/
            problem.md
            investigation.md
            fix_plan.md
            fix_summary.md
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

## Using with AI Agents

The Brain is designed to work with AI coding assistants (Cursor, Copilot, etc.). The `prompts/` directory contains system prompts that teach the agent how to operate within the Brain.

### start.prompt

The primary system prompt. Paste it at the beginning of a session to set the operating context. It instructs the agent to:

- Prioritize understanding before proposing solutions
- Document findings in the Brain instead of long chat responses
- Propose changes with intent/reasoning/risks before executing
- Check playbooks for repeatable workflows
- Make thinking visible (assumptions, uncertainties, conclusions)

### How to Start a Session

1. Open the Brain workspace in your IDE
2. Paste `start.prompt` content to the AI agent
3. Tell the agent which project/feature you're working on
4. The agent reads the existing Brain docs for context and picks up where you left off

### Multi-Agent Workflow

Different agents can work on the same feature because the Brain is the shared context:

- Agent 1 explores code → writes to `exploration.md`
- Agent 2 reads exploration → proposes architecture in `architecture.md`
- Agent 3 implements → updates `implementation.md`, `tasks.md`, and `tests.md`

Each agent reads the Brain first, so context isn't lost between sessions.

## Commands

| Command | What It Does |
|---------|-------------|
| `python3 brain.py project <name>` | Create a new project with full directory structure and starter playbooks |
| `python3 brain.py feature <project> <name>` | Create a feature directory with all documentation templates |
| `python3 brain.py bug <project> <name>` | Create a bugfix directory with investigation templates |

## Key Rules

- **`intent.md` is the starting point.** Every feature must have one. It includes a "Source Repositories" table — the single source of truth for where code lives.
- **Playbooks capture repeatable workflows.** If you discover a useful process, document it as a playbook. You can teach the skill to agent & let it document for future use by other agent.
- **Artifacts are tracked.** Docker images, PRs, configs — anything produced goes in `artifacts.md`.
- **Documentation is for future-you.** Write so another developer (or your future self) can understand the reasoning.
