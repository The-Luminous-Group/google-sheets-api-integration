# Google Sheets API Integration - Implementation Specification

**Project:** google-sheets-api-integration
**Purpose:** Python library for reading from and writing to Google Sheets programmatically
**Target Repository:** `https://github.com/The-Luminous-Group/google-sheets-api-integration`
**Implementation Agent:** Claude Code Web
**Specification Author:** Guido (Luminous CTO-in-Residence)
**Date:** 11 November 2025

---

## Overview

Create a Python library that enables both humans and AI coding assistants to interact with Google Sheets via the Google Sheets API v4. This follows the established Luminous pattern for API integrations (similar to `linear_API` and `github_api`).

**Core Principle:** Make it easy for AI assistants to read qualification data from spreadsheets and write analysis results back.

---

## Primary Use Cases

### 1. Read Qualification Data
AI assistants need to read company qualification data from a Google Sheet to inform outreach decisions.

**Example:** Read FRL scores, journey stage, and notes from "Lead Generation Tracker" spreadsheet.

### 2. Write Analysis Results
After processing (e.g., email extraction, company research), write structured results back to a tracking spreadsheet.

**Example:** Write extraction results (company name, contacts, URLs) to a new row in the tracker.

### 3. Update Status Fields
Mark records as "Researched", "Outreach Sent", "Response Received" etc.

**Example:** Update status column when outreach email is sent.

---

## Technical Requirements

### Authentication

Support multiple authentication methods (ordered by security preference):

#### Option 1: Service Account (Recommended for automation)
- Use Google Service Account JSON key file
- Store credential path in environment variable or 1Password
- No interactive OAuth flow required
- Best for unattended AI agent workflows

#### Option 2: OAuth 2.0 User Credentials
- Interactive browser-based OAuth flow
- Store refresh token securely
- Good for human-initiated workflows

**Environment Variables:**
```bash
export GOOGLE_SHEETS_SERVICE_ACCOUNT="/path/to/service-account.json"
# OR
export GOOGLE_SHEETS_CREDENTIALS="/path/to/oauth-credentials.json"
```

**1Password Integration:**
```bash
export GOOGLE_SHEETS_SERVICE_ACCOUNT="op://Personal/Google Sheets Service Account/credential"
```

### Core Functionality

#### 1. Read Operations

**Read entire sheet:**
```python
from google_sheets_integration import read_sheet

# Read all data from a sheet
data = read_sheet(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    range_notation="A1:Z100"  # Optional, defaults to entire sheet
)
# Returns: List[List[str]] (2D array of cell values)
```

**Read specific range:**
```python
# Read just company names and status (columns A and E)
data = read_sheet(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    range_notation="A2:E100"  # Skip header row
)
```

**Read with headers (dict format):**
```python
from google_sheets_integration import read_sheet_as_dicts

# Returns list of dicts with column headers as keys
records = read_sheet_as_dicts(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker"
)
# Returns: [{"Company": "Acme Corp", "Status": "Qualified", ...}, ...]
```

#### 2. Write Operations

**Append new row:**
```python
from google_sheets_integration import append_row

append_row(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    values=["Acme Corp", "John Doe", "CEO", "Qualified", "2025-11-11"]
)
```

**Append multiple rows:**
```python
from google_sheets_integration import append_rows

append_rows(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    rows=[
        ["Acme Corp", "John Doe", "CEO"],
        ["Beta Inc", "Jane Smith", "CTO"]
    ]
)
```

**Update specific cell/range:**
```python
from google_sheets_integration import update_range

update_range(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    range_notation="E5",  # Status column, row 5
    values=[["Outreach Sent"]]
)
```

**Update multiple cells:**
```python
update_range(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    range_notation="A2:C4",
    values=[
        ["Company A", "Contact A", "Status A"],
        ["Company B", "Contact B", "Status B"],
        ["Company C", "Contact C", "Status C"]
    ]
)
```

#### 3. Helper Functions

**Find row by value:**
```python
from google_sheets_integration import find_row

# Find row where column A contains "Acme Corp"
row_index = find_row(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    column="A",
    value="Acme Corp"
)
# Returns: int (1-indexed row number) or None
```

