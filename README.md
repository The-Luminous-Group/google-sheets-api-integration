# Google Sheets API Integration

Python library for reading from and writing to Google Sheets programmatically. Designed to be simple and AI-assistant-friendly.

## Features

- **Service account authentication** (automation-friendly, no browser required)
- **Multiple credential sources** (environment variable, macOS Keychain, 1Password CLI)
- **Simple read operations** (`read_sheet`, `read_sheet_as_dicts`)
- **Simple write operations** (`append_row`, `append_rows`, `update_range`)
- **Helper functions** (`find_row`, `sheets_from_spec`)
- **AI-friendly** spec dictionary pattern for easy integration
- **Comprehensive error handling** with custom exceptions
- **Type hints** and full test coverage

## Prerequisites

- Python 3.7+
- Google Cloud project with Sheets API enabled
- Service account credentials (see [Service Account Setup](docs/service-account-setup.md))

## Installation

**Recommended:** Use a virtual environment to avoid dependency conflicts:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

For development (includes testing and linting tools):
```bash
pip install -r requirements-dev.txt
```

**Note:** Always activate the virtual environment before using the library or running scripts.

## Quick Start

### 1. Set up authentication

Export your service account credentials (the code now also accepts raw JSON via `GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON`):

```bash
# Option 1: File path
export GOOGLE_SHEETS_SERVICE_ACCOUNT="/path/to/service-account.json"

# Option 2: 1Password reference
export GOOGLE_SHEETS_SERVICE_ACCOUNT="op://Personal/Google Sheets Service Account/credential"

# Option 3: Paste the JSON directly (useful in sandboxed environments)
export GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON="$(op read 'op://Personal/Google Sheets Service Account/credential')"
```

### 2. Read data from a sheet

```python
from google_sheets_integration import read_sheet_as_dicts

# Read data as list of dictionaries
result = read_sheet_as_dicts(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker"
)

if result["success"]:
    for row in result["data"]:
        print(f"Company: {row['Company']}, Status: {row['Status']}")
```

### 3. Write data to a sheet

```python
from google_sheets_integration import append_row

# Append a new row
result = append_row(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    values=["Acme Corp", "John Doe", "CEO", "Qualified", "2025-11-11"]
)

if result["success"]:
    print(f"Row added: {result['updated_range']}")
```

## Authentication Methods

The library tries multiple credential sources in order:

### 1. Environment Variable (File Path)

```bash
export GOOGLE_SHEETS_SERVICE_ACCOUNT="/path/to/service-account.json"
```

### 2. Environment Variable (1Password Reference)

```bash
export GOOGLE_SHEETS_SERVICE_ACCOUNT="op://Personal/Google Sheets/credential"
```

### 3. macOS Keychain

Store your service account JSON in Keychain:
- Service name: "Google Sheets Service Account"
- Account name: your username
- Value: path to JSON file or JSON content

### 4. 1Password CLI (Default Path)

Store your credentials in 1Password at:
```
op://Personal/Google Sheets Service Account/credential
```

### Custom Source Order

Override the lookup order:
```bash
export GOOGLE_SHEETS_CREDENTIAL_SOURCES="env,1password,keychain"
```

## Core Functions

### Read Operations

#### `read_sheet()`

Read data as a 2D list:

```python
from google_sheets_integration import read_sheet

result = read_sheet(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    range_notation="A1:E100"  # Optional
)

if result["success"]:
    data = result["data"]  # List[List[str]]
    print(f"Read {result['rows']} rows")
```

#### `read_sheet_as_dicts()`

Read data with headers as dict keys:

```python
from google_sheets_integration import read_sheet_as_dicts

result = read_sheet_as_dicts(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker"
)

if result["success"]:
    for row in result["data"]:
        print(f"{row['Company']} - {row['Status']}")
```

### Write Operations

#### `append_row()`

Append a single row:

```python
from google_sheets_integration import append_row

result = append_row(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    values=["Acme Corp", "John Doe", "CEO"]
)
```

#### `append_rows()`

Append multiple rows:

```python
from google_sheets_integration import append_rows

result = append_rows(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    rows=[
        ["Company A", "Contact A", "Status A"],
        ["Company B", "Contact B", "Status B"]
    ]
)
```

#### `update_range()`

Update specific cells:

```python
from google_sheets_integration import update_range

# Update single cell
result = update_range(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    range_notation="E5",
    values=[["Outreach Sent"]]
)

# Update multiple cells
result = update_range(
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

### Helper Functions

#### `find_row()`

Find row number by column value:

```python
from google_sheets_integration import find_row

result = find_row(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    column="A",
    value="Acme Corp"
)

