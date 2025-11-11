# GitHub Issue Creation Tool

Automated GitHub issue creation for any repository using Python and AI coding assistants.

## What This Does

This tool allows you to create GitHub issues programmatically through AI coding assistants like Claude Code, Cursor, or Codex. Instead of manually filling out issue forms on GitHub's web interface, you can describe what you want and let the AI assistant handle the API calls via GitHub CLI.

**Key Features:**
- Create issues on any GitHub repository (public or private, with appropriate access)
- Support for all standard fields (title, description, labels, assignees, milestones)
- Works with any AI coding assistant that can run Python
- Uses GitHub CLI (`gh`) for authentication and API access
- No manual API token management required

## Getting Started

### Prerequisites

- Python 3.7 or higher
- GitHub CLI (`gh`) installed and authenticated
- Access to create issues in the target repository

### Installing GitHub CLI

If you don't have `gh` installed:

**macOS:**
```bash
brew install gh
```

**Windows:**
```bash
winget install GitHub.cli
```

**Linux:**
See [GitHub CLI installation guide](https://github.com/cli/cli#installation)

### Authentication

Authenticate with GitHub (one-time setup):

```bash
gh auth login
```

Follow the prompts to:
1. Select GitHub.com
2. Choose HTTPS protocol
3. Authenticate via web browser
4. Complete authorisation

**Verify authentication:**
```bash
gh auth status
```

### Switching Accounts

If you have multiple GitHub accounts:

```bash
# List available accounts
gh auth status

# Switch to a different account
gh auth switch --user username
```

## Usage

### With AI Coding Assistants

Tell your AI assistant (Claude Code, Cursor, Codex, etc.) what issue you want to create. For example:

> "Create a GitHub issue on pieces-app/support titled 'Copilot Not Responding' with a bug label describing the chat being unresponsive"

The assistant will use the Python scripts in this repo to create the issue via the GitHub CLI.

### Direct Python Usage (Developers)

```python
from github_issue_helper import create_issue_from_spec

spec = {
    "repo": "owner/repo-name",
    "title": "Bug: Feature X not working",
    "body": """## Description

Feature X has stopped working as of today.

## Steps to Reproduce

1. Open application
2. Navigate to Feature X
3. Click button
4. Observe error

## Expected Behavior

Feature should work without errors.

## Actual Behavior

Error message appears and feature fails.

## Environment

- OS: macOS 14.0
- Version: 1.2.3
""",
    "labels": ["bug"],
    "assignees": ["username"],  # Optional
    "milestone": "v2.0"  # Optional
}

create_issue_from_spec(spec)
```

## Repository Access

The tool can create issues on:

- **Public repositories** - Anyone can create issues
- **Private repositories** - Requires appropriate access (collaborator, organisation member, etc.)
- **Your own repositories** - Full access
- **Organisation repositories** - Based on your organisation role

GitHub CLI authentication handles permissions automatically.

## Examples

### Bug Report

```python
from github_issue_helper import create_issue_from_spec

spec = {
    "repo": "pieces-app/support",
    "title": "Copilot Not Responding",
    "body": """## Description

Copilot has not responded to queries for 2+ weeks.

## Steps to Reproduce

1. Open application
2. Send chat message
3. No response received

## Environment

- Pieces OS: 12.3.0
- macOS: Darwin 24.6.0
""",
    "labels": ["bug"]
}

create_issue_from_spec(spec)
```

### Feature Request

```python
spec = {
    "repo": "owner/project",
    "title": "Add dark mode support",
    "body": """## Feature Request

Add dark mode theme to improve usability in low-light environments.

## Use Case

Users working at night would benefit from reduced eye strain.

## Proposed Solution

Toggle in settings to switch between light and dark themes.
""",
    "labels": ["enhancement", "ui"]
}

create_issue_from_spec(spec)
```

### Documentation Issue

```python
spec = {
    "repo": "owner/docs-repo",
    "title": "Update installation instructions for macOS",
    "body": """## Documentation Gap

Current installation docs don't mention Homebrew installation method.

## Suggested Addition

Add section showing: `brew install tool-name`
""",
    "labels": ["documentation"],
    "assignees": ["doc-maintainer"]
}

create_issue_from_spec(spec)
```

## Common Use Cases

### Reporting Bugs to Open Source Projects

When you encounter bugs in tools you use:

```python
spec = {
    "repo": "maintainer/project",
    "title": "Clear description of the bug",
    "body": """
Include:
- What you were trying to do
- Steps to reproduce
- Expected vs actual behavior
- Your environment details
- Screenshots if relevant
""",
    "labels": ["bug"]
}
```

### Creating Issues in Your Own Projects

For tracking work in your repositories:

```python
spec = {
    "repo": "your-username/your-project",
    "title": "Implement new feature",
    "body": "Feature description and requirements",
    "labels": ["enhancement"],
    "assignees": ["your-username"],
    "milestone": "v1.0"
}
```

### Collaborative Issue Creation

For team projects:

```python
spec = {
    "repo": "organisation/team-project",
    "title": "Fix production bug",
    "body": "Bug details and impact",
    "labels": ["bug", "priority:high"],
    "assignees": ["teammate1", "teammate2"]
}
```

## Best Practices

### Before Creating an Issue

1. **Search for duplicates** - Check if the issue already exists
2. **Review contribution guidelines** - Check for CONTRIBUTING.md or issue templates
3. **Gather information** - Screenshots, error messages, reproduction steps
4. **Be specific** - Clear title and detailed description

### Writing Good Issues

**Good title:**
- "Copilot Not Responding"
- "Installation fails on macOS 14"
- "Add support for Python 3.12"

**Poor title:**
- "It doesn't work"
- "Bug"
- "Help needed"

**Good description:**
- Clear problem statement
- Steps to reproduce
- Expected vs actual behaviour
- Environment details
- Screenshots when relevant

**Poor description:**
- "It's broken"
- No context or details
- Vague descriptions

## Troubleshooting

### "GitHub CLI not authenticated"

**Solution:**
```bash
gh auth login
```

### "Not Found (HTTP 404)" when creating issue

**Possible causes:**
- Repository doesn't exist
- You don't have access to the repository
- Repository name is misspelt (check owner/repo-name format)

**Solution:**
```bash
# Verify you can access the repo
gh repo view owner/repo-name
```

### "This API operation needs the 'X' scope"

**Solution:**
```bash
# Refresh authentication with required scopes
gh auth refresh -h github.com -s repo -s user
```

### Wrong GitHub Account

**Check current account:**
```bash
gh auth status
```

**Switch accounts:**
```bash
gh auth switch --user your-other-username
```

## For Developers

### Project Structure

```
github_api/
├── create_github_issue.py    # Core functions using gh CLI
├── github_issue_helper.py     # Simplified interface for AI assistants
├── venv/                      # Virtual environment (not in git)
├── README.md                  # This file
└── .gitignore                 # Excludes sensitive files
```

### Available Functions

See `create_github_issue.py` for full API:
- `create_issue()` - Create an issue with all options
- `check_gh_auth()` - Verify GitHub CLI authentication
- `print_issue_summary()` - Format issue details

See `github_issue_helper.py` for simplified helpers:
- `create_issue_from_spec()` - Create issue from dictionary

### How It Works

This tool is a Python wrapper around GitHub CLI (`gh`):

1. **Authentication**: Uses `gh auth` for secure token management
2. **Issue Creation**: Calls `gh issue create` with appropriate parameters
3. **Response**: Parses output to return issue URL and number

**Why GitHub CLI?**
- Handles authentication automatically
- Supports multiple accounts
- No manual token management
- Works with all GitHub features
- Official GitHub tool

### Testing

```bash
# Check authentication
python3 -c "from create_github_issue import check_gh_auth; print(check_gh_auth())"

# Test issue creation (replace with your test repo)
python3 -c "
from github_issue_helper import create_issue_from_spec
spec = {
    'repo': 'your-username/test-repo',
    'title': 'Test Issue',
    'body': 'Testing automated issue creation',
    'labels': ['test']
}
create_issue_from_spec(spec)
"
```

## Contributing

This tool is part of The Luminous Group's internal automation toolkit. For questions or suggestions, create an issue in the repository or discuss with the team.

## Related Tools

- [linear-api-integration](https://github.com/The-Luminous-Group/linear-api-integration) - Python tools for creating Linear issues programmatically
- [docs](https://github.com/The-Luminous-Group/docs) - Technical documentation for Luminous Group processes

## License

Internal tool for The Luminous Group.

---

**Created:** 25 October 2025
**Author:** Barton (with Claude Code)
**First Use Case:** Reporting Pieces OS Copilot bug ([#904](https://github.com/pieces-app/support/issues/904))