**Helper for AI assistants:**
```python
from google_sheets_integration import update_from_spec

# AI-friendly specification dictionary
spec = {
    "spreadsheet_id": "1ABC...XYZ",
    "sheet_name": "Lead Tracker",
    "operation": "append_row",
    "values": ["Acme Corp", "John Doe", "CEO", "Qualified"]
}

result = update_from_spec(spec)
# Returns: {"success": True, "updated_range": "Lead Tracker!A100", ...}
```

---

## Project Structure

```
google-sheets-api/
├── README.md                          # Setup, authentication, usage examples
├── pyproject.toml                     # Project metadata, ruff/mypy config
├── requirements.txt                   # google-auth, google-api-python-client
├── requirements-dev.txt               # pytest, ruff, mypy, pytest-cov
├── google_sheets_integration.py       # Core API functions
├── sheets_helper.py                   # AI-friendly helper functions
├── examples/
│   ├── read_tracker.py               # Example: Read qualification data
│   ├── write_results.py              # Example: Write analysis results
│   └── update_status.py              # Example: Update status field
├── docs/
│   ├── setup.md                      # Installation and authentication setup
│   ├── service-account-setup.md      # How to create Google Service Account
│   ├── troubleshooting.md            # Common issues and solutions
│   └── technical-debt.md             # Track known issues
└── tests/
    ├── __init__.py
    ├── test_google_sheets_integration.py
    └── test_sheets_helper.py
```

---

## Dependencies

```txt
# requirements.txt
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-api-python-client>=2.100.0
```

```txt
# requirements-dev.txt
pytest>=7.0.0
pytest-cov>=4.0.0
ruff>=0.1.0
mypy>=1.5.0
```

---

## Code Quality Standards

### Linting & Type Checking
- Use `ruff` for linting (same config as other Luminous repos)
- Use `mypy` for type checking with strict settings
- All functions must have type hints
- All public functions must have docstrings

### Testing
- Comprehensive pytest test suite
- Mock Google API calls (no real API calls in tests)
- Test authentication flows
- Test read/write operations
- Test error handling
- Aim for >80% coverage

### Error Handling
- Custom exception hierarchy:
  - `GoogleSheetsError` (base)
  - `GoogleSheetsAuthError` (authentication failures)
  - `GoogleSheetsAPIError` (API call failures)
  - `GoogleSheetsNotFoundError` (spreadsheet/sheet not found)
- Return dicts with `{"success": bool, "error": str, ...}` for AI-friendly responses
- Raise exceptions for library-style usage

### Documentation
- Comprehensive README with:
  - Installation instructions
  - Authentication setup (both service account and OAuth)
  - Usage examples for common operations
  - Troubleshooting section
- `docs/service-account-setup.md` with step-by-step guide:
  - How to create Google Cloud project
  - Enable Google Sheets API
  - Create service account
  - Download JSON key
  - Share spreadsheet with service account email
- `docs/troubleshooting.md` with common issues:
  - Authentication errors
  - Permission errors
  - API quota limits
  - Invalid spreadsheet ID format

---

## Security Considerations

### Credential Storage
- **Never** hardcode credentials
- Support environment variables
- Support 1Password CLI (`op read`)
- Document secure storage best practices
- Add `.env` to `.gitignore`
- Provide `.env.template` example

### API Permissions
- Service account should request minimal scopes:
  - `https://www.googleapis.com/auth/spreadsheets` (read/write)
  - OR `https://www.googleapis.com/auth/spreadsheets.readonly` (read-only)
- Document how to share spreadsheets with service account email

### Error Messages
- Don't leak sensitive information in error messages
- Sanitize file paths in logs
- Be careful with spreadsheet IDs in error output

---

## AI Assistant Integration

### Specification Dictionary Pattern

AI assistants should be able to use a simple dictionary specification:

```python
spec = {
    "spreadsheet_id": "1ABC...XYZ",
    "sheet_name": "Lead Tracker",
    "operation": "append_row",  # or "update_range", "read_sheet"
    "values": ["Company", "Contact", "Status"],
    # Optional fields:
    "range_notation": "A2:C100",
    "return_format": "dicts"  # or "lists"
}

result = execute_from_spec(spec)
```

### Helper Functions

Provide high-level helpers that handle common workflows:

```python
def update_lead_status(spreadsheet_id: str, company_name: str, new_status: str) -> dict:
    """Find row by company name and update status column"""
    pass

def append_extraction_results(spreadsheet_id: str, extraction_data: dict) -> dict:
    """Append email extraction results as new row"""
    pass
```

