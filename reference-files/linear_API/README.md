# Linear Issue Creation Tool

Automated issue creation for the Luminous Group Linear workspace using Python and AI coding assistants.

**⚠️ IMPORTANT FOR AI ASSISTANTS:** This project uses a Python virtual environment. Always activate it before running scripts:
```bash
source venv/bin/activate  # Must run from the project root directory
```

## What This Does

This tool allows you to create and manage Linear issues programmatically through AI coding assistants like Claude Code, Cursor, or Codex. Instead of manually creating issues in Linear's web interface, you can describe what you want and let the AI assistant handle the API calls.

**Key Features:**
- Create issues with all standard fields (title, description, assignee, labels, priority, due dates)
- Update existing issues
- Add comments to issues (progress updates, discussions, meeting notes)
- Link issues together with relationships (parent/child, blocks, related)
- Add subscribers/watchers to issues
- Works with any AI coding assistant that can run Python

## Getting Started

### Prerequisites

- Python 3.7 or higher
- A Linear account with access to the Luminous Group workspace
- A Linear API key (instructions below)
- An AI coding assistant (Claude Code, Cursor, Codex, etc.)

### Getting Your Linear API Key

1. Log into Linear at https://linear.app
2. Go to **Settings** → **API** (or **Settings** → **Account** → **API**)
3. Click **"Create new API key"** or **"Personal API keys"**
4. Give it a descriptive name (e.g., "AI Assistant - Issue Creation")
5. Copy the key immediately (it's only shown once)

For detailed instructions, see [Linear's API documentation](https://developers.linear.app/docs/graphql/working-with-the-graphql-api#authentication).

### Installation

1. Clone this repository
2. Navigate to the project directory
3. Install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration: Securing Your API Key

**IMPORTANT:** Your API key is like a password. Never commit it to git or share it publicly.

**⚠️ SECURITY BEST PRACTICE:** Use Keychain or 1Password for secure storage. Avoid environment variables and `.env` files as they can leak in logs, get accidentally committed, or be exposed to other processes.

---

### ✅ Recommended: Secure Storage Methods

#### Option 1: macOS Keychain (Recommended on Mac)

1. Store the key (macOS will prompt the first time a script reads it):
   ```bash
   security add-generic-password \
     -a "$USER" \
     -s "Linear API Key" \
     -w 'your_api_key_here' \
     -U
   ```
2. Optional overrides via environment variables:
   - `LINEAR_KEYCHAIN_SERVICE` (default `Linear API Key`)
   - `LINEAR_KEYCHAIN_ACCOUNT` (default current macOS user)

**Why this is secure:**
- Keys stored in encrypted macOS Keychain
- Access controlled by macOS security
- Not visible in process lists or logs

#### Option 2: 1Password CLI (Recommended if you use 1Password)

1. Install 1Password CLI: https://developer.1password.com/docs/cli/get-started/
2. Store your API key in 1Password with field "credential" (default item name: "Linear")
3. The script will automatically retrieve it when needed

**Custom item names:** If your 1Password item has a different name (e.g., "Linear API Key"), set the path:
```bash
export LINEAR_1PASSWORD_PATH="op://Personal/Linear API Key/credential"
```

**Why this is secure:**
- Keys stored in 1Password vault with encryption
- Biometric authentication available
- Centralized credential management

---

### ⚠️ Not Recommended: Insecure Methods

**The following methods work but are less secure. Use only if Keychain/1Password are unavailable.**

#### Option 3: Environment Variable (Not Recommended)

Add to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):
```bash
export LINEAR_API_KEY='your_api_key_here'
```

Then reload: `source ~/.zshrc`

**Security risks:**
- Visible in process lists (`ps aux | grep LINEAR`)
- May appear in shell history
- Inherited by all child processes
- Can leak in error logs and crash dumps

#### Option 4: .env File (Not Recommended)

1. Copy the template:
   ```bash
   cp .env.template .env
   ```
2. Edit `.env` and replace `your_api_key_here` with your actual key
3. Make sure `.env` is in `.gitignore` (it already is)

**Security risks:**
- Plain text file on disk
- Easy to accidentally commit to git
- Readable by any process with file system access
- No encryption at rest

---

**The script will automatically try these options in order:** environment variable → Keychain → 1Password → `.env` file

Override the order with `LINEAR_API_SOURCES` (comma separated, e.g., `LINEAR_API_SOURCES=keychain,1password`).

### Discovering Your Authentication Setup

**For AI Assistants:** If you're unsure which authentication method is configured on this machine, run these checks:

```bash
# Check 1: Environment variable
echo $LINEAR_API_KEY
# If this prints a key (lin_api_...), authentication is via environment variable

# Check 2: macOS Keychain (macOS only)
security find-generic-password -a "$USER" -s "Linear API Key" 2>/dev/null
# If this succeeds, authentication is via Keychain

# Check 3: 1Password CLI
op --version 2>/dev/null && echo "1Password CLI is installed"
# If installed, check if the item exists:
op item get Linear 2>/dev/null
# If this succeeds, authentication may be via 1Password

# Check 4: .env file
test -f .env && echo ".env file exists" || echo "No .env file"
# If exists, check contents: grep LINEAR_API_KEY .env
```

**Quick test:** After activating venv, try running:
```bash
source venv/bin/activate
python -c "from create_linear_issue import get_api_key; get_api_key(); print('Authentication OK')"
```

If this prints "Authentication OK", your setup is working. If it fails, it will tell you which sources it tried.

## Usage

### ⚠️ For AI Assistants: Pre-Flight Checklist

**BEFORE running ANY Python scripts in this project:**

1. **ALWAYS activate the virtual environment first:**
   ```bash
   source venv/bin/activate
   ```
   If you see `ModuleNotFoundError` or import errors, you forgot this step.

2. **Verify you're in the project root directory** (`/path/to/linear-api-integration`)

3. **Check authentication is configured** (see "Discovering Your Authentication Setup" below)

### With AI Coding Assistants

Tell your AI assistant (Claude Code, Cursor, Codex, etc.) what issue you want to create. For example:

> "Create a Linear issue titled 'Update documentation' assigned to alexandre@luminousgroup.net with labels 'knowledge system' and priority High"

The assistant will use the Python scripts in this repo to create the issue via the Linear API.

### Direct Python Usage (Developers)

```python
from issue_helper import create_issue_from_spec

spec = {
    "title": "Issue Title",
    "description": "Full description...",
    "assignee_email": "user@luminousgroup.net",
    "subscriber_emails": ["supporter@luminousgroup.net"],  # Optional
    "label_names": ["service catalogue", "team task"],
    "parent_identifier": "LUM-12",  # Optional - makes this a sub-issue
    "priority": 2,  # 1=Urgent, 2=High, 3=Normal (default), 4=Low
    "due_date": "2025-10-28",  # Optional, YYYY-MM-DD format
    "state_name": "In Progress",  # Optional, workflow state by name (e.g., "Done")
    "relations": [  # Optional - link to other issues
        {"issue": "LUM-12", "type": "related"},
        {"issue": "LUM-5", "type": "blocks"}
    ]
}

create_issue_from_spec(spec)
```

### Quick CLI: List Assigned Issues

```bash
source venv/bin/activate
LINEAR_DEFAULT_EMAIL=volker@luminousgroup.net python issue_helper.py
# or provide parameters explicitly
python issue_helper.py --email volker@luminousgroup.net --limit 50 --include-completed
```

This uses the same authentication lookup order described above.

### Updating Existing Issues

```python
from issue_helper import update_issue_from_spec

update_issue_from_spec("LUM-24", {
    "due_date": "2025-11-01",
    "priority": 1,
    "subscriber_emails": ["newperson@luminousgroup.net"]
})
```

### Adding Comments to Issues

```python
from issue_helper import add_comment

add_comment("LUM-7", """
## Progress Update

Met with the team today to discuss timeline:
- Draft completion: End of week
- Review period: Next week
- Publication target: Following Wednesday
""")
```

### Updating Existing Comments

```python
from create_linear_issue import update_comment, get_api_key

api_key = get_api_key()
comment_id = "comment-uuid-from-linear"

update_comment(api_key, comment_id, """
## Updated Progress

Timeline has changed:
- Draft completion: Next Monday
- Review period: Following week
- Publication target: Two weeks out
""")
```

**Note:** To update a comment, you need its UUID (not the issue identifier). You can find this by querying the issue's comments via the Linear API or from the comment URL in Linear's web interface.

**Use comments for:**
- Progress updates and status changes
- Timeline adjustments
- Discussion and feedback
- Meeting notes related to the issue

**Keep descriptions for:**
- Original requirements and scope
- Permanent context about the issue

## Linear Workspace Reference

### Team

- **Name:** Luminous Group
- **Key:** LUM (all issues are LUM-###)

### Available Labels

Use these exact names when creating issues:

**Marketing (use one of these, not "marketing" itself):**
- `blog post`
- `luminous narrative`
- `personae and pain points`

**Business Development:**
- `lead generation`

**General:**
- `knowledge system`
- `service catalogue`
- `strategic plan`
- `team task`

**Issue Types:**
- `Bug`
- `Feature`
- `Improvement`

### Team Members

- alexandre@luminousgroup.net
- barton@luminousgroup.net
- klemen@luminousgroup.net
- volker@luminousgroup.net

### Priority Levels

- `1` - Urgent
- `2` - High
- `3` - Normal (default)
- `4` - Low

### Relation Types

When linking issues:
- `related` - General relationship
- `blocks` - This issue blocks another
- `duplicate` - Issues are duplicates
- `similar` - Issues are similar

## Security Best Practices

### What is an API Key?

An API key is a secret token that acts like a password for automated access to Linear. Anyone with your API key can create, modify, or delete issues in your name.

### Keeping Your Key Secure

**DO:**
- Store it using one of the secure methods above
- Treat it like a password (don't share or expose it)
- Use different keys for different purposes
- Revoke and regenerate if accidentally exposed

**DON'T:**
- Commit it to git
- Share it in chat or email
- Include it in screenshots
- Hard-code it in scripts

### If Your Key is Exposed

1. Go to Linear → Settings → API
2. Delete the compromised key
3. Create a new one
4. Update your secure storage with the new key

## Troubleshooting

### "ModuleNotFoundError" or "No module named 'requests'"

**Cause:** You forgot to activate the virtual environment.

**Solution:**
```bash
source venv/bin/activate  # Run from project root
```

You should see `(venv)` appear in your terminal prompt. **Always activate venv before running any Python scripts.**

### "Error: LINEAR_API_KEY environment variable not set"

Your API key isn't configured. Follow the Configuration section above to set it up, or use the "Discovering Your Authentication Setup" section to check which method is configured.

### "Error: Could not retrieve API key from 1Password"

If using 1Password CLI:
1. Make sure 1Password CLI is installed: `op --version`
2. Sign in: `op signin`
3. Verify the item exists: `op item get Linear`

### "Warning: Label 'xyz' not found"

Check the spelling against the Available Labels section above. Remember that "marketing" is a group - use specific labels like "blog post" instead.

### "Warning: User 'email@example.com' not found"

The email address isn't in the Luminous Group workspace. Check the Team Members section above for valid emails.

## For Developers

### Project Structure

```
linear_API/
├── create_linear_issue.py  # Core API functions
├── issue_helper.py          # Simplified interface
├── requirements.txt         # Python dependencies
├── venv/                    # Virtual environment (not in git)
├── README.md               # This file
└── .gitignore              # Excludes sensitive files
```

### Available Functions

See `create_linear_issue.py` for full API:
- `create_issue()` - Create an issue with all options
- `update_issue()` - Update existing issue fields
- `create_comment()` - Add comments to issues
- `update_comment()` - Update existing comments (requires comment UUID)
- `create_issue_relation()` - Link issues together
- `get_user_id()` - Look up user by email
- `get_label_ids()` - Look up labels by name

See `issue_helper.py` for simplified helpers:
- `create_issue_from_spec()` - Create issue from dictionary
- `update_issue_from_spec()` - Update issue from dictionary
- `add_comment()` - Add comment to issue

### Running Tests

The scripts are designed to be used through AI assistants, but you can test directly:

```bash
source venv/bin/activate
python3 issue_helper.py
```

## Contributing

### Development Workflow

**Important:** To keep the codebase stable and working for everyone, please follow this workflow:

1. **Never commit directly to `main`**
2. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Test your changes** locally with your AI assistant
4. **Push your branch** to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a Pull Request** on GitHub
6. **Get review** from at least one other team member
7. **Merge** after approval

### Branch Naming Convention

Use descriptive branch names with these prefixes:

- `feature/` - New features (e.g., `feature/add-comments-api`)
- `fix/` - Bug fixes (e.g., `fix/update-mutation-bug`)
- `docs/` - Documentation updates (e.g., `docs/update-setup-guide`)
- `refactor/` - Code improvements (e.g., `refactor/simplify-auth`)

### Before Committing

✓ Test your changes work with your AI assistant
✓ Don't commit sensitive data (API keys, `.env` files, credentials)
✓ Update README if you change functionality or add features
✓ Make sure `.gitignore` is properly excluding sensitive files

### Branch Protection

The `main` branch is protected:
- Direct commits are blocked
- Pull requests require 1 approval
- This prevents accidental breaking changes

### Why This Matters

Multiple team members use this tool with different AI assistants (Claude Code, Cursor, Codex). The review process ensures changes work for everyone and don't introduce breaking changes.

## References

- [Linear API Documentation](https://developers.linear.app/docs/graphql/working-with-the-graphql-api)
- [Linear GraphQL Schema](https://studio.apollographql.com/public/Linear-API/variant/current/home)
- [1Password CLI Documentation](https://developer.1password.com/docs/cli/)

## Support

For issues or questions:
- Check the Troubleshooting section above
- Ask in the Luminous team chat
- Review Linear's API documentation
- Open an issue on GitHub

---

**Last Updated:** November 7, 2025
