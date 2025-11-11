# Responses to Claude Code Web Questions

**Date:** 11 November 2025
**From:** Guido (Luminous CTO-in-Residence)

---

## 1. Reference Repositories

**Answer:** Both repositories are public and accessible:

**linear_API:**
- Repository: https://github.com/The-Luminous-Group/linear-api-integration
- Key files to review:
  - `pyproject.toml` - ruff/mypy configuration
  - `create_linear_issue.py` - error handling patterns
  - `issue_helper.py` - AI-friendly helper functions
  - `README.md` - documentation style
  - `tests/test_api_key_sources.py` - testing approach

**github_api:**
- Repository: https://github.com/The-Luminous-Group/github-api-integration
- Key files to review:
  - `pyproject.toml` - project configuration
  - `create_github_issue.py` - error handling with custom exceptions
  - `github_issue_helper.py` - specification dictionary pattern
  - `tests/` - comprehensive test suite (23 tests)
  - `docs/troubleshooting.md` - documentation approach

**Action:** Clone both repositories locally and review their structure before implementing.

---

## 2. Project Structure

**Answer:** Put Python files **directly in the root** of `google-sheets-api-integration/`.

This matches both reference repositories:
- `linear_API` has files in root: `create_linear_issue.py`, `issue_helper.py`
- `github_api` has files in root: `create_github_issue.py`, `github_issue_helper.py`

**Correct structure:**
```
google-sheets-api-integration/
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── google_sheets_integration.py    # ← Root level
├── sheets_helper.py                # ← Root level
├── docs/
│   └── ...
└── tests/
    └── ...
```

**Do NOT create a subdirectory** like `src/google_sheets_integration/`. Keep it simple - files in root.

---

## 3. 1Password Integration

**Answer:** The inconsistency is my error. Here's the clarification:

**Phase 1 should support:**
1. ✅ Service account JSON from file path (environment variable)
2. ✅ Keychain integration (macOS Keychain)
3. ✅ 1Password CLI integration (`op read`)

**Defer to Phase 3:**
- OAuth 2.0 user credentials flow

### Authentication Pattern (Phase 1)

Follow the **exact pattern from linear_API**:

```python
def get_api_key() -> Optional[str]:
    """Get Google Service Account credentials from various sources"""

    # 1. Try environment variable (file path)
    if env_path := os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT'):
        if env_path.startswith('op://'):
            # 1Password reference
            return get_from_1password(env_path)
        else:
            # File path
            return read_service_account_file(env_path)

    # 2. Try macOS Keychain
    if key := get_from_keychain('Google Sheets Service Account'):
        return key

    # 3. Try 1Password CLI (default item name)
    if key := get_from_1password('op://Personal/Google Sheets Service Account/credential'):
        return key

    return None
```

**Reference:** See `linear_API/create_linear_issue.py` lines ~50-150 for the exact authentication pattern.

---

## 4. Scope Confirmation

**Your understanding is INCORRECT.** Phase 1 includes more than you listed.

### Phase 1 Core Functions (Confirmed)

**Read operations:**
- ✅ `read_sheet()` - Read raw 2D list of values
- ✅ `read_sheet_as_dicts()` - Read with headers as dict keys

**Write operations:**
- ✅ `append_row()` - Append single row
- ✅ `append_rows()` - Append multiple rows
- ✅ `update_range()` - Update specific cells

**Helper operations (INCLUDE IN PHASE 1):**
- ✅ `find_row()` - Find row by column value (needed for updates)
- ✅ `execute_from_spec()` or `sheets_from_spec()` - AI-friendly wrapper

**Why these helpers are Phase 1:**
- `find_row()` is essential for updating existing rows (common use case)
- `execute_from_spec()` is the AI-friendly pattern we use everywhere (see `issue_helper.py`)
- Both are simple to implement and don't add significant scope

**Reference:** Check `github_api/github_issue_helper.py` for the `create_issue_from_spec()` pattern. Implement the same for sheets.

---

## 5. Additional Requirement: Keychain + 1Password Support

**User requirement:** Must support both Keychain AND 1Password (same as linear_API).

### Implementation Pattern

**Credential storage options (in priority order):**

1. **Environment variable with file path:**
   ```bash
   export GOOGLE_SHEETS_SERVICE_ACCOUNT="/path/to/service-account.json"
   ```

2. **Environment variable with 1Password reference:**
   ```bash
   export GOOGLE_SHEETS_SERVICE_ACCOUNT="op://Personal/Google Sheets/credential"
   ```

3. **macOS Keychain:**
   - Item name: "Google Sheets Service Account"
   - Account name: "service-account"
   - Value: JSON content or file path

4. **1Password CLI (default):**
   - Item path: `op://Personal/Google Sheets Service Account/credential`
   - Field: "credential" contains JSON or file path

### Helper Functions Required

```python
def get_from_keychain(item_name: str) -> Optional[str]:
    """Get credentials from macOS Keychain"""
    # See linear_API for implementation

def get_from_1password(item_path: str) -> Optional[str]:
    """Get credentials from 1Password using op CLI"""
    # See linear_API for implementation

def read_service_account_file(path: str) -> dict:
    """Read and parse service account JSON file"""
    # Read JSON, return dict

def get_service_account_credentials() -> dict:
    """Try all credential sources in order"""
    # Main function that tries all methods
```

**Critical:** Study `linear_API/create_linear_issue.py` authentication section (lines ~50-150). Replicate the exact pattern for Google Sheets.

---

## Summary of Phase 1 Scope (CORRECTED)

### Authentication (4 methods)
1. ✅ File path from environment variable
2. ✅ 1Password reference from environment variable
3. ✅ macOS Keychain
4. ✅ 1Password CLI default

### Core Functions (8 functions)
1. ✅ `read_sheet()`
2. ✅ `read_sheet_as_dicts()`
3. ✅ `append_row()`
4. ✅ `append_rows()`
5. ✅ `update_range()`
6. ✅ `find_row()`
7. ✅ `execute_from_spec()` or `sheets_from_spec()`
8. ✅ `get_service_account_credentials()` (internal)

### Testing
- Mock Google API calls
- Test all authentication methods
- Test all core functions
- Test error cases

### Documentation
- README with all authentication methods
- `docs/setup.md` - Installation
- `docs/service-account-setup.md` - Google Cloud setup
- `docs/troubleshooting.md` - Common issues

---

## Action Items for Claude Code Web

1. **Clone reference repositories:**
   ```bash
   git clone https://github.com/The-Luminous-Group/linear-api-integration.git
   git clone https://github.com/The-Luminous-Group/github-api-integration.git
   ```

2. **Study authentication pattern:**
   - Read `linear_API/create_linear_issue.py` (authentication section)
   - Replicate for Google Sheets with service account JSON

3. **Study helper pattern:**
   - Read `github_api/github_issue_helper.py`
   - Implement `sheets_from_spec()` following same pattern

4. **Study testing approach:**
   - Read `github_api/tests/` (23 test cases)
   - Replicate mocking approach for Google Sheets API

5. **Implement Phase 1:**
   - Files in root directory
   - All 8 functions listed above
   - All 4 authentication methods
   - Comprehensive tests

6. **Verify before PR:**
   ```bash
   pytest tests/          # All tests pass
   ruff check .           # No linting errors
   mypy .                 # No type errors
   ```

---

## Questions?

If anything is still unclear after reviewing the reference repositories, create an issue in the google-sheets-api-integration repository and tag @barton.

Good luck with implementation!

— Guido
