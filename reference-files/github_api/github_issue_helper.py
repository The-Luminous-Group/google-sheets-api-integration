#!/usr/bin/env python3
"""
Helper script for creating GitHub issues
Provides a simplified interface for AI coding assistants
"""

from create_github_issue import create_issue, check_gh_auth, print_issue_summary
import sys

def create_issue_from_spec(spec: dict):
    """
    Create a GitHub issue from a specification dictionary

    Expected spec format:
    {
        "repo": str,              # Required: "owner/repo-name"
        "title": str,             # Required: Issue title
        "body": str,              # Required: Issue description (markdown supported)
        "labels": list[str],      # Optional: ["bug", "documentation"]
        "assignees": list[str],   # Optional: ["username1", "username2"]
        "milestone": str          # Optional: Milestone name or number
    }
    """

    # Check authentication first
    if not check_gh_auth():
        print("Error: GitHub CLI not authenticated")
        print("Run: gh auth login")
        sys.exit(1)

    # Validate required fields
    if "repo" not in spec or "title" not in spec or "body" not in spec:
        print("Error: spec must include 'repo', 'title', and 'body'")
        sys.exit(1)

    issue = create_issue(
        repo=spec["repo"],
        title=spec["title"],
        body=spec["body"],
        labels=spec.get("labels"),
        assignees=spec.get("assignees"),
        milestone=spec.get("milestone")
    )

    print_issue_summary(issue)
    return issue

if __name__ == "__main__":
    # Example usage
    spec = {
        "repo": "owner/repo-name",
        "title": "Example Bug Report",
        "body": """## Description

This is an example bug report with markdown formatting.

## Steps to Reproduce

1. Step one
2. Step two
3. Bug occurs

## Expected Behavior

Should work correctly.

## Actual Behavior

Does not work as expected.

## Environment

- OS: macOS
- Version: 1.0.0
""",
        "labels": ["bug"]
    }

    create_issue_from_spec(spec)
