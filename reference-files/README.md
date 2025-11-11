# Reference Files from Luminous API Integrations

**Purpose:** These files show the established patterns for Luminous API integrations.

**Note:** The main repositories are private, so key files are provided here for reference during google-sheets-api implementation.

---

## Directory Structure

```
reference-files/
├── linear_API/
│   ├── create_linear_issue.py    # Authentication pattern, error handling
│   ├── issue_helper.py            # AI-friendly spec dictionary pattern
│   ├── README.md                  # Documentation style
│   └── requirements.txt           # Dependencies
└── github_api/
    ├── pyproject.toml             # ruff/mypy configuration (USE THIS)
    ├── requirements-dev.txt       # Dev dependencies pattern
    ├── create_github_issue.py     # Custom exceptions, error handling
    ├── github_issue_helper.py     # Spec dictionary implementation
    └── README.md                  # Documentation structure
```

---

## Key Patterns to Follow

### 1. Authentication (from linear_API/create_linear_issue.py)

**Pattern: Try multiple credential sources**

```python
def get_api_key() -> Optional[str]:
    """Get API key from various sources, in order of preference"""

    # 1. Environment variable (might be file path or 1Password reference)
    if env_value := os.getenv('LINEAR_API_KEY'):
        if env_value.startswith('op://'):
            return get_from_1password(env_value)
        return env_value

    # 2. macOS Keychain
    if key := get_from_keychain('Linear'):
        return key

    # 3. 1Password CLI (default item)
    if key := get_from_1password('op://Personal/Linear/credential'):
        return key

    return None

def get_from_keychain(item_name: str) -> Optional[str]:
    """Get value from macOS Keychain"""
    try:
        result = subprocess.run(
            ['security', 'find-generic-password',
             '-s', item_name, '-w'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_from_1password(item_path: str) -> Optional[str]:
    """Get value from 1Password using op CLI"""
    try:
        result = subprocess.run(
            ['op', 'read', item_path],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
```

**Adapt this for Google Sheets:**
- Environment variable: `GOOGLE_SHEETS_SERVICE_ACCOUNT`
- Keychain item: "Google Sheets Service Account"
- 1Password path: `op://Personal/Google Sheets Service Account/credential`
- Value: JSON content or path to JSON file

---

### 2. Error Handling (from github_api/create_github_issue.py)

**Pattern: Custom exception hierarchy + return dicts**

```python
# Custom Exceptions
class GoogleSheetsError(Exception):
    """Base exception for Google Sheets related errors"""
    pass

class GoogleSheetsAuthError(GoogleSheetsError):
    """Raised when authentication fails"""
    pass

class GoogleSheetsAPIError(GoogleSheetsError):
    """Raised when API call fails"""
    pass

class GoogleSheetsNotFoundError(GoogleSheetsError):
    """Raised when spreadsheet/sheet not found"""
    pass

# Functions return dicts for AI-friendly usage
def read_sheet(...) -> dict:
    try:
        # ... do work ...
        return {
            "success": True,
            "data": data,
            "rows": len(data)
        }
    except AuthError:
        return {
            "success": False,
            "error": "Authentication failed. Run: ..."
        }
    except APIError as e:
        return {
            "success": False,
            "error": str(e)
        }
```

---

### 3. AI-Friendly Helper (from github_api/github_issue_helper.py)

**Pattern: Specification dictionary with validation**

```python
def sheets_from_spec(spec: dict) -> dict:
    """
    Execute Google Sheets operation from specification dictionary

    Expected spec format:
    {
        "spreadsheet_id": str,    # Required
        "sheet_name": str,        # Required
        "operation": str,         # Required: "read", "append", "update"
        "values": list,           # For write operations
        "range_notation": str,    # Optional
        "return_format": str      # Optional: "lists" or "dicts"
    }
    """

    # Validate required fields
    required = ["spreadsheet_id", "sheet_name", "operation"]
    missing = [f for f in required if f not in spec]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # Route to appropriate function
    operation = spec["operation"]

    if operation == "read":
        if spec.get("return_format") == "dicts":
            return read_sheet_as_dicts(...)
        return read_sheet(...)

    elif operation == "append":
        return append_row(...)

    elif operation == "update":
        return update_range(...)

    else:
        raise ValueError(f"Unknown operation: {operation}")
```

---

### 4. Configuration (from github_api/pyproject.toml)

**Use this exact pyproject.toml structure:**

```toml
[project]
name = "google-sheets-api-integration"
version = "1.0.0"
description = "Python library for Google Sheets integration"
requires-python = ">=3.7"

[tool.ruff]
line-length = 100
target-version = "py37"

exclude = [
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "*.egg-info",
]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort (import sorting)
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "SIM", # flake8-simplify
]

ignore = []

[tool.ruff.lint.isort]
known-first-party = ["google_sheets_integration", "sheets_helper"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
]
```

---

### 5. Documentation Style (from both READMEs)

**Pattern: Clear, practical, example-driven**

Structure:
1. Brief description (1-2 sentences)
2. Prerequisites
3. Installation
4. Authentication setup (detailed, multi-method)
5. Usage examples (copy-paste ready)
6. Troubleshooting
7. Development setup (for contributors)

**Tone:**
- Direct, practical
- British English spelling
- No marketing fluff
- Actionable commands (not "you should", but "run this:")

---

## Implementation Checklist

Using these references, implement:

- [ ] Authentication following linear_API pattern (4 methods)
- [ ] Error handling following github_api pattern (custom exceptions + dicts)
- [ ] Helper function following github_issue_helper pattern (spec dict)
- [ ] Configuration following github_api pyproject.toml exactly
- [ ] Documentation following README patterns
- [ ] Testing following github_api test structure

---

## Questions?

If the reference files don't answer your question, create an issue in the google-sheets-api-integration repository.

— Guido
