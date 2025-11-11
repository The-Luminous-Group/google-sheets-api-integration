#!/usr/bin/env python3
"""
GitHub Issue Creation Tool
Uses GitHub CLI (gh) to create issues on any GitHub repository
"""

import subprocess
import sys
import json
from typing import Optional, List

def create_issue(
    repo: str,
    title: str,
    body: str,
    labels: Optional[List[str]] = None,
    assignees: Optional[List[str]] = None,
    milestone: Optional[str] = None
) -> dict:
    """
    Create a GitHub issue using the gh CLI

    Args:
        repo: Repository in format "owner/repo-name" (e.g., "pieces-app/support")
        title: Issue title
        body: Issue body/description (markdown supported)
        labels: List of label names (e.g., ["bug", "documentation"])
        assignees: List of GitHub usernames to assign (e.g., ["username"])
        milestone: Milestone name or number

    Returns:
        Dictionary with issue details including URL

    Raises:
        subprocess.CalledProcessError: If gh command fails
    """

    # Build the gh command
    cmd = [
        "gh", "issue", "create",
        "--repo", repo,
        "--title", title,
        "--body", body
    ]

    # Add optional parameters
    if labels:
        cmd.extend(["--label", ",".join(labels)])

    if assignees:
        cmd.extend(["--assignee", ",".join(assignees)])

    if milestone:
        cmd.extend(["--milestone", milestone])

    try:
        # Run the command and capture output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # Parse the URL from output
        issue_url = result.stdout.strip()

        # Get issue details
        issue_number = issue_url.split('/')[-1]

        return {
            "success": True,
            "url": issue_url,
            "number": issue_number,
            "repo": repo
        }

    except subprocess.CalledProcessError as e:
        print(f"Error creating GitHub issue: {e.stderr}", file=sys.stderr)
        return {
            "success": False,
            "error": e.stderr
        }

def check_gh_auth() -> bool:
    """
    Check if GitHub CLI is authenticated

    Returns:
        True if authenticated, False otherwise
    """
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: GitHub CLI (gh) is not installed", file=sys.stderr)
        print("Install it from: https://cli.github.com/", file=sys.stderr)
        return False

def print_issue_summary(issue_data: dict):
    """Print a formatted summary of the created issue"""
    if issue_data.get("success"):
        print(f"\n✓ GitHub issue created successfully!")
        print(f"  Repository: {issue_data['repo']}")
        print(f"  Issue #{issue_data['number']}")
        print(f"  URL: {issue_data['url']}")
    else:
        print(f"\n✗ Failed to create issue")
        print(f"  Error: {issue_data.get('error', 'Unknown error')}")

if __name__ == "__main__":
    # Example usage
    if not check_gh_auth():
        print("Please authenticate with: gh auth login")
        sys.exit(1)

    issue = create_issue(
        repo="owner/repo-name",
        title="Example Issue",
        body="This is an example issue created via GitHub CLI",
        labels=["bug"]
    )

    print_issue_summary(issue)
