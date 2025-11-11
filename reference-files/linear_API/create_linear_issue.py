#!/usr/bin/env python3
"""
Linear Issue Creator - Parameterized version
Creates issues in Linear via GraphQL API using issue specifications
"""

import os
import sys
import json
import subprocess
import requests
import getpass
from typing import Optional, List, Dict, Callable

LINEAR_API_URL = "https://api.linear.app/graphql"


def _from_env() -> Optional[str]:
    value = os.getenv("LINEAR_API_KEY")
    return value.strip() if value else None


def _from_keychain() -> Optional[str]:
    service = os.getenv("LINEAR_KEYCHAIN_SERVICE", "Linear API Key")
    account = os.getenv("LINEAR_KEYCHAIN_ACCOUNT", getpass.getuser())

    try:
        result = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-a",
                account,
                "-s",
                service,
                "-w",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()
        return output or None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _from_1password() -> Optional[str]:
    item_path = os.getenv("LINEAR_1PASSWORD_PATH", "op://Personal/Linear/credential")

    try:
        result = subprocess.run(
            ["op", "read", item_path],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()
        return output or None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


API_KEY_SOURCES: Dict[str, Callable[[], Optional[str]]] = {
    "env": _from_env,
    "keychain": _from_keychain,
    "1password": _from_1password,
}


def get_api_key() -> str:
    """Retrieve the Linear API key using configurable sources."""
    source_env = os.getenv("LINEAR_API_SOURCES")
    if source_env:
        preferred_sources = [item.strip().lower() for item in source_env.split(",") if item.strip()]
    else:
        preferred_sources = ["env", "keychain", "1password"]

    tried: List[str] = []

    for source in preferred_sources:
        retriever = API_KEY_SOURCES.get(source)
        if not retriever:
            tried.append(f"{source} (unknown)")
            continue

        value = retriever()
        if value:
            return value
        tried.append(source)

    print("Error: Unable to retrieve Linear API key.")
    if tried:
        print("Tried sources: " + ", ".join(tried))
    else:
        print("Tried sources: (none)")
    print("Set LINEAR_API_KEY, store the key in Keychain (service 'Linear API Key'), or configure a 1Password item.")
    print("Override lookup order via LINEAR_API_SOURCES (comma separated, e.g., 'env,1password').")
    sys.exit(1)

def query_linear(api_key: str, query: str, variables: Optional[Dict] = None) -> Dict:
    """Execute a GraphQL query against Linear API"""
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(LINEAR_API_URL, json=payload, headers=headers)

    if response.status_code != 200:
        print(f"Error: API returned {response.status_code}")
        print(response.text)
        sys.exit(1)

    return response.json()

def get_team_id(api_key: str, team_name: Optional[str] = None) -> str:
    """Get team ID by name, or return first team if no name specified"""
    query = """
    query {
      teams {
        nodes {
          id
          name
          key
        }
      }
    }
    """

    data = query_linear(api_key, query)
    teams = data.get("data", {}).get("teams", {}).get("nodes", [])

    if not teams:
        print("Error: No teams found")
        sys.exit(1)

    if team_name:
        for team in teams:
            if team["name"].lower() == team_name.lower():
                return team["id"]
        print(f"Error: Team '{team_name}' not found")
        sys.exit(1)

    return teams[0]["id"]

def get_user_id(api_key: str, email: str) -> Optional[str]:
    """Get user ID by email address"""
    query = """
    query {
      users {
        nodes {
          id
          name
          email
        }
      }
    }
    """

    data = query_linear(api_key, query)
    users = data.get("data", {}).get("users", {}).get("nodes", [])

    for user in users:
        if user.get("email", "").lower() == email.lower():
            return user["id"]

    return None

def get_issue_id_by_identifier(api_key: str, identifier: str) -> Optional[str]:
    """Get issue ID by identifier (e.g., 'LUM-12')"""
    query = """
    query($identifier: String!) {
      issue(id: $identifier) {
        id
        identifier
      }
    }
    """

    data = query_linear(api_key, query, {"identifier": identifier})
    issue = data.get("data", {}).get("issue")

    if issue:
        return issue["id"]

    return None

def get_label_ids(api_key: str, label_names: List[str]) -> List[str]:
    """Get label IDs by names"""
    query = """
    query {
      issueLabels {
        nodes {
          id
          name
        }
      }
    }
    """

    data = query_linear(api_key, query)
    labels = data.get("data", {}).get("issueLabels", {}).get("nodes", [])

    label_map = {label["name"].lower(): label["id"] for label in labels}

    label_ids = []
    for name in label_names:
        label_id = label_map.get(name.lower())
        if label_id:
            label_ids.append(label_id)
        else:
            print(f"Warning: Label '{name}' not found")

    return label_ids


def get_state_id(
    api_key: str,
    state_name: str,
    team_name: Optional[str] = None,
) -> Optional[str]:
    """Return the workflow state ID matching the provided name (and optional team)."""
    query = """
    query {
      workflowStates {
        nodes {
          id
          name
          type
          team {
            id
            name
          }
        }
      }
    }
    """

    data = query_linear(api_key, query)
    states = data.get("data", {}).get("workflowStates", {}).get("nodes", [])

    state_name_lower = state_name.lower()

    for state in states:
        if state.get("name", "").lower() != state_name_lower:
            continue
        if team_name and state.get("team", {}).get("name", "").lower() != team_name.lower():
            continue
        return state["id"]

    return None


def get_issues_assigned_to(
    api_key: str,
    assignee_email: str,
    limit: int = 20,
    include_completed: bool = False,
) -> List[Dict]:
    """Return issues assigned to the given user."""
    assignee_id = get_user_id(api_key, assignee_email)

    if not assignee_id:
        print(f"Error: User '{assignee_email}' not found")
        return []

    issue_filter: Dict[str, Dict] = {
        "assignee": {"id": {"eq": assignee_id}}
    }

    if not include_completed:
        issue_filter["state"] = {"type": {"neq": "completed"}}

    query = """
    query IssuesByAssignee($filter: IssueFilter!, $first: Int!) {
      issues(filter: $filter, first: $first, orderBy: updatedAt) {
        nodes {
          identifier
          title
          url
          updatedAt
          dueDate
          priority
          state {
            name
            type
          }
        }
      }
    }
    """

    variables = {"filter": issue_filter, "first": limit}
    data = query_linear(api_key, query, variables)

    if "errors" in data:
        print("Error fetching issues:")
        print(json.dumps(data["errors"], indent=2))
        return []

    return data.get("data", {}).get("issues", {}).get("nodes", [])

def create_issue_relation(
    api_key: str,
    issue_identifier: str,
    related_issue_identifier: str,
    relation_type: str = "related"
) -> Dict:
    """
    Create a relation between two issues

    Args:
        api_key: Linear API key
        issue_identifier: The issue identifier (e.g., "LUM-17")
        related_issue_identifier: The related issue identifier (e.g., "LUM-12")
        relation_type: Type of relation - "related", "blocks", "duplicate", or "similar"

    Returns:
        The created relation data
    """
    # Validate relation type
    valid_types = ["related", "blocks", "duplicate", "similar"]
    if relation_type not in valid_types:
        print(f"Error: Invalid relation type '{relation_type}'")
        print(f"Valid types: {', '.join(valid_types)}")
        sys.exit(1)

    # Get issue IDs
    issue_id = get_issue_id_by_identifier(api_key, issue_identifier)
    if not issue_id:
        print(f"Error: Issue '{issue_identifier}' not found")
        sys.exit(1)

    related_issue_id = get_issue_id_by_identifier(api_key, related_issue_identifier)
    if not related_issue_id:
        print(f"Error: Related issue '{related_issue_identifier}' not found")
        sys.exit(1)

    # Create the relation
    mutation = """
    mutation IssueRelationCreate($input: IssueRelationCreateInput!) {
      issueRelationCreate(input: $input) {
        success
        issueRelation {
          id
          type
          issue {
            identifier
            title
          }
          relatedIssue {
            identifier
            title
          }
        }
      }
    }
    """

    input_data = {
        "issueId": issue_id,
        "relatedIssueId": related_issue_id,
        "type": relation_type
    }

    data = query_linear(api_key, mutation, {"input": input_data})

    if "errors" in data:
        print("Error creating issue relation:")
        print(json.dumps(data["errors"], indent=2))
        sys.exit(1)

    result = data.get("data", {}).get("issueRelationCreate", {})

    if not result.get("success"):
        print("Failed to create issue relation")
        print(json.dumps(result, indent=2))
        sys.exit(1)

    return result["issueRelation"]

def create_issue(
    api_key: str,
    title: str,
    description: str,
    team_name: Optional[str] = None,
    assignee_email: Optional[str] = None,
    subscriber_emails: Optional[List[str]] = None,
    label_names: Optional[List[str]] = None,
    parent_identifier: Optional[str] = None,
    priority: int = 3,
    due_date: Optional[str] = None
) -> Dict:
    """
    Create a Linear issue with the specified parameters

    Args:
        due_date: Due date in ISO 8601 format (YYYY-MM-DD), e.g., "2025-10-28"
    """

    # Get team ID
    team_id = get_team_id(api_key, team_name)

    # Build input data
    input_data = {
        "teamId": team_id,
        "title": title,
        "description": description,
        "priority": priority
    }

    # Add due date if provided
    if due_date:
        input_data["dueDate"] = due_date

    # Add assignee if provided
    if assignee_email:
        assignee_id = get_user_id(api_key, assignee_email)
        if assignee_id:
            input_data["assigneeId"] = assignee_id
        else:
            print(f"Warning: User '{assignee_email}' not found")

    # Add subscribers if provided
    if subscriber_emails:
        subscriber_ids = []
        for email in subscriber_emails:
            user_id = get_user_id(api_key, email)
            if user_id:
                subscriber_ids.append(user_id)
            else:
                print(f"Warning: Subscriber '{email}' not found")
        if subscriber_ids:
            input_data["subscriberIds"] = subscriber_ids

    # Add labels if provided
    if label_names:
        label_ids = get_label_ids(api_key, label_names)
        if label_ids:
            input_data["labelIds"] = label_ids

    # Add parent if provided
    if parent_identifier:
        parent_id = get_issue_id_by_identifier(api_key, parent_identifier)
        if parent_id:
            input_data["parentId"] = parent_id
        else:
            print(f"Warning: Parent issue '{parent_identifier}' not found")

    # Create the issue
    mutation = """
    mutation IssueCreate($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue {
          id
          identifier
          title
          url
          parent {
            identifier
          }
          labels {
            nodes {
              name
            }
          }
          assignee {
            name
            email
          }
          subscribers {
            nodes {
              name
              email
            }
          }
        }
      }
    }
    """

    data = query_linear(api_key, mutation, {"input": input_data})

    if "errors" in data:
        print("Error creating issue:")
        print(json.dumps(data["errors"], indent=2))
        sys.exit(1)

    result = data.get("data", {}).get("issueCreate", {})

    if not result.get("success"):
        print("Failed to create issue")
        print(json.dumps(result, indent=2))
        sys.exit(1)

    return result["issue"]

def update_issue(
    api_key: str,
    issue_identifier: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    assignee_email: Optional[str] = None,
    subscriber_emails: Optional[List[str]] = None,
    label_names: Optional[List[str]] = None,
    parent_identifier: Optional[str] = None,
    priority: Optional[int] = None,
    state_name: Optional[str] = None,
    due_date: Optional[str] = None
) -> Dict:
    """
    Update an existing Linear issue with the specified parameters

    Args:
        due_date: Due date in ISO 8601 format (YYYY-MM-DD), e.g., "2025-10-28"
    """

    # Get the issue ID from identifier
    issue_id = get_issue_id_by_identifier(api_key, issue_identifier)
    if not issue_id:
        print(f"Error: Issue '{issue_identifier}' not found")
        sys.exit(1)

    # Build input data (only include fields that are provided)
    input_data = {}

    if title is not None:
        input_data["title"] = title

    if description is not None:
        input_data["description"] = description

    if priority is not None:
        input_data["priority"] = priority

    if due_date is not None:
        input_data["dueDate"] = due_date

    if state_name is not None:
        state_id = get_state_id(api_key, state_name)
        if state_id:
            input_data["stateId"] = state_id
        else:
            print(f"Warning: State '{state_name}' not found")

    # Add assignee if provided
    if assignee_email is not None:
        assignee_id = get_user_id(api_key, assignee_email)
        if assignee_id:
            input_data["assigneeId"] = assignee_id
        else:
            print(f"Warning: User '{assignee_email}' not found")

    # Add subscribers if provided
    if subscriber_emails is not None:
        subscriber_ids = []
        for email in subscriber_emails:
            user_id = get_user_id(api_key, email)
            if user_id:
                subscriber_ids.append(user_id)
            else:
                print(f"Warning: Subscriber '{email}' not found")
        if subscriber_ids:
            input_data["subscriberIds"] = subscriber_ids

    # Add labels if provided
    if label_names is not None:
        label_ids = get_label_ids(api_key, label_names)
        if label_ids:
            input_data["labelIds"] = label_ids

    # Add parent if provided
    if parent_identifier is not None:
        parent_id = get_issue_id_by_identifier(api_key, parent_identifier)
        if parent_id:
            input_data["parentId"] = parent_id
        else:
            print(f"Warning: Parent issue '{parent_identifier}' not found")

    # Update the issue
    mutation = """
    mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        success
        issue {
          id
          identifier
          title
          url
          parent {
            identifier
          }
          labels {
            nodes {
              name
            }
          }
          assignee {
            name
            email
          }
          subscribers {
            nodes {
              name
              email
            }
          }
        }
      }
    }
    """

    data = query_linear(api_key, mutation, {"id": issue_id, "input": input_data})

    if "errors" in data:
        print("Error updating issue:")
        print(json.dumps(data["errors"], indent=2))
        sys.exit(1)

    result = data.get("data", {}).get("issueUpdate", {})

    if not result.get("success"):
        print("Failed to update issue")
        print(json.dumps(result, indent=2))
        sys.exit(1)

    return result["issue"]

def create_comment(
    api_key: str,
    issue_identifier: str,
    body: str
) -> Dict:
    """
    Create a comment on a Linear issue

    Args:
        api_key: Linear API key
        issue_identifier: The issue identifier (e.g., "LUM-7")
        body: The comment text (markdown supported)

    Returns:
        The created comment data
    """

    # Get the issue ID from identifier
    issue_id = get_issue_id_by_identifier(api_key, issue_identifier)
    if not issue_id:
        print(f"Error: Issue '{issue_identifier}' not found")
        sys.exit(1)

    # Create the comment
    mutation = """
    mutation CommentCreate($input: CommentCreateInput!) {
      commentCreate(input: $input) {
        success
        comment {
          id
          body
          createdAt
          user {
            name
            email
          }
          issue {
            identifier
            title
          }
        }
      }
    }
    """

    input_data = {
        "issueId": issue_id,
        "body": body
    }

    data = query_linear(api_key, mutation, {"input": input_data})

    if "errors" in data:
        print("Error creating comment:")
        print(json.dumps(data["errors"], indent=2))
        sys.exit(1)

    result = data.get("data", {}).get("commentCreate", {})

    if not result.get("success"):
        print("Failed to create comment")
        print(json.dumps(result, indent=2))
        sys.exit(1)

    return result["comment"]


def update_comment(
    api_key: str,
    comment_id: str,
    body: str
) -> Dict:
    """
    Update an existing Linear comment

    Args:
        api_key: Linear API key
        comment_id: The comment ID to update
        body: The new comment text (markdown supported)

    Returns:
        The updated comment data
    """

    # Update the comment
    mutation = """
    mutation CommentUpdate($id: String!, $input: CommentUpdateInput!) {
      commentUpdate(id: $id, input: $input) {
        success
        comment {
          id
          body
          updatedAt
          user {
            name
            email
          }
          issue {
            identifier
            title
          }
        }
      }
    }
    """

    variables = {
        "id": comment_id,
        "input": {
            "body": body
        }
    }

    data = query_linear(api_key, mutation, variables)

    if "errors" in data:
        print("Error updating comment:")
        print(json.dumps(data["errors"], indent=2))
        sys.exit(1)

    result = data.get("data", {}).get("commentUpdate", {})

    if not result.get("success"):
        print("Failed to update comment")
        print(json.dumps(result, indent=2))
        sys.exit(1)

    return result["comment"]


def print_issue_summary(issue: Dict, action: str = "created"):
    """Print a formatted summary of the created/updated issue"""
    print(f"\n✓ Issue {action} successfully!")
    print(f"  ID: {issue['identifier']}")
    print(f"  Title: {issue['title']}")

    if issue.get("assignee"):
        print(f"  Assignee: {issue['assignee']['name']} ({issue['assignee']['email']})")

    if issue.get("subscribers", {}).get("nodes"):
        subscribers = [f"{s['name']} ({s['email']})" for s in issue["subscribers"]["nodes"]]
        print(f"  Subscribers: {', '.join(subscribers)}")

    if issue.get("parent"):
        print(f"  Parent: {issue['parent']['identifier']}")

    if issue.get("labels", {}).get("nodes"):
        labels = [l["name"] for l in issue["labels"]["nodes"]]
        print(f"  Labels: {', '.join(labels)}")

    print(f"  URL: {issue['url']}")

def main():
    """Example usage"""
    api_key = get_api_key()

    # Example: Create a simple issue
    issue = create_issue(
        api_key=api_key,
        title="Test Issue",
        description="This is a test issue created with the parameterized script"
    )

    print_issue_summary(issue)

if __name__ == "__main__":
    main()