---

## Example Usage (from README)

### Reading Qualification Data

```python
from google_sheets_integration import read_sheet_as_dicts

# Read all qualified leads
leads = read_sheet_as_dicts(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Qualified Leads"
)

for lead in leads:
    print(f"{lead['Company']} - FRL Score: {lead['FRL Score']}")
```

### Writing Analysis Results

```python
from google_sheets_integration import append_row

# Add extraction results
append_row(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Extraction Results",
    values=[
        "Acme Corp",
        "John Doe",
        "CEO",
        "john.doe@acme.com",
        "https://acme.com",
        "2025-11-11"
    ]
)
```

### Updating Status

```python
from google_sheets_integration import find_row, update_range

# Find company row
row = find_row(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    column="A",
    value="Acme Corp"
)

if row:
    # Update status column (E)
    update_range(
        spreadsheet_id="1ABC...XYZ",
        sheet_name="Lead Tracker",
        range_notation=f"E{row}",
        values=[["Outreach Sent"]]
    )
```

---

## Implementation Phases

### Phase 1: Core Functionality (MVP)
- Service account authentication
- Basic read operations (`read_sheet`, `read_sheet_as_dicts`)
- Basic write operations (`append_row`, `update_range`)
- Error handling with custom exceptions
- README with setup instructions
- Basic test coverage

### Phase 2: Helper Functions
- `find_row()` helper
- `execute_from_spec()` for AI assistants
- Comprehensive examples in `examples/`
- Service account setup documentation

### Phase 3: Polish
- OAuth 2.0 user authentication
- 1Password integration
- Expanded test coverage (>80%)
- Troubleshooting documentation
- Type checking with mypy (all passing)

---

## Success Criteria

**MVP is complete when:**
1. ✅ Service account authentication works
2. ✅ Can read data from Google Sheet
3. ✅ Can write data to Google Sheet
4. ✅ Can update existing cells
5. ✅ Comprehensive README with examples
6. ✅ All tests passing
7. ✅ Ruff and mypy checks passing
8. ✅ Documentation covers authentication setup

**Production-ready when:**
1. ✅ All Phase 1-3 items complete
2. ✅ >80% test coverage
3. ✅ Service account setup guide complete
4. ✅ Troubleshooting documentation complete
5. ✅ Technical debt document exists
6. ✅ Works seamlessly for AI assistants

---

## Notes for Implementation Agent

### Style Consistency
- Follow the patterns established in `linear_API` and `github_api`
- Use the same pyproject.toml structure
- Use the same documentation style
- Use the same error handling patterns

### Don't Reinvent
- Use official `google-api-python-client` library
- Don't write custom OAuth flow - use `google-auth-oauthlib`
- Follow Google's authentication best practices

### Testing Philosophy
- Mock all Google API calls in tests
- Test the interface, not the implementation
- Cover error cases (auth failures, API errors, not found)
- Use pytest fixtures for common test data

### YAGNI (You Aren't Gonna Need It)
- Start simple - don't build features we haven't specified
- Focus on the use cases listed above
- Don't add batch operations until we need them
- Don't add caching until we have performance issues

---

## Questions for Clarification

**Before starting implementation, confirm:**

1. **Authentication preference:** Should we prioritize service account (automation) or OAuth (user)?
   - **Answer:** Service account first (Phase 1), OAuth in Phase 3

2. **Read/write balance:** More focus on reading data or writing data?
   - **Answer:** Equal focus - need both for qualification workflow

3. **Sheet discovery:** Do we need to list available sheets in a spreadsheet?
   - **Answer:** Not for MVP - can add in Phase 3 if needed

4. **Data validation:** Should we validate data types before writing?
   - **Answer:** Basic validation (not None, not empty) but don't over-engineer

---

## Repository Setup Checklist

Before implementation begins, set up repository:

- [ ] Create GitHub repository: `google-sheets-api-integration`
- [ ] Add to The-Luminous-Group organization
- [ ] Enable branch protection on `main`
- [ ] Add standard `.gitignore` (Python, venv, .env, credentials)
- [ ] Add MIT license (or Luminous standard)
- [ ] Create initial README with "Work in Progress" status

---

**End of Specification**

This specification should be handed to Claude Code Web for implementation. All decisions have been made to minimize back-and-forth. Implementation can begin immediately.
