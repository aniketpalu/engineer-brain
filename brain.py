#!/usr/bin/env python3
"""
Developer Brain — structured knowledge system for engineering work.

Run from the brain root directory (same level as projects/ and prompts/).

Usage:
    python3 brain.py start                           Interactive session setup (slim prompt, assumes Cursor rules)
    python3 brain.py start --full                    Full prompt with all rules embedded (for non-Cursor tools)
    python3 brain.py project <project_name>          Create a new project
    python3 brain.py feature <project> <feature>     Create a feature
    python3 brain.py bug <project> <bug>             Create a bugfix
"""

import sys
from pathlib import Path
from datetime import date


# -------------------------
# FILESYSTEM HELPERS
# -------------------------

def create_dir(path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {path}/")


def create_file(path, content=""):
    if not path.exists():
        with open(path, "w") as f:
            f.write(content)
        print(f"  Created: {path}")


# -------------------------
# CURSOR RULES AUTO-SETUP
# -------------------------

_RULE_DEVELOPER_BRAIN = """\
---
description: Developer Brain — structured engineering knowledge system. Applies to ALL sessions in this workspace.
alwaysApply: true
---

# Developer Brain System

You are working inside a **Developer Brain** — a structured knowledge system for engineering work.
Brain documents are the source of truth. Prefer updating them over long chat responses.

## Structure

```
projects/<project>/technical/
  features/<feature>/    Feature lifecycle docs
  bugfix/<bug>/          Bug investigation docs
  playbooks/             Repeatable workflows
  system/                System architecture
  knowledge/             Reference material
```

## Feature Lifecycle (in order)

| File | Purpose |
|------|---------|
| checkpoint.md | Session state — READ FIRST, UPDATE LAST |
| intent.md | Goal, motivation, constraints, source repos |
| exploration.md | Code analysis, findings, gap analysis |
| architecture.md | Design options, selected approach, tradeoffs |
| tasks.md | Work breakdown, status tracking |
| implementation.md | What was changed and why |
| tests.md | Test strategy, cases, results |
| artifacts.md | Docker images, PRs, configs |

## Bugfix Lifecycle

| File | Purpose |
|------|---------|
| checkpoint.md | Session state — READ FIRST, UPDATE LAST |
| problem.md | Description, expected vs actual behavior |
| investigation.md | Logs, reproduction, observations |
| fix_plan.md | Root cause, proposed fix |
| fix_summary.md | Files changed, reasoning |
| tests.md | Validation of fix |

## Operating Principles

1. Prioritize understanding before action.
2. Never behave like a black-box code generator.
3. Explain what you know, what you infer, and what you are unsure about.
4. Prefer updating brain docs over long chat responses.
5. Keep reasoning structured and traceable.
6. Ask clarifying questions if anything is unclear.
7. Do NOT assume tasks without confirmation.

## Approval System

Request approval BEFORE:
- Modifying code
- Proposing implementation steps
- Updating architecture decisions
- Executing bug fixes

Include: intent, reasoning, files impacted, risks.

## Documentation Discipline

Continuously update brain docs as you work:
- After exploring → update exploration.md
- After deciding → update architecture.md
- After completing tasks → update tasks.md status
- After implementing → update implementation.md
- After testing → update tests.md
- After producing artifacts → update artifacts.md

If any document is missing or weak, suggest improvements.

## Testing Discipline

All validation must be recorded in tests.md:
- Test strategy, cases executed, edge cases
- Failures encountered, fixes applied
- Final validation status

## Playbook Usage

For repeatable workflows (builds, tests, deployments):
- Check `technical/playbooks/` first
- If a repeatable process is missing, suggest creating a playbook

## Role Behavior

**Developer**: Focus on system understanding, safe implementation plans, clear code changes, well-structured tasks.

**QE**: Focus on validation, edge cases, failure scenarios, challenging assumptions, system reliability.

## Development Principles

- Test before theorize. One change at a time. Simplest path first.
- Don't assume existing code is correct — prove it.
- No narratives — show test results.
- Avoid large in-memory operations; optimize for database-level work.
- Minimize API and database calls; optimize beyond your first instinct.

## Transparency

Always explain:
- What information you are using
- What conclusions you are drawing
- What uncertainties exist
"""

_RULE_CHECKPOINT = """\
---
description: MANDATORY checkpoint enforcement for Developer Brain. Non-negotiable. Applies to ALL sessions.
alwaysApply: true
---

# CHECKPOINT RULE — NON-NEGOTIABLE

This rule overrides all other priorities. No exceptions. No shortcuts.

---

## ON FIRST RESPONSE — Read checkpoint.md FIRST

1. Read `checkpoint.md` in the feature/bug directory BEFORE any other brain document.
2. It tells you: current phase, what to focus on, which docs to read next.
3. Do NOT read all brain docs upfront — only read what checkpoint.md and the task require.
4. Summarize state to the user before starting work.

---

## AFTER EVERY RESPONSE WHERE WORK WAS DONE — Update checkpoint.md

This is not a "session end" task. You update checkpoint.md **after each response** where
meaningful work was accomplished. Every single time. The reason: chat sessions degrade
over time and may be abandoned at any point. The last checkpoint must always be current.

Update ALL of the following sections:

- **Current Phase** — intent / exploration / architecture / implementation / testing / complete
- **Last Updated** — today's date
- **Summary** — what was accomplished (be specific, not vague)
- **Active Focus** — what the next response or session should pick up
- **Next Steps** — concrete numbered actions
- **Relevant Docs** — which brain docs matter for the current phase

---

## WHEN SWITCHING TASKS — Update checkpoint.md BEFORE switching

If the user asks you to shift focus within a conversation, update checkpoint.md
for the current task before moving to the new one.

---

## BRAIN DOC UPDATES — Immediate, not deferred

When you make a decision → update architecture.md NOW.
When you complete a task → update tasks.md NOW.
When you change code → update implementation.md NOW.
When you test something → update tests.md NOW.
When you produce an artifact → update artifacts.md NOW.

Do NOT say "I'll update the docs later." There is no later.

---

## WHY THIS EXISTS

checkpoint.md is what allows multiple chat sessions to work on the same feature.
Each chat reads the last checkpoint, does work, writes a new checkpoint.
If you skip the update, the next chat starts from zero and repeats work.

**Treat checkpoint.md as your most important output — more important than any code you write.**
"""

_CURSOR_RULES = {
    "developer-brain.mdc": _RULE_DEVELOPER_BRAIN,
    "checkpoint.mdc": _RULE_CHECKPOINT,
}


def _ensure_cursor_rules():
    """Create .cursor/rules/ with brain rules if any rule files are missing."""
    rules_dir = Path(".cursor/rules")
    created_any = False

    if not rules_dir.exists():
        rules_dir.mkdir(parents=True, exist_ok=True)
        created_any = True

    for filename, content in _CURSOR_RULES.items():
        path = rules_dir / filename
        if not path.exists():
            path.write_text(content)
            if not created_any:
                print()
            print(f"  Created Cursor rule: {path}")
            created_any = True

    if created_any:
        print("  Cursor rules are active — behavioral rules persist across all turns.\n")


# -------------------------
# PROJECT STRUCTURE
# -------------------------

def create_project(project_name):
    project_root = Path("projects") / project_name

    dirs = [
        "technical/features",
        "technical/bugfix",
        "technical/playbooks",
        "technical/system",
        "technical/knowledge",
        "non_technical",
    ]

    create_dir(Path("projects"))
    create_dir(Path("prompts"))

    for d in dirs:
        create_dir(project_root / d)

    playbooks = {
        "build_docker.md": "# Docker Build Playbook\n\nCommands to build docker images.\n",
        "run_tests.md": "# Test Playbook\n\nCommands to run tests.\n",
        "deploy_dev.md": "# Dev Deployment Playbook\n\nSteps to deploy to dev.\n",
        "experiment_template.md": "# Experiment Template\n\nGoal:\n\nSteps:\n\nResults:\n",
    }
    for name, content in playbooks.items():
        create_file(project_root / "technical/playbooks" / name, content)

    create_file(
        project_root / "technical/system/system_map.md",
        "# System Map\n\nHigh level architecture diagrams.\n",
    )

    print(f"\n  Project '{project_name}' initialized.\n")


# -------------------------
# FEATURE STRUCTURE
# -------------------------

def create_feature(project, feature_name):
    feature_dir = Path("projects") / project / "technical/features" / feature_name
    create_dir(feature_dir)

    today = date.today().isoformat()

    files = {
        "intent.md": (
            f"# Feature Intent\n\n"
            f"Feature: {feature_name}\n\n"
            f"## Goal\n\n"
            f"## Why Needed\n\n"
            f"## Constraints\n\n"
            f"## Source Repositories\n\n"
            f"| Repo | Local Path | Branch |\n"
            f"|------|------------|--------|\n"
            f"| | | |\n\n"
            f"## Questions\n"
        ),
        "exploration.md": (
            "# Code Exploration\n\n"
            "## Relevant Modules\n\n"
            "## Current Flow\n\n"
            "## Observations\n"
        ),
        "architecture.md": (
            "# Architecture Decision\n\n"
            "## Options Considered\n\n"
            "## Selected Approach\n\n"
            "## Tradeoffs\n"
        ),
        "tasks.md": (
            "# Task Breakdown\n\n"
            "## Overview\n\n"
            "## Tasks\n\n"
            "1.\n2.\n3.\n\n"
            "## Scope Decisions\n\n"
            "## Implementation Order\n"
        ),
        "implementation.md": (
            "# Implementation Summary\n\n"
            "## Files Changed\n\n"
            "## Code Flow\n\n"
            "## Design Decisions\n"
        ),
        "tests.md": (
            "# Tests\n\n"
            "## Test Strategy\n\n"
            "## Test Cases\n\n"
            "## Edge Cases\n\n"
            "## Results\n"
        ),
        "artifacts.md": (
            "# Artifacts\n\n"
            "## Docker Images\n\n"
            "| Image | Tag | Registry | Purpose |\n"
            "|-------|-----|----------|---------|\n"
            "| | | | |\n\n"
            "## GitHub Links\n\n"
            "- PR:\n"
            "- Issue:\n"
            "- Branch:\n\n"
            "## Config Examples\n\n"
            "## Other\n"
        ),
        "checkpoint.md": (
            f"# Checkpoint\n\n"
            f"## Current Phase\n"
            f"intent\n\n"
            f"## Last Updated\n"
            f"{today}\n\n"
            f"## Summary\n"
            f"New feature — no work done yet.\n\n"
            f"## Active Focus\n"
            f"Define intent: what are we building and why?\n\n"
            f"## Next Steps\n"
            f"- Fill out intent.md: goal, motivation, constraints, source repositories\n"
            f"- Identify open questions\n\n"
            f"## Relevant Docs\n"
            f"- intent.md\n"
        ),
    }

    for name, content in files.items():
        create_file(feature_dir / name, content)

    print(f"\n  Feature '{feature_name}' created in project '{project}'.\n")


# -------------------------
# BUGFIX STRUCTURE
# -------------------------

def create_bug(project, bug_name):
    bug_dir = Path("projects") / project / "technical/bugfix" / bug_name
    create_dir(bug_dir)

    today = date.today().isoformat()

    files = {
        "problem.md": (
            f"# Bug Problem\n\n"
            f"Bug: {bug_name}\n\n"
            f"## Description\n\n"
            f"## Expected Behavior\n\n"
            f"## Actual Behavior\n"
        ),
        "investigation.md": (
            "# Investigation\n\n"
            "## Logs\n\n"
            "## Reproduction Steps\n\n"
            "## Observations\n"
        ),
        "fix_plan.md": (
            "# Fix Plan\n\n"
            "## Root Cause\n\n"
            "## Proposed Fix\n"
        ),
        "fix_summary.md": (
            "# Fix Summary\n\n"
            "## Files Changed\n\n"
            "## Reasoning\n"
        ),
        "tests.md": (
            "# Tests\n\n"
            "## Test Strategy\n\n"
            "## Test Cases\n\n"
            "## Results\n"
        ),
        "checkpoint.md": (
            f"# Checkpoint\n\n"
            f"## Current Phase\n"
            f"problem\n\n"
            f"## Last Updated\n"
            f"{today}\n\n"
            f"## Summary\n"
            f"New bug — no investigation done yet.\n\n"
            f"## Active Focus\n"
            f"Define the problem: what is broken and what was expected?\n\n"
            f"## Next Steps\n"
            f"- Fill out problem.md: description, expected vs actual behavior\n"
            f"- Gather logs and reproduction steps\n\n"
            f"## Relevant Docs\n"
            f"- problem.md\n"
        ),
    }

    for name, content in files.items():
        create_file(bug_dir / name, content)

    print(f"\n  Bugfix '{bug_name}' created in project '{project}'.\n")


# -------------------------
# INTERACTIVE HELPERS
# -------------------------

def _list_subdirs(path):
    if not path.is_dir():
        return []
    return sorted(d.name for d in path.iterdir() if d.is_dir() and not d.name.startswith("."))


def _list_files(path, suffix=None):
    if not path.is_dir():
        return []
    if suffix:
        return sorted(f.name for f in path.iterdir() if f.is_file() and f.suffix == suffix)
    return sorted(f.name for f in path.iterdir() if f.is_file() and not f.name.startswith("."))


def _pick(options, label):
    """Single-choice picker. Auto-selects if only one option."""
    if not options:
        return None
    if len(options) == 1:
        print(f"  {label}: {options[0]}")
        return options[0]
    print(f"\n  {label}:")
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt}")
    while True:
        raw = input(f"  Select [1-{len(options)}]: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print("  Invalid choice.")


def _confirm(question):
    answer = input(f"  {question} [Y/n]: ").strip().lower()
    return answer != "n"


def _input_text(label):
    """Get non-empty text input."""
    while True:
        val = input(f"  {label}: ").strip()
        if val:
            return val
        print("  Cannot be empty.")


# -------------------------
# CONTEXT EXTRACTION
# -------------------------

def _extract_repos(intent_path):
    """Parse Source Repositories table from intent.md."""
    repos = []
    if not intent_path.is_file():
        return repos
    with open(intent_path) as f:
        lines = f.readlines()
    in_table = False
    for line in lines:
        if "Source Repositories" in line:
            in_table = True
            continue
        if in_table:
            s = line.strip()
            if s.startswith("|") and "---" not in s:
                cells = [c.strip().strip("`") for c in s.split("|") if c.strip()]
                if not cells or cells[0].lower() in ("repo", "name"):
                    continue
                if len(cells) >= 2 and cells[1]:
                    r = {"name": cells[0], "path": cells[1]}
                    if len(cells) >= 3 and cells[2] not in ("", "\u2014", "\u2013", "-"):
                        r["branch"] = cells[2]
                    repos.append(r)
            elif s and not s.startswith("|"):
                break
    return repos


def _extract_task_summary(tasks_path):
    """Count task status markers in tasks.md (supports [x] and [ ] in any context)."""
    if not tasks_path.is_file():
        return None
    text = tasks_path.read_text()
    done = text.count("[x]") + text.count("[X]")
    todo = text.count("[ ]")
    total = done + todo
    return {"done": done, "total": total} if total else None


# -------------------------
# PROMPT BUILDERS
# -------------------------

def _build_context_block(role, project, work_type, item, item_path,
                         repos, doc_files, task_summary,
                         playbook_files, knowledge_files):
    """Session context block shared by both slim and full prompts."""
    bp = str(item_path)
    ctx = []
    ctx.append(f"Role: {role}")
    ctx.append(f"Project: {project}")
    ctx.append(f"Type: {work_type.capitalize()}")
    ctx.append(f"Name: {item}")
    ctx.append(f"Brain Path: {bp}/")

    if repos:
        ctx.append("\nSource Repositories:")
        for r in repos:
            line = f"  {r['name']}: {r['path']}"
            if "branch" in r:
                line += f" (branch: {r['branch']})"
            ctx.append(line)

    if task_summary:
        ctx.append(f"\nTask Progress: {task_summary['done']}/{task_summary['total']} complete")

    ctx.append("\nBrain Documents:")
    for name in doc_files:
        ctx.append(f"  {bp}/{name}")

    project_tech = Path("projects") / project / "technical"
    if playbook_files:
        ctx.append(f"\nPlaybooks: {project_tech / 'playbooks'}/")
        for name in playbook_files:
            ctx.append(f"  {name}")
    if knowledge_files:
        ctx.append(f"\nKnowledge: {project_tech / 'knowledge'}/")
        for name in knowledge_files:
            ctx.append(f"  {name}")

    return "\n".join(ctx)


def _build_slim_prompt(role, project, work_type, item, item_path,
                       repos, doc_files, task_summary,
                       playbook_files, knowledge_files):
    """Compact prompt — session context only. Behavioral rules live in Cursor rules."""
    lines = ["SESSION CONTEXT\n"]
    lines.append(_build_context_block(
        role, project, work_type, item, item_path,
        repos, doc_files, task_summary,
        playbook_files, knowledge_files,
    ))
    lines.append("")
    lines.append("Read checkpoint.md first. Summarize state. Ask what to work on.")
    return "\n".join(lines)


def _build_full_prompt(role, project, work_type, item, item_path,
                       repos, doc_files, task_summary,
                       playbook_files, knowledge_files):
    """Comprehensive prompt with all rules embedded — for non-Cursor tools."""
    prompt_path = Path("prompts") / "start.prompt"
    raw = prompt_path.read_text() if prompt_path.is_file() else ""

    divider = "--" * 25
    skip_markers = {"YOUR FIRST RESPONSIBILITY", "FINAL INSTRUCTION"}

    sections = []
    if raw:
        for chunk in raw.split(divider):
            text = chunk.strip()
            if not text:
                continue
            if any(m in text for m in skip_markers):
                continue
            sections.append(text)

    ctx_block = _build_context_block(
        role, project, work_type, item, item_path,
        repos, doc_files, task_summary,
        playbook_files, knowledge_files,
    )
    sections.append("SESSION CONTEXT (pre-loaded \u2014 do not ask setup questions)\n\n" + ctx_block)

    has_checkpoint = (item_path / "checkpoint.md").is_file()
    if has_checkpoint:
        start_inst = (
            "START INSTRUCTIONS\n\n"
            "1. Read checkpoint.md in the Brain path for current session state and phase.\n"
            "2. Based on the current phase and active focus, read relevant Brain documents as needed.\n"
            "3. Summarize where we are and ask what I want to work on.\n\n"
            "CHECKPOINT RULE (mandatory):\n"
            "After EVERY response where meaningful work was done, update checkpoint.md with:\n"
            "current phase, today's date, summary, active focus, next steps, relevant docs.\n"
            "Do NOT defer this. Chat sessions degrade — the last checkpoint must always be current.\n\n"
            "Do not ask setup questions \u2014 all context is provided above."
        )
    else:
        start_inst = (
            "START INSTRUCTIONS\n\n"
            "1. Read ALL Brain documents listed above to establish context.\n"
            "2. Summarize current state: what is done, what is in progress, what is next.\n"
            "3. Create checkpoint.md in the Brain path with:\n"
            "   current phase, today's date, summary, active focus, next steps, relevant docs.\n"
            "4. Ask what I want to work on today.\n\n"
            "CHECKPOINT RULE (mandatory):\n"
            "After EVERY response where meaningful work was done, update checkpoint.md with:\n"
            "current phase, today's date, summary, active focus, next steps, relevant docs.\n"
            "Do NOT defer this. Chat sessions degrade — the last checkpoint must always be current.\n\n"
            "Do not ask setup questions \u2014 all context is provided above."
        )

    sections.append(start_inst)

    return ("\n\n" + divider + "\n\n").join(sections)


def _generate_and_output(project, work_type, item, item_path, role, full=False):
    """Discover context, build prompt, print and copy to clipboard."""
    repos = _extract_repos(item_path / "intent.md")
    doc_files = _list_files(item_path, suffix=".md")
    task_summary = _extract_task_summary(item_path / "tasks.md")
    project_tech = Path("projects") / project / "technical"
    playbook_files = _list_files(project_tech / "playbooks", suffix=".md")
    knowledge_files = _list_files(project_tech / "knowledge")

    builder = _build_full_prompt if full else _build_slim_prompt
    prompt = builder(
        role, project, work_type, item, item_path,
        repos, doc_files, task_summary,
        playbook_files, knowledge_files,
    )

    sep = "=" * 60
    mode = "FULL (all rules embedded)" if full else "SLIM (Cursor rules active)"
    print(f"\n{sep}")
    print(f"  Prompt mode: {mode}")
    print(f"  Paste the following into your AI agent:")
    print(sep)
    print()
    print(prompt)

    try:
        import subprocess
        subprocess.run(["pbcopy"], input=prompt.encode(), check=True, capture_output=True)
        print(f"\n{sep}")
        print("  Copied to clipboard.")
        print(sep)
    except Exception:
        pass


# -------------------------
# SESSION FLOWS
# -------------------------

def _flow_new():
    """Create new project/feature/bug. Returns (project, work_type, item, item_path)."""
    existing = _list_subdirs(Path("projects"))

    if existing:
        choices = existing + ["+ Create new project"]
        selected = _pick(choices, "Project")
        if selected == "+ Create new project":
            project = _input_text("New project name")
            create_project(project)
        else:
            project = selected
    else:
        project = _input_text("New project name")
        create_project(project)

    work_type = _pick(["feature", "bugfix"], "Work type")
    name = _input_text(f"{work_type.capitalize()} name")

    if work_type == "feature":
        create_feature(project, name)
        item_path = Path("projects") / project / "technical/features" / name
    else:
        create_bug(project, name)
        item_path = Path("projects") / project / "technical/bugfix" / name

    return project, work_type, name, item_path


def _flow_continue():
    """Select existing feature/bug. Returns (project, work_type, item, item_path)."""
    projects = _list_subdirs(Path("projects"))
    if not projects:
        print("  No projects found. Start something new instead.")
        sys.exit(1)
    project = _pick(projects, "Project")

    work_type = _pick(["feature", "bugfix"], "Work type")

    type_dir = "features" if work_type == "feature" else "bugfix"
    items_path = Path("projects") / project / "technical" / type_dir
    items = _list_subdirs(items_path)
    if not items:
        print(f"\n  No {work_type}s in {project}. Start something new instead.")
        sys.exit(1)
    item = _pick(items, work_type.capitalize())

    return project, work_type, item, items_path / item


# -------------------------
# SESSION START (UNIFIED)
# -------------------------

def start_session(full=False):
    """Unified interactive session setup — continue or create, then generate prompt."""
    if not Path("projects").is_dir() and not Path("prompts").is_dir():
        print("Cannot find projects/ or prompts/ directory.")
        print("Run brain.py from the brain root (same level as projects/ and prompts/).")
        sys.exit(1)

    _ensure_cursor_rules()

    print("Developer Brain \u2014 Session Setup\n")

    action = _pick(["Continue existing work", "Start something new"], "Action")

    if action == "Start something new":
        project, work_type, item, item_path = _flow_new()
    else:
        project, work_type, item, item_path = _flow_continue()

    role = _pick(["Developer", "QE"], "Role")

    _generate_and_output(project, work_type, item, item_path, role, full=full)


# -------------------------
# MAIN
# -------------------------

def main():
    if len(sys.argv) < 2:
        print("""
Developer Brain — structured knowledge system for engineering work.

Usage (run from brain root directory):

  python3 brain.py start                        Interactive session setup
  python3 brain.py start --full                  Full prompt (for non-Cursor tools)
  python3 brain.py project <name>               Create a new project
  python3 brain.py feature <project> <name>     Create a feature
  python3 brain.py bug <project> <name>         Create a bugfix
""")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start":
        full = "--full" in sys.argv
        start_session(full=full)

    elif command == "project":
        if len(sys.argv) != 3:
            print("Usage: python3 brain.py project <project_name>")
            sys.exit(1)
        create_project(sys.argv[2])

    elif command == "feature":
        if len(sys.argv) != 4:
            print("Usage: python3 brain.py feature <project> <feature_name>")
            sys.exit(1)
        create_feature(sys.argv[2], sys.argv[3])

    elif command == "bug":
        if len(sys.argv) != 4:
            print("Usage: python3 brain.py bug <project> <bug_name>")
            sys.exit(1)
        create_bug(sys.argv[2], sys.argv[3])

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
