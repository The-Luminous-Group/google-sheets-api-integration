#!/usr/bin/env python3
"""
Helper script for assistants to create and manage Linear issues with structured specs.
"""

import argparse
import os

from create_linear_issue import (
    get_api_key,
    create_issue,
    update_issue,
    create_issue_relation,
    create_comment,
    print_issue_summary,
    get_issues_assigned_to,
)

def create_issue_from_spec(spec: dict):
    """
    Create a Linear issue from a specification dictionary

    Expected spec format:
    {
        "title": str,
        "description": str,
        "assignee_email": str (optional),
        "subscriber_emails": list[str] (optional),
        "label_names": list[str] (optional),
        "parent_identifier": str (optional, e.g., "LUM-12"),
        "priority": int (optional, 1-4, default 3),
        "due_date": str (optional, "YYYY-MM-DD" format, e.g., "2025-10-28"),
        "relations": list[dict] (optional) - [{"issue": "LUM-12", "type": "related"}]
    }
    """
    api_key = get_api_key()

    issue = create_issue(
        api_key=api_key,
        title=spec["title"],
        description=spec["description"],
        assignee_email=spec.get("assignee_email"),
        subscriber_emails=spec.get("subscriber_emails"),
        label_names=spec.get("label_names"),
        parent_identifier=spec.get("parent_identifier"),
        priority=spec.get("priority", 3),
        due_date=spec.get("due_date"),
    )

    print_issue_summary(issue)

    # Create relations if specified
    if spec.get("relations"):
        for relation in spec["relations"]:
            related_issue = relation.get("issue")
            relation_type = relation.get("type", "related")

            if related_issue:
                print(f"\nCreating {relation_type} relation to {related_issue}...")
                relation_result = create_issue_relation(
                    api_key=api_key,
                    issue_identifier=issue["identifier"],
                    related_issue_identifier=related_issue,
                    relation_type=relation_type
                )
                print(f"  ✓ {issue['identifier']} {relation_type} → {related_issue}")

    return issue

def update_issue_from_spec(issue_identifier: str, spec: dict):
    """
    Update an existing Linear issue from a specification dictionary

    Args:
        issue_identifier: The issue ID (e.g., "LUM-12")
        spec: Dictionary with fields to update (all optional):
        {
            "title": str (optional),
            "description": str (optional),
            "assignee_email": str (optional),
            "subscriber_emails": list[str] (optional),
            "label_names": list[str] (optional),
            "parent_identifier": str (optional, e.g., "LUM-12"),
            "priority": int (optional, 1-4),
            "state_name": str (optional, e.g., "Done"),
            "due_date": str (optional, "YYYY-MM-DD" format, e.g., "2025-10-28")
        }

    Note: Only fields provided in spec will be updated. Others remain unchanged.
    """
    api_key = get_api_key()

    issue = update_issue(
        api_key=api_key,
        issue_identifier=issue_identifier,
        title=spec.get("title"),
        description=spec.get("description"),
        assignee_email=spec.get("assignee_email"),
        subscriber_emails=spec.get("subscriber_emails"),
        label_names=spec.get("label_names"),
        parent_identifier=spec.get("parent_identifier"),
        priority=spec.get("priority"),
        due_date=spec.get("due_date"),
        state_name=spec.get("state_name"),
    )

    print_issue_summary(issue, action="updated")
    return issue

def add_comment(issue_identifier: str, comment_body: str):
    """
    Add a comment to a Linear issue

    Args:
        issue_identifier: The issue ID (e.g., "LUM-7")
        comment_body: The comment text (markdown supported)

    Returns:
        The created comment data
    """
    api_key = get_api_key()

    comment = create_comment(
        api_key=api_key,
        issue_identifier=issue_identifier,
        body=comment_body
    )

    print(f"\n✓ Comment added to {issue_identifier}")
    print(f"  By: {comment['user']['name']} ({comment['user']['email']})")
    print(f"  Issue: {comment['issue']['title']}")

    return comment


def list_assigned_issues(
    assignee_email: str,
    limit: int = 20,
    include_completed: bool = False,
):
    """Print and return issues assigned to the specified user."""
    api_key = get_api_key()
    issues = get_issues_assigned_to(
        api_key=api_key,
        assignee_email=assignee_email,
        limit=limit,
        include_completed=include_completed,
    )

    if not issues:
        print(f"No issues found for {assignee_email} (include_completed={include_completed}).")
        return []

    for issue in issues:
        state = issue.get("state", {})
        state_name = state.get("name", "Unknown state")
        print(
            f"- {issue['identifier']} · {state_name} · {issue['title']}"
        )
        if issue.get("dueDate"):
            print(f"  Due: {issue['dueDate']}")
        print(f"  URL: {issue['url']}")

    return issues

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List Linear issues assigned to a teammate.")
    parser.add_argument("--email", help="Email address to filter by (defaults to LINEAR_DEFAULT_EMAIL)")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of issues to fetch")
    parser.add_argument(
        "--include-completed",
        action="store_true",
        help="Include completed issues",
    )

    args = parser.parse_args()

    email = args.email or os.getenv("LINEAR_DEFAULT_EMAIL")
    if not email:
        print("Error: Provide an email via --email or set LINEAR_DEFAULT_EMAIL.")
        raise SystemExit(1)

    print(f"Listing issues assigned to {email} (include_completed={args.include_completed})...\n")
    list_assigned_issues(
        assignee_email=email,
        limit=args.limit,
        include_completed=args.include_completed,
    )
