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
    python3 brain.py task <name>                     Create a brain-level task
    python3 brain.py task <project> <name>           Create a project-level task
    python3 brain.py research <name>                 Create a brain-level research
    python3 brain.py research <project> <name>       Create a project-level research
    python3 brain.py review <name>                   Create a brain-level PR review
    python3 brain.py review <project> <name>         Create a project-level PR review
    python3 brain.py check                           Audit brain docs for credentials and staleness
    python3 brain.py migrate-obsidian                  Add YAML frontmatter to existing docs for Obsidian
"""

import sys
from pathlib import Path
from datetime import date, datetime


# -------------------------
# FILESYSTEM HELPERS
# -------------------------

def _now_hhmm():
    """Current time as HH:MM."""
    return datetime.now().strftime("%H:%M")


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
description: Developer Brain — structured engineering knowledge system.
alwaysApply: true
---

# Developer Brain

You are working inside a **Developer Brain** — a knowledge system where brain docs are the
source of truth. Write findings, decisions, and progress into brain docs, not into long chat messages.

## Structure

```
projects/<project>/technical/
  features/<feature>/    intent → exploration → architecture → tasks → implementation → tests → artifacts
  bugfix/<bug>/          problem → investigation → fix_plan → fix_summary → tests
  tasks/<task>/          task.md (goal, notes, outcome)
  research/<research>/   research.md (question, approach, findings, conclusion)
  reviews/<review>/      review.md (intent, impact, assumptions, edge cases, verdict)
  playbooks/             Repeatable workflows
  system/                Architecture docs
  knowledge/             Reference material

tasks/ research/ reviews/   Brain-level standalone (not project-specific)
shared/playbooks/           Cross-project workflows
shared/knowledge/           Cross-project reference material
shared/persona.md           Your preferences and shortcuts — read this first
```

Every work item has a `checkpoint.md` — read it first to know where things stand.

## How to Work

1. Read `checkpoint.md` first — it tells you the current phase and what to focus on.
2. Read `shared/persona.md` — respect the user's shortcuts and preferences.
3. Do the work. Update the relevant brain doc as you go.
4. Use `[[links]]` when referencing other brain docs: `Based on [[exploration]]...`
5. Add code references to YAML frontmatter: `code_refs: [FeatureStore.apply]`
6. Add cross-feature connections to frontmatter: `related: ["[[OIDC exploration]]"]`
7. Update `checkpoint.md` at the end — this is your memory for the next response.
8. Request approval before modifying code or making architecture decisions.

## Reviews

The reviewer's job is to understand WHY changes were made, assess IMPACT, and find what's
MISSING. Think from the perspective of the system under load, bad input, partial failure.
The Verdict section is only set by the user — present your findings and ask for their verdict.

## Principles

- Understand before acting. Explain what you know, infer, and are unsure about.
- Test before theorize. Simplest path first.
- Suggest promoting reusable knowledge to `shared/` — but don't move without approval.
- If a playbook exists for a workflow, follow it. If one should exist, suggest creating it.
"""

_RULE_CHECKPOINT = """\
---
description: Checkpoint — your memory between responses and sessions.
alwaysApply: true
---

# Checkpoint

checkpoint.md is YOUR memory. Without it, your next response — or the next chat session —
starts from zero. You lose what you explored, what you decided, what you planned to do next.
Updating it isn't a chore — it's how you stay effective.

## On first response

Read checkpoint.md before anything else. It tells you where things stand, what to focus on,
and which docs to read. Don't load everything — load what the checkpoint points you to.

## After doing work

When you've done meaningful work in a response, update checkpoint.md with:

- **phase** (in YAML frontmatter + body) — where the work is now
- **prompt_count** — increment by 1 (frontmatter + body)
- **last_updated** — current date and time
- **summary** — what you actually accomplished (be specific)
- **active focus** — what the next response should pick up
- **next steps** — concrete actions remaining
- **relevant docs** — which brain docs matter now (use [[links]])
- **dependencies** — cross-feature connections if discovered
- **session log** — append a row: `| # | date | time | summary |`

If the work was trivial (a clarifying question, a short answer), use your judgment —
not every response needs a checkpoint update. But if you explored, decided, implemented,
or produced something — capture it. You'll thank yourself next response.

## When switching tasks

If the user shifts focus mid-conversation, update the current checkpoint before moving on.
Otherwise you lose the state of the work you were just doing.

## Brain doc updates

Update brain docs as you work, not after. When you explore → write to exploration.md.
When you decide → write to architecture.md. When you implement → write to implementation.md.
Don't defer — the doc update IS the work product.
"""

