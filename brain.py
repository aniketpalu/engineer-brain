#!/usr/bin/env python3
"""
Developer Brain — structured knowledge system for engineering work.

Creates and manages a directory-based documentation system designed for
use with AI coding assistants. See brain/README.md for full documentation.

Usage:
    python3 brain.py project <project_name>
    python3 brain.py feature <project_name> <feature_name>
    python3 brain.py bug <project_name> <bug_name>
"""

import sys
from pathlib import Path

BASE = Path("brain")


def create_dir(path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {path}")


def create_file(path, content=""):
    if not path.exists():
        with open(path, "w") as f:
            f.write(content)
        print(f"Created file: {path}")


# -------------------------
# PROJECT STRUCTURE
# -------------------------

def create_project(project_name):
    project_root = BASE / "projects" / project_name

    dirs = [
        "technical/features",
        "technical/bugfix",
        "technical/playbooks",
        "technical/system",
        "technical/knowledge",
        "non_technical",
    ]

    create_dir(BASE)
    create_dir(BASE / "projects")
    create_dir(BASE / "prompts")

    for d in dirs:
        create_dir(project_root / d)

    # Create starter playbooks
    playbooks = {
        "build_docker.md": "# Docker Build Playbook\n\nCommands to build docker images.\n",
        "run_tests.md": "# Test Playbook\n\nCommands to run tests.\n",
        "deploy_dev.md": "# Dev Deployment Playbook\n\nSteps to deploy to dev.\n",
        "experiment_template.md": "# Experiment Template\n\nGoal:\n\nSteps:\n\nResults:\n",
    }

    for name, content in playbooks.items():
        create_file(project_root / "technical/playbooks" / name, content)

    # System map starter
    create_file(
        project_root / "technical/system/system_map.md",
        "# System Map\n\nHigh level architecture diagrams.\n"
    )

    print(f"\nProject '{project_name}' initialized.\n")


# -------------------------
# FEATURE STRUCTURE
# -------------------------

def create_feature(project, feature_name):
    feature_dir = BASE / "projects" / project / "technical/features" / feature_name

    create_dir(feature_dir)

    files = {
        "intent.md": (
            f"# Feature Intent\n\n"
            f"Feature: {feature_name}\n\n"
            f"## Goal\n\n"
            f"## Why Needed\n\n"
            f"## Constraints\n\n"
            f"## Source Repositories\n\n"
            f"| Repo | Local Path |\n"
            f"|------|------------|\n"
            f"| | |\n\n"
            f"## Questions\n"
        ),
        "exploration.md": "# Code Exploration\n\n## Relevant Modules\n\n## Current Flow\n\n## Observations\n",
        "architecture.md": "# Architecture Decision\n\n## Options Considered\n\n## Selected Approach\n\n## Tradeoffs\n",
        "tasks.md": "# Task Breakdown\n\n## Overview\n\n## Tasks\n\n1.\n2.\n3.\n\n## Scope Decisions\n\n## Implementation Order\n",
        "implementation.md": "# Implementation Summary\n\n## Files Changed\n\n## Code Flow\n\n## Design Decisions\n",
        "tests.md": (
            f"# Test Plan\n\n"
            f"Feature: {feature_name}\n\n"
            f"## Test Strategy\n\n"
            f"## Test Cases\n\n"
            f"| # | Description | Type | Status |\n"
            f"|---|-------------|------|--------|\n"
            f"| 1 | | | |\n\n"
            f"## Edge Cases\n\n"
            f"## Test Results\n\n"
            f"## Notes\n"
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
    }

    for name, content in files.items():
        create_file(feature_dir / name, content)

    print(f"\nFeature '{feature_name}' created in project '{project}'.\n")


# -------------------------
# BUGFIX STRUCTURE
# -------------------------

def create_bug(project, bug_name):
    bug_dir = BASE / "projects" / project / "technical/bugfix" / bug_name

    create_dir(bug_dir)

    files = {
        "problem.md": f"# Bug Problem\n\nBug: {bug_name}\n\n## Description\n\n## Expected Behavior\n\n## Actual Behavior\n",
        "investigation.md": "# Investigation\n\n## Logs\n\n## Reproduction Steps\n\n## Observations\n",
        "fix_plan.md": "# Fix Plan\n\n## Root Cause\n\n## Proposed Fix\n",
        "fix_summary.md": "# Fix Summary\n\n## Files Changed\n\n## Reasoning\n",
    }

    for name, content in files.items():
        create_file(bug_dir / name, content)

    print(f"\nBugfix '{bug_name}' created in project '{project}'.\n")


# -------------------------
# MAIN
# -------------------------

def main():
    if len(sys.argv) < 3:
        print("""
Usage:

Create project:
    python3 brain.py project <project_name>

Create feature:
    python3 brain.py feature <project_name> <feature_name>

Create bugfix:
    python3 brain.py bug <project_name> <bug_name>
""")
        sys.exit(1)

    command = sys.argv[1]

    if command == "project":
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
        print("Unknown command")


if __name__ == "__main__":
    main()