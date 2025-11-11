# Setup Guide

Complete guide to installing and configuring Google Sheets API integration.

## Prerequisites

- Python 3.7 or higher
- pip package manager
- Google Cloud account
- Service account with Sheets API access

## Installation

### 1. Install Python Dependencies

Clone the repository (or install from PyPI when published):

```bash
git clone https://github.com/The-Luminous-Group/google-sheets-api-integration.git
cd google-sheets-api-integration
```

Install required packages:

```bash
pip install -r requirements.txt
```

For development work:

```bash
pip install -r requirements-dev.txt
```

### 2. Verify Installation

Test that modules can be imported:

```python
python3 -c "import google_sheets_integration; print('✓ Installation successful')"
```

## Authentication Setup

You need a Google Service Account to authenticate with the Sheets API.

### Step 1: Create Service Account

See [Service Account Setup Guide](service-account-setup.md) for detailed instructions on:
- Creating a Google Cloud project
- Enabling Sheets API
- Creating a service account
- Downloading credentials JSON

### Step 2: Configure Credentials

Choose one of the following methods:

#### Method 1: Environment Variable (File Path)

Export the path to your service account JSON file:

```bash
export GOOGLE_SHEETS_SERVICE_ACCOUNT="/path/to/service-account.json"
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
echo 'export GOOGLE_SHEETS_SERVICE_ACCOUNT="/path/to/service-account.json"' >> ~/.zshrc
source ~/.zshrc
```

#### Method 2: macOS Keychain

Store credentials in Keychain:

```bash
# Store file path
security add-generic-password \
  -s "Google Sheets Service Account" \
  -a "$USER" \
  -w "/path/to/service-account.json"
```

Or store the JSON content directly:

```bash
# Store JSON content
security add-generic-password \
  -s "Google Sheets Service Account" \
  -a "$USER" \
  -w "$(cat /path/to/service-account.json)"
```

#### Method 3: 1Password CLI

Install 1Password CLI:

```bash
brew install 1password-cli
```

Store credentials in 1Password:
1. Open 1Password
2. Create new item in "Personal" vault
3. Name it "Google Sheets Service Account"
4. Add field named "credential"
5. Paste service account JSON content

Or reference a custom path:

```bash
export GOOGLE_SHEETS_SERVICE_ACCOUNT="op://Personal/MyCustomItem/credential"
```

### Step 3: Share Spreadsheet with Service Account

1. Open your service account JSON file
2. Find the `client_email` field (e.g., `name@project.iam.gserviceaccount.com`)
3. Open your Google Sheet
4. Click "Share"
5. Paste the service account email
6. Grant "Editor" permission
7. Click "Send"

**Important:** Every spreadsheet you want to access must be shared with the service account email.

## Verify Authentication

Test authentication:

```python
from google_sheets_integration import get_service_account_credentials

try:
    credentials = get_service_account_credentials()
    print("✓ Authentication successful")
    print(f"  Service account: {credentials.service_account_email}")
except Exception as e:
    print(f"✗ Authentication failed: {e}")
```

## Configuration Options

### Custom Credential Source Order

Override the default lookup order:

```bash
export GOOGLE_SHEETS_CREDENTIAL_SOURCES="env,1password,keychain"
```

Default order: `env`, `keychain`, `1password`

### Custom 1Password Path

Change the default 1Password item path:

```bash
export GOOGLE_SHEETS_1PASSWORD_PATH="op://Work/Google Sheets/service-account"
```

## Testing the Setup

### Test Reading a Sheet

Create a test script `test_read.py`:

```python
from google_sheets_integration import read_sheet

# Replace with your spreadsheet ID
SPREADSHEET_ID = "1ABC...XYZ"
SHEET_NAME = "Sheet1"

result = read_sheet(SPREADSHEET_ID, SHEET_NAME)

if result["success"]:
    print(f"✓ Successfully read {result['rows']} rows")
    print(f"  Data: {result['data'][:3]}")  # First 3 rows
else:
    print(f"✗ Failed: {result['error']}")
```

Run the test:

```bash
python3 test_read.py
```

### Test Writing to a Sheet

Create a test script `test_write.py`:

```python
from google_sheets_integration import append_row

# Replace with your spreadsheet ID
SPREADSHEET_ID = "1ABC...XYZ"
SHEET_NAME = "Sheet1"

result = append_row(
    SPREADSHEET_ID,
    SHEET_NAME,
    ["Test", "Data", "Row"]
)

if result["success"]:
    print(f"✓ Successfully wrote row: {result['updated_range']}")
else:
    print(f"✗ Failed: {result['error']}")
```

Run the test:

```bash
python3 test_write.py
```

## Development Setup

For contributors working on the library:

### 1. Install Dev Dependencies

```bash
pip install -r requirements-dev.txt
```

### 2. Run Tests

```bash
pytest tests/
```

### 3. Run Linting

```bash
ruff check .
```

### 4. Run Type Checking

```bash
mypy .
```

### 5. Run All Checks

```bash
pytest tests/ && ruff check . && mypy .
```

## Next Steps

- Read the [Service Account Setup](service-account-setup.md) guide
- Review the [Troubleshooting](troubleshooting.md) guide
- Explore usage examples in the main [README](../README.md)

## Getting Help

If you encounter issues:
1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Verify your authentication setup
3. Ensure spreadsheet is shared with service account
4. Create an issue on GitHub with error details