_RULE_BRAIN_EVOLUTION = """\
---
description: Brain self-evolution — the brain learns from usage.
alwaysApply: true
---

# Brain Evolution

Read `shared/persona.md` on your first response. It has the user's shortcuts, question
patterns, and preferences. Respect them.

If you notice a pattern during conversation — repeated shorthand, a recurring question
style, a workflow done more than once, a preference being expressed — suggest adding it
to persona.md. Keep it brief: what to add, where, why. Don't modify without approval.

If you notice brain structure friction — a template that doesn't fit, a doc type that's
missing, a process that could be smoother — suggest an improvement.
"""

_RULE_BRAIN_SECURITY = """\
---
description: Security — never persist credentials in files.
alwaysApply: true
---

# Security

Never write passwords, tokens, API keys, or private keys to any file. Use environment
variable references instead: `$API_KEY`, `os.environ["TOKEN"]`.

If a credential appears in chat, you can use it for the current operation, but warn the
user to rotate it after the session. Log actions in brain docs, not credential values.
Good: "Tested OIDC endpoint — 200 OK". Bad: "Tested with token eyJhbGciOi..."

If you spot credentials in existing brain docs, warn and suggest replacing with env var refs.
"""

_CURSOR_RULES = {
    "developer-brain.mdc": _RULE_DEVELOPER_BRAIN,
    "checkpoint.mdc": _RULE_CHECKPOINT,
    "brain-evolution.mdc": _RULE_BRAIN_EVOLUTION,
    "brain-security.mdc": _RULE_BRAIN_SECURITY,
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


_PERSONA_TEMPLATE = """\
# Persona

## Shortcuts

Shorthand the user uses. Interpret these as described.

| Short | Meaning |
|-------|---------|
| WDYT | What do you think? Give honest assessment including risks and alternatives. |
| LGTM | Approved. Proceed with implementation. |
| IDTS | I don't think so. Reconsider or explain why. |

## Question Patterns

How the user likes to understand things. Apply these during exploration.

## Preferences

Working style, communication preferences, technical depth expectations.

## Learned Patterns

Behaviors observed over time. Added by agent suggestion, approved by user.
"""


def _ensure_shared():
    """Create shared/ directory structure and persona.md if missing."""
    shared = Path("shared")
    created_any = False

    for subdir in ["playbooks", "knowledge"]:
        p = shared / subdir
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
            if not created_any:
                print()
            print(f"  Created: {p}/")
            created_any = True

    persona = shared / "persona.md"
    if not persona.exists():
        persona.write_text(_PERSONA_TEMPLATE)
        if not created_any:
            print()
        print(f"  Created: {persona}")
        created_any = True

    if created_any:
        print("  Shared directory ready — cross-project playbooks, knowledge, and persona.\n")


# -------------------------
# PROJECT STRUCTURE
# -------------------------

def create_project(project_name):
    project_root = Path("projects") / project_name

    dirs = [
        "technical/features",
        "technical/bugfix",
        "technical/tasks",
        "technical/research",
        "technical/reviews",
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

    _fm = lambda dtype, code=False: _doc_frontmatter(dtype, project, feature_name, has_code_refs=code)
    files = {
        "intent.md": (
            _fm("intent") +
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
            _fm("exploration", code=True) +
            "# Code Exploration\n\n"
            "## Relevant Modules\n\n"
            "## Current Flow\n\n"
            "## Observations\n"
        ),
        "architecture.md": (
            _fm("architecture", code=True) +
            "# Architecture Decision\n\n"
            "## Options Considered\n\n"
            "## Selected Approach\n\n"
            "## Tradeoffs\n"
        ),
        "tasks.md": (
            _fm("tasks") +
            "# Task Breakdown\n\n"
            "## Overview\n\n"
            "## Tasks\n\n"
            "1.\n2.\n3.\n\n"
            "## Scope Decisions\n\n"
            "## Implementation Order\n"
        ),
        "implementation.md": (
            _fm("implementation", code=True) +
            "# Implementation Summary\n\n"
            "## Files Changed\n\n"
            "## Code Flow\n\n"
            "## Design Decisions\n"
        ),
        "tests.md": (
            _fm("tests", code=True) +
            "# Tests\n\n"
            "## Test Strategy\n\n"
            "## Test Cases\n\n"
            "## Edge Cases\n\n"
            "## Results\n"
        ),
        "artifacts.md": (
            _fm("artifacts") +
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
        "checkpoint.md": _checkpoint_template(
            feature_name, "feature",
            "Fill out [[intent]]: goal, motivation, constraints, source repositories",
            project=project,
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

    _fm = lambda dtype, code=False: _doc_frontmatter(dtype, project, bug_name, has_code_refs=code)
    files = {
        "problem.md": (
            _fm("problem") +
            f"# Bug Problem\n\n"
            f"Bug: {bug_name}\n\n"
            f"## Description\n\n"
            f"## Expected Behavior\n\n"
            f"## Actual Behavior\n"
        ),
        "investigation.md": (
            _fm("investigation", code=True) +
            "# Investigation\n\n"
            "## Logs\n\n"
            "## Reproduction Steps\n\n"
            "## Observations\n"
        ),
        "fix_plan.md": (
            _fm("fix_plan", code=True) +
            "# Fix Plan\n\n"
            "## Root Cause\n\n"
            "## Proposed Fix\n"
        ),
        "fix_summary.md": (
            _fm("fix_summary", code=True) +
            "# Fix Summary\n\n"
            "## Files Changed\n\n"
            "## Reasoning\n"
        ),
        "tests.md": (
            _fm("tests", code=True) +
            "# Tests\n\n"
            "## Test Strategy\n\n"
            "## Test Cases\n\n"
            "## Results\n"
        ),
        "checkpoint.md": _checkpoint_template(
            bug_name, "bugfix",
            "Fill out [[problem]]: description, expected vs actual behavior",
            project=project,
        ),
    }

    for name, content in files.items():
        create_file(bug_dir / name, content)

    print(f"\n  Bugfix '{bug_name}' created in project '{project}'.\n")


# -------------------------
# TASK STRUCTURE
# -------------------------

def _doc_frontmatter(doc_type, project=None, feature=None, has_code_refs=False):
    """Generate YAML frontmatter for a brain doc."""
    lines = ["---", f"type: {doc_type}"]
    if project:
        lines.append(f"project: {project}")
    if feature:
        lines.append(f"feature: {feature}")
    if has_code_refs:
        lines.append("code_refs: []")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def _checkpoint_template(name, work_label, first_step, project=None):
    """Build a checkpoint.md string for any work type."""
    today = date.today().isoformat()
    now = _now_hhmm()
    fm_lines = [
        "---",
        f"type: {work_label}",
        f"name: {name}",
    ]
    if project:
        fm_lines.append(f"project: {project}")
    fm_lines.extend([
        "phase: intent",
        "prompt_count: 0",
        f"created: {today}",
        f"last_updated: {today} {now}",
        "code_refs: []",
        "related: []",
        "tags: []",
        "---",
    ])
    frontmatter = "\n".join(fm_lines)
    return (
        f"{frontmatter}\n\n"
        f"# Checkpoint\n\n"
        f"## Current Phase\n"
        f"intent\n\n"
        f"## Last Updated\n"
        f"{today} {now}\n\n"
        f"## Prompt Count\n"
        f"0\n\n"
        f"## Summary\n"
        f"New {work_label} — no work done yet.\n\n"
        f"## Active Focus\n"
        f"{first_step}\n\n"
        f"## Next Steps\n"
        f"1. {first_step}\n\n"
        f"## Relevant Docs\n"
        f"- (none yet)\n\n"
        f"## Dependencies\n"
        f"- (none yet)\n\n"
        f"## Session Log\n"
        f"| # | Date | Time | Summary |\n"
        f"|---|------|------|---------|\n"
    )


def create_task(name, project=None):
    """Create a task — brain-level (tasks/<name>/) or project-level."""
    if project:
        task_dir = Path("projects") / project / "technical/tasks" / name
    else:
        task_dir = Path("tasks") / name
    create_dir(task_dir)

    files = {
        "task.md": (
            _doc_frontmatter("task", project, name, has_code_refs=True) +
            f"# Task: {name}\n\n"
            f"## Goal\n\n"
            f"## Notes\n\n"
            f"## Outcome\n"
        ),
        "checkpoint.md": _checkpoint_template(name, "task", "Define the goal: what needs to be done and why?", project=project),
    }

    for fname, content in files.items():
        create_file(task_dir / fname, content)

    location = f"project '{project}'" if project else "brain-level"
    print(f"\n  Task '{name}' created ({location}).\n")


def create_research(name, project=None):
    """Create a research — brain-level (research/<name>/) or project-level."""
    if project:
        research_dir = Path("projects") / project / "technical/research" / name
    else:
        research_dir = Path("research") / name
    create_dir(research_dir)

    files = {
        "research.md": (
            _doc_frontmatter("research", project, name, has_code_refs=True) +
            f"# Research: {name}\n\n"
            f"## Question / Hypothesis\n\n"
            f"## Approach\n\n"
            f"## Findings\n\n"
            f"## Conclusion\n\n"
            f"## Reusable Knowledge\n"
        ),
        "checkpoint.md": _checkpoint_template(name, "research", "Define the question: what are we trying to find out?", project=project),
    }

    for fname, content in files.items():
        create_file(research_dir / fname, content)

    location = f"project '{project}'" if project else "brain-level"
    print(f"\n  Research '{name}' created ({location}).\n")


def create_review(name, project=None):
    """Create a PR review — brain-level (reviews/<name>/) or project-level."""
    if project:
        review_dir = Path("projects") / project / "technical/reviews" / name
    else:
        review_dir = Path("reviews") / name
    create_dir(review_dir)

    files = {
        "review.md": (
            _doc_frontmatter("review", project, name, has_code_refs=True) +
            f"# PR Review: {name}\n\n"
            f"## PR Link\n\n"
            f"## Intent\n"
            f"Why does this PR exist? What problem does it solve? What motivated it?\n"
            f"(If unclear from the PR description, that's the first finding.)\n\n"
            f"## Changes Summary\n"
            f"Files changed, what each change does at a high level.\n\n"
            f"## Architecture Impact\n"
            f"- What existing code paths are affected by this change?\n"
            f"- What depends on the code that was modified?\n"
            f"- Does this change any contracts (API signatures, data formats, behavior)?\n\n"
            f"## Assumptions vs Reality\n"
            f"| What the author assumed | What can also happen in the real world |\n"
            f"|------------------------|---------------------------------------|\n"
            f"| | |\n\n"
            f"## Edge Cases & Failure Modes\n"
            f"- What inputs are not handled?\n"
            f"- What happens under partial failure (network, timeout, OOM)?\n"
            f"- What happens under concurrent access?\n"
            f"- What happens with empty/null/malformed data?\n\n"
            f"## Missing\n"
            f"- Tests not written\n"
            f"- Error handling not present\n"
            f"- Documentation not updated\n"
            f"- Logging/observability gaps\n\n"
            f"## Verdict\n"
            f"**Pending** — verdict is set ONLY by the user after reviewing all findings above.\n"
            f"Agent must present all findings and explicitly ask for verdict before this is updated.\n\n"
            f"[ ] Approve  [ ] Request changes  [ ] Needs discussion\n\n"
            f"## Comments for Author\n"
        ),
        "checkpoint.md": _checkpoint_template(name, "review", "Read the PR, understand the intent, and document what was changed and why", project=project),
    }

    for fname, content in files.items():
        create_file(review_dir / fname, content)

    location = f"project '{project}'" if project else "brain-level"
    print(f"\n  Review '{name}' created ({location}).\n")


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
# SECRET SCANNING
# -------------------------

import re

_SECRET_PATTERNS = [
    ("AWS Access Key", r"AKIA[0-9A-Z]{16}"),
    ("AWS Secret Key", r"(?i)aws_secret_access_key\s*[=:]\s*\S+"),
    ("GitHub Token", r"gh[pousr]_[A-Za-z0-9_]{36,}"),
    ("GitLab Token", r"glpat-[A-Za-z0-9\-]{20,}"),
    ("Google API Key", r"AIza[0-9A-Za-z\-_]{35}"),
    ("Google OAuth Secret", r"GOCSPX-[A-Za-z0-9\-_]{28,}"),
    ("Slack Token", r"xox[bporas]-[A-Za-z0-9\-]+"),
    ("Private Key Header", r"-----BEGIN\s+(RSA|EC|DSA|OPENSSH|PGP)\s+PRIVATE\s+KEY-----"),
    ("Generic Token Assignment", r"(?i)(token|secret|password|api_key|apikey)\s*[=:]\s*['\"][A-Za-z0-9+/=\-_]{20,}['\"]"),
    ("URL Credentials", r"://[^/\s:]+:[^/\s@]+@"),
    ("OpenAI API Key", r"sk-[A-Za-z0-9]{20,}"),
    ("Hugging Face Token", r"hf_[A-Za-z0-9]{20,}"),
    ("Red Hat Registry Token", r"(?i)registry\.redhat\.io.*token\s*[=:]\s*\S+"),
    ("Bearer Token Header", r"(?i)authorization:\s*bearer\s+[A-Za-z0-9\-._~+/]+=*"),
    ("Base64 Encoded Secret", r"(?i)(password|secret|token)\s*[=:]\s*[A-Za-z0-9+/]{40,}={0,2}"),
]

_COMPILED_SECRETS = [(name, re.compile(pattern)) for name, pattern in _SECRET_PATTERNS]


def _scan_for_secrets(text):
    """Scan text for credential patterns. Returns list of (pattern_name, line_num, matched_text)."""
    findings = []
    for i, line in enumerate(text.splitlines(), 1):
        for name, regex in _COMPILED_SECRETS:
            match = regex.search(line)
            if match:
                snippet = match.group(0)
                if len(snippet) > 60:
                    snippet = snippet[:57] + "..."
                findings.append((name, i, snippet))
    return findings


def _scan_file(filepath):
    """Scan a single file for secrets."""
    try:
        text = filepath.read_text()
    except Exception:
        return []
    return [(filepath, name, line, snippet) for name, line, snippet in _scan_for_secrets(text)]


def run_check():
    """Audit all brain docs for credential patterns."""
    print("Developer Brain — Security Audit\n")

    all_findings = []
    scan_dirs = [Path("projects"), Path("tasks"), Path("research"), Path("reviews"), Path("shared")]

    for scan_dir in scan_dirs:
        if not scan_dir.is_dir():
            continue
        for md_file in scan_dir.rglob("*.md"):
            all_findings.extend(_scan_file(md_file))

    if not all_findings:
        print("  No credential patterns found. All clear.\n")
        sys.exit(0)

    print(f"  Found {len(all_findings)} potential credential(s):\n")
    for filepath, name, line, snippet in all_findings:
        print(f"    {filepath}:{line}  [{name}]  {snippet}")
    print()
    sys.exit(1)


# -------------------------
# OBSIDIAN MIGRATION
# -------------------------

_DOC_TYPE_MAP = {
    "checkpoint": "checkpoint",
    "intent": "intent",
    "exploration": "exploration",
    "architecture": "architecture",
    "tasks": "tasks",
    "implementation": "implementation",
    "tests": "tests",
    "artifacts": "artifacts",
    "problem": "problem",
    "investigation": "investigation",
    "fix_plan": "fix_plan",
    "fix_summary": "fix_summary",
    "task": "task",
    "research": "research",
    "review": "review",
}

_CODE_REF_TYPES = {
    "exploration", "architecture", "implementation", "tests",
    "investigation", "fix_plan", "fix_summary",
    "task", "research", "review",
}


def _infer_metadata(filepath):
    """Infer type, project, feature from a brain doc's file path."""
    parts = filepath.parts
    stem = filepath.stem

    doc_type = _DOC_TYPE_MAP.get(stem)
    if not doc_type:
        return None

    project = None
    feature = None

    if "projects" in parts:
        idx = list(parts).index("projects")
        if idx + 1 < len(parts):
            project = parts[idx + 1]
        for subdir in ("features", "bugfix", "tasks", "research", "reviews"):
            if subdir in parts:
                sidx = list(parts).index(subdir)
                if sidx + 1 < len(parts):
                    feature = parts[sidx + 1]
                    break

    return {"type": doc_type, "project": project, "feature": feature}


def _parse_checkpoint_fields(text):
    """Extract phase and prompt_count from existing checkpoint body text."""
    phase = "intent"
    prompt_count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if stripped in ("intent", "exploration", "architecture", "implementation", "testing", "complete",
                        "problem", "investigation", "fix_plan", "documentation"):
            phase = stripped
        if stripped.isdigit() and int(stripped) < 1000:
            prev_lines = text[:text.index(line)].splitlines()
            if prev_lines and "Prompt Count" in prev_lines[-1]:
                prompt_count = int(stripped)
    return phase, prompt_count


def migrate_obsidian():
    """Add YAML frontmatter to existing brain docs for Obsidian compatibility."""
    print("Developer Brain — Obsidian Migration\n")
    count = 0
    skipped = 0

    scan_dirs = [Path("projects"), Path("tasks"), Path("research"),
                 Path("reviews"), Path("shared")]

    for scan_dir in scan_dirs:
        if not scan_dir.is_dir():
            continue
        for md_file in sorted(scan_dir.rglob("*.md")):
            text = md_file.read_text(encoding="utf-8", errors="replace")

            if text.startswith("---"):
                skipped += 1
                continue

            meta = _infer_metadata(md_file)
            if not meta:
                skipped += 1
                continue

            fm_lines = ["---", f"type: {meta['type']}"]
            if meta["project"]:
                fm_lines.append(f"project: {meta['project']}")
            if meta["feature"]:
                fm_lines.append(f"feature: {meta['feature']}")

            if meta["type"] == "checkpoint":
                phase, prompt_count = _parse_checkpoint_fields(text)
                fm_lines.append(f"phase: {phase}")
                fm_lines.append(f"prompt_count: {prompt_count}")
                fm_lines.append(f"last_updated: {date.today().isoformat()}")
                fm_lines.append("code_refs: []")
                fm_lines.append("related: []")
                fm_lines.append("tags: []")
            elif meta["type"] in _CODE_REF_TYPES:
                fm_lines.append("code_refs: []")

            fm_lines.append("---")
            frontmatter = "\n".join(fm_lines) + "\n\n"

            md_file.write_text(frontmatter + text, encoding="utf-8")
            count += 1
            print(f"  Migrated: {md_file}")

    gitignore = Path(".gitignore")
    if gitignore.is_file():
        content = gitignore.read_text()
        if ".obsidian/" not in content:
            gitignore.write_text(content.rstrip() + "\n\n# Obsidian\n.obsidian/\n")
            print("\n  Added .obsidian/ to .gitignore")

    print(f"\n  Migrated: {count} files")
    print(f"  Skipped (already has frontmatter or unrecognized): {skipped} files")
    print(f"\n  Open this directory in Obsidian to see the graph.\n")


# -------------------------
# PROMPT BUILDERS
# -------------------------

def _build_context_block(role, project, work_type, item, item_path,
                         repos, doc_files, task_summary,
                         playbook_files, knowledge_files,
                         shared_playbooks=None, shared_knowledge=None):
    """Session context block shared by both slim and full prompts."""
    bp = str(item_path)
    ctx = []
    ctx.append(f"Role: {role}")
    if project:
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

    if project:
        project_tech = Path("projects") / project / "technical"
        if playbook_files:
            ctx.append(f"\nProject Playbooks: {project_tech / 'playbooks'}/")
            for name in playbook_files:
                ctx.append(f"  {name}")
        if knowledge_files:
            ctx.append(f"\nProject Knowledge: {project_tech / 'knowledge'}/")
            for name in knowledge_files:
                ctx.append(f"  {name}")

    if shared_playbooks:
        ctx.append("\nShared Playbooks: shared/playbooks/")
        for name in shared_playbooks:
            ctx.append(f"  {name}")
    if shared_knowledge:
        ctx.append("\nShared Knowledge: shared/knowledge/")
        for name in shared_knowledge:
            ctx.append(f"  {name}")

    persona = Path("shared/persona.md")
    if persona.is_file():
        ctx.append("\nPersona: shared/persona.md")

    return "\n".join(ctx)


def _build_slim_prompt(role, project, work_type, item, item_path,
                       repos, doc_files, task_summary,
                       playbook_files, knowledge_files,
                       shared_playbooks=None, shared_knowledge=None):
    """Compact prompt — session context only. Behavioral rules live in Cursor rules."""
    lines = ["SESSION CONTEXT\n"]
    lines.append(_build_context_block(
        role, project, work_type, item, item_path,
        repos, doc_files, task_summary,
        playbook_files, knowledge_files,
        shared_playbooks, shared_knowledge,
    ))
    lines.append("")
    lines.append("Read checkpoint.md first. Summarize state. Ask what to work on.")
    return "\n".join(lines)


def _build_full_prompt(role, project, work_type, item, item_path,
                       repos, doc_files, task_summary,
                       playbook_files, knowledge_files,
                       shared_playbooks=None, shared_knowledge=None):
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
        shared_playbooks, shared_knowledge,
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

    playbook_files = []
    knowledge_files = []
    if project:
        project_tech = Path("projects") / project / "technical"
        playbook_files = _list_files(project_tech / "playbooks", suffix=".md")
        knowledge_files = _list_files(project_tech / "knowledge")

    shared_playbooks = _list_files(Path("shared/playbooks"), suffix=".md")
    shared_knowledge = _list_files(Path("shared/knowledge"))

    builder = _build_full_prompt if full else _build_slim_prompt
    prompt = builder(
        role, project, work_type, item, item_path,
        repos, doc_files, task_summary,
        playbook_files, knowledge_files,
        shared_playbooks, shared_knowledge,
    )

    findings = _scan_for_secrets(prompt)
    if findings:
        print("\n  WARNING: Potential credentials detected in generated prompt:\n")
        for name, line, snippet in findings:
            print(f"    Line {line}: [{name}] {snippet}")
        print()
        answer = input("  Send anyway? [y/N]: ").strip().lower()
        if answer != "y":
            print("  Aborted. Clean up credentials before generating prompt.")
            return

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
    """Create new work item. Returns (project, work_type, item, item_path)."""
    scope = _pick(["Project work (feature / bugfix)", "Standalone (task / research)"], "Scope")

    if scope.startswith("Standalone"):
        work_type = _pick(["task", "research", "review"], "Work type")
        name = _input_text(f"{work_type.capitalize()} name")
        if work_type == "task":
            create_task(name)
            return None, "task", name, Path("tasks") / name
        elif work_type == "review":
            create_review(name)
            return None, "review", name, Path("reviews") / name
        else:
            create_research(name)
            return None, "research", name, Path("research") / name

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

    work_type = _pick(["feature", "bugfix", "task", "research", "review"], "Work type")
    name = _input_text(f"{work_type.capitalize()} name")

    if work_type == "feature":
        create_feature(project, name)
        item_path = Path("projects") / project / "technical/features" / name
    elif work_type == "bugfix":
        create_bug(project, name)
        item_path = Path("projects") / project / "technical/bugfix" / name
    elif work_type == "task":
        create_task(name, project=project)
        item_path = Path("projects") / project / "technical/tasks" / name
    elif work_type == "review":
        create_review(name, project=project)
        item_path = Path("projects") / project / "technical/reviews" / name
    else:
        create_research(name, project=project)
        item_path = Path("projects") / project / "technical/research" / name

    return project, work_type, name, item_path


def _flow_continue():
    """Select existing work item. Returns (project, work_type, item, item_path)."""
    brain_tasks = _list_subdirs(Path("tasks"))
    brain_research = _list_subdirs(Path("research"))
    brain_reviews = _list_subdirs(Path("reviews"))
    projects = _list_subdirs(Path("projects"))

    scope_options = []
    if projects:
        scope_options.append("Project work")
    if brain_tasks:
        scope_options.append("Standalone task")
    if brain_research:
        scope_options.append("Standalone research")
    if brain_reviews:
        scope_options.append("Standalone review")

    if not scope_options:
        print("  No existing work found. Start something new instead.")
        sys.exit(1)

    scope = _pick(scope_options, "Scope")

    if scope == "Standalone task":
        item = _pick(brain_tasks, "Task")
        return None, "task", item, Path("tasks") / item
    if scope == "Standalone research":
        item = _pick(brain_research, "Research")
        return None, "research", item, Path("research") / item
    if scope == "Standalone review":
        item = _pick(brain_reviews, "Review")
        return None, "review", item, Path("reviews") / item

    project = _pick(projects, "Project")

    type_map = {"feature": "features", "bugfix": "bugfix", "task": "tasks", "research": "research", "review": "reviews"}
    available_types = []
    for wt, dirname in type_map.items():
        type_path = Path("projects") / project / "technical" / dirname
        if _list_subdirs(type_path):
            available_types.append(wt)

    if not available_types:
        print(f"\n  No work items in {project}. Start something new instead.")
        sys.exit(1)

    work_type = _pick(available_types, "Work type")
    type_dir = type_map[work_type]
    items_path = Path("projects") / project / "technical" / type_dir
    items = _list_subdirs(items_path)
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
    _ensure_shared()

    print("Developer Brain \u2014 Session Setup\n")

    action = _pick(["Continue existing work", "Start something new"], "Action")

    if action == "Start something new":
        project, work_type, item, item_path = _flow_new()
    else:
        project, work_type, item, item_path = _flow_continue()

    role = _pick(["Developer", "QE", "Reviewer"], "Role")

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
  python3 brain.py task <name>                  Create a brain-level task
  python3 brain.py task <project> <name>        Create a project-level task
  python3 brain.py research <name>              Create a brain-level research
  python3 brain.py research <project> <name>    Create a project-level research
  python3 brain.py review <name>                Create a brain-level PR review
  python3 brain.py review <project> <name>      Create a project-level PR review
  python3 brain.py check                        Audit brain docs for credentials
  python3 brain.py migrate-obsidian              Add frontmatter for Obsidian
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

    elif command == "task":
        if len(sys.argv) == 3:
            create_task(sys.argv[2])
        elif len(sys.argv) == 4:
            create_task(sys.argv[3], project=sys.argv[2])
        else:
            print("Usage: python3 brain.py task <name>              (brain-level)")
            print("       python3 brain.py task <project> <name>    (project-level)")
            sys.exit(1)

    elif command == "research":
        if len(sys.argv) == 3:
            create_research(sys.argv[2])
        elif len(sys.argv) == 4:
            create_research(sys.argv[3], project=sys.argv[2])
        else:
            print("Usage: python3 brain.py research <name>              (brain-level)")
            print("       python3 brain.py research <project> <name>    (project-level)")
            sys.exit(1)

    elif command == "review":
        if len(sys.argv) == 3:
            create_review(sys.argv[2])
        elif len(sys.argv) == 4:
            create_review(sys.argv[3], project=sys.argv[2])
        else:
            print("Usage: python3 brain.py review <name>              (brain-level)")
            print("       python3 brain.py review <project> <name>    (project-level)")
            sys.exit(1)

    elif command == "check":
        run_check()

    elif command == "migrate-obsidian":
        migrate_obsidian()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