if result["success"] and result["row"]:
    print(f"Found at row {result['row']}")
```

#### `sheets_from_spec()` (AI-Friendly)

Execute operations using a specification dictionary:

```python
from sheets_helper import sheets_from_spec

# Read as dictionaries
result = sheets_from_spec({
    "spreadsheet_id": "1ABC...XYZ",
    "sheet_name": "Lead Tracker",
    "operation": "read_dicts"
})

# Append row
result = sheets_from_spec({
    "spreadsheet_id": "1ABC...XYZ",
    "sheet_name": "Lead Tracker",
    "operation": "append",
    "values": ["Company", "Contact", "Status"]
})

# Update range
result = sheets_from_spec({
    "spreadsheet_id": "1ABC...XYZ",
    "sheet_name": "Lead Tracker",
    "operation": "update",
    "range_notation": "E5",
    "values": [["New Status"]]
})

# Find row
result = sheets_from_spec({
    "spreadsheet_id": "1ABC...XYZ",
    "sheet_name": "Lead Tracker",
    "operation": "find",
    "column": "A",
    "value": "Acme Corp"
})
```

## Error Handling

All functions return dictionaries with `success` boolean:

```python
result = read_sheet("1ABC...XYZ", "Sheet1")

if result["success"]:
    data = result["data"]
    # Process data
else:
    print(f"Error: {result['error']}")
```

### Custom Exceptions

For library-style usage, the following exceptions may be raised:

- `GoogleSheetsError` - Base exception
- `GoogleSheetsAuthError` - Authentication failures
- `GoogleSheetsAPIError` - API call failures
- `GoogleSheetsNotFoundError` - Spreadsheet/sheet not found

## Common Use Cases

### Read qualification data

```python
from google_sheets_integration import read_sheet_as_dicts

leads = read_sheet_as_dicts(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Qualified Leads"
)

if leads["success"]:
    for lead in leads["data"]:
        frl_score = lead.get("FRL Score", "N/A")
        print(f"{lead['Company']} - FRL Score: {frl_score}")
```

### Write analysis results

```python
from google_sheets_integration import append_row

result = append_row(
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

### Update status field

```python
from google_sheets_integration import find_row, update_range

# Find the company row
row_result = find_row(
    spreadsheet_id="1ABC...XYZ",
    sheet_name="Lead Tracker",
    column="A",
    value="Acme Corp"
)

if row_result["success"] and row_result["row"]:
    row_num = row_result["row"]

    # Update status column (E)
    update_result = update_range(
        spreadsheet_id="1ABC...XYZ",
        sheet_name="Lead Tracker",
        range_notation=f"E{row_num}",
        values=[["Outreach Sent"]]
    )
```

## Sharing Spreadsheets

Your service account must have access to the spreadsheet:

1. Open your service account JSON file
2. Copy the `client_email` (looks like `name@project.iam.gserviceaccount.com`)
3. Share your Google Sheet with this email address
4. Grant "Editor" permission

See [Service Account Setup](docs/service-account-setup.md) for detailed instructions.

## Troubleshooting

See [Troubleshooting Guide](docs/troubleshooting.md) for common issues and solutions.

### Quick fixes

**"Unable to retrieve credentials"**
- Check that `GOOGLE_SHEETS_SERVICE_ACCOUNT` is set
- Verify file path exists and is readable
- Ensure 1Password CLI is installed (`op --version`)

**"Spreadsheet not found"**
- Verify spreadsheet ID is correct (from URL)
- Ensure service account has access to spreadsheet
- Check sheet name matches exactly (case-sensitive)

**"Authentication failed"**
- Verify service account JSON is valid
- Check that Sheets API is enabled in Google Cloud Console
- Ensure service account has correct permissions

## Development

### Running Tests

```bash
pytest tests/
```

### Linting

```bash
ruff check .
```

### Type Checking

```bash
mypy .
```

### Running All Checks

```bash
pytest tests/ && ruff check . && mypy .
```

## Documentation

- [Setup Guide](docs/setup.md) - Installation and setup instructions
- [Service Account Setup](docs/service-account-setup.md) - Creating service account in Google Cloud
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- [Luminous Lead Generation System Spreadsheet Guide](https://github.com/The-Luminous-Group/lead-generation/blob/main/docs/google-sheets-integration.md) - Complete guide to using this library with the Luminous Lead Generation spreadsheet (spreadsheet structure, FRL scoring, workflow examples)

## License

MIT

## Contributing

Contributions welcome! Please ensure:
- All tests pass (`pytest tests/`)
- Code passes linting (`ruff check .`)
- Code passes type checking (`mypy .`)
- New features include tests and documentation
