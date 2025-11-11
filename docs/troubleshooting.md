# Troubleshooting Guide

Common issues and solutions for Google Sheets API integration.

## Authentication Errors

### "Unable to retrieve Google Sheets service account credentials"

**Symptoms:**
- `GoogleSheetsAuthError` raised
- Error message lists tried sources

**Common Causes:**
1. Environment variable not set
2. File path incorrect
3. 1Password CLI not installed or not authenticated
4. Keychain item doesn't exist

**Solutions:**

```bash
# Check environment variable
echo $GOOGLE_SHEETS_SERVICE_ACCOUNT

# If not set, set it
export GOOGLE_SHEETS_SERVICE_ACCOUNT="/path/to/service-account.json"

# Verify file exists
ls -la /path/to/service-account.json

# Check 1Password CLI
op --version
op whoami

# Check Keychain (macOS)
security find-generic-password -s "Google Sheets Service Account" -w
```

### "Service account file not found"

**Symptoms:**
- Error message includes file path
- File path is set but file doesn't exist

**Solutions:**

```bash
# Verify path in environment variable
echo $GOOGLE_SHEETS_SERVICE_ACCOUNT

# Check if file exists
ls -la $GOOGLE_SHEETS_SERVICE_ACCOUNT

# Check current directory
ls -la service-account.json

# Move file to expected location
mv ~/Downloads/service-account-*.json ~/.config/google/sheets-service-account.json
export GOOGLE_SHEETS_SERVICE_ACCOUNT="$HOME/.config/google/sheets-service-account.json"
```

### "Failed to load service account credentials"

**Symptoms:**
- JSON parsing error
- Invalid format error

**Solutions:**

```bash
# Validate JSON format
python3 -m json.tool /path/to/service-account.json

# Check file isn't empty
cat /path/to/service-account.json

# Check file permissions
ls -la /path/to/service-account.json

# Should be readable: chmod 600 if needed
chmod 600 /path/to/service-account.json
```

### "1Password reference failed"

**Symptoms:**
- Error reading from `op://...` path
- 1Password CLI errors

**Solutions:**

```bash
# Check 1Password CLI is installed
op --version

# Install if needed (macOS)
brew install 1password-cli

# Authenticate
op signin

# Verify item exists
op item get "Google Sheets Service Account" --vault Personal

# Test reading the credential
op read "op://Personal/Google Sheets Service Account/credential"
```

## API Errors

### "Spreadsheet or sheet not found"

**Symptoms:**
- HTTP 404 error
- Error message mentions spreadsheet ID

**Solutions:**

1. **Verify Spreadsheet ID**
   - Open Google Sheet in browser
   - URL format: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`
   - Copy the ID between `/d/` and `/edit`
   - Ensure no extra characters or spaces

2. **Check Sheet Name**
   ```python
   # Sheet names are case-sensitive
   # ✗ Wrong: "sheet1"
   # ✓ Correct: "Sheet1"
   ```

3. **Verify Sharing**
   - Open service account JSON
   - Find `client_email` value
   - Open Google Sheet
   - Click "Share"
   - Ensure service account email is in the list with Editor/Viewer access

### "The caller does not have permission"

**Symptoms:**
- HTTP 403 error
- Permission denied message

**Solutions:**

1. **Share Sheet with Service Account**
   ```bash
   # Get service account email from JSON
   cat /path/to/service-account.json | grep client_email
   ```
   - Copy the email address
   - Open Google Sheet
   - Click "Share"
   - Add service account email
   - Grant Editor permission
   - Click "Send"

2. **Check API is Enabled**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Select your project
   - Go to "APIs & Services" > "Enabled APIs"
   - Verify "Google Sheets API" is listed
   - If not, enable it in Library

3. **Verify Service Account Credentials**
   ```python
   from google_sheets_integration import get_service_account_credentials

   creds = get_service_account_credentials()
   print(f"Service account email: {creds.service_account_email}")
   ```

### "API key not valid"

**Symptoms:**
- HTTP 400 error
- Invalid API key message

**Solutions:**

1. **Check Credentials Format**
   - Service account JSON should have these fields:
     - `type`: "service_account"
     - `project_id`
     - `private_key_id`
     - `private_key`
     - `client_email`

2. **Regenerate Key**
   - Go to [Google Cloud Console](https://console.cloud.google.com/iam-admin/serviceaccounts)
   - Select service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Select JSON format
   - Download and use new key

### "Quota exceeded"

**Symptoms:**
- HTTP 429 error
- Rate limit exceeded message

**Solutions:**

1. **Check Quota Usage**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Navigate to "IAM & Admin" > "Quotas"
   - Search for "Sheets API"
   - Check current usage

2. **Implement Rate Limiting**
   ```python
   import time

   # Add delay between requests
   for row_data in data:
       result = append_row(spreadsheet_id, sheet_name, row_data)
       time.sleep(0.1)  # 100ms delay
   ```

3. **Request Quota Increase**
   - In Quotas page, select "Sheets API Read/Write"
   - Click "Edit Quotas"
   - Enter justification
   - Submit request

## Operation Errors

### "No data returned" (empty sheet)

**Symptoms:**
- `result["success"]` is True
- `result["rows"]` is 0
- `result["data"]` is empty list

**Common Causes:**
1. Sheet is actually empty
2. Range notation incorrect
3. Data below specified range

**Solutions:**

```python
# Read entire sheet (no range)
result = read_sheet(spreadsheet_id, sheet_name)

# Check if any data exists
if result["success"]:
    if result["rows"] == 0:
        print("Sheet is empty or range has no data")
    else:
        print(f"Found {result['rows']} rows")

# Try different range
result = read_sheet(spreadsheet_id, sheet_name, "A:Z")
```

### "Find row returns None"

**Symptoms:**
- `find_row()` succeeds but returns `row: None`
- Value exists in sheet but not found

**Common Causes:**
1. Case sensitivity
2. Extra whitespace
3. Different column
4. Value in excluded range

**Solutions:**

```python
# Check for exact match (case-sensitive)
result = find_row(spreadsheet_id, sheet_name, "A", "Acme Corp")

# Search might fail if actual value is:
# - "acme corp" (lowercase)
# - "Acme Corp " (trailing space)
# - "Acme  Corp" (double space)

# Read column to debug
data = read_sheet(spreadsheet_id, sheet_name, "A:A")
if data["success"]:
    for idx, row in enumerate(data["data"], 1):
        print(f"Row {idx}: '{row[0] if row else ''}'")
```

### "Update didn't change anything"

**Symptoms:**
- `update_range()` returns success
- Sheet looks unchanged

**Common Causes:**
1. Incorrect range notation
2. Sheet name mismatch
3. Caching in browser

**Solutions:**

```python
# Verify range notation
# Single cell: "E5"
# Range: "A2:C4"
# Column: "A:A"
# Row: "5:5"

# Check result details
result = update_range(spreadsheet_id, sheet_name, "E5", [["New Value"]])
if result["success"]:
    print(f"Updated: {result['updated_range']}")
    print(f"Cells: {result['updated_cells']}")

# Refresh Google Sheets in browser (Cmd+R / Ctrl+R)

# Read back to verify
verify = read_sheet(spreadsheet_id, sheet_name, "E5")
print(f"Current value: {verify['data']}")
```

## Import Errors

### "No module named 'google'"

**Symptoms:**
- Import error when using the library
- Missing Google API dependencies

**Solutions:**

```bash
# Install requirements
pip install -r requirements.txt

# Or install individually
pip install google-auth google-auth-oauthlib google-api-python-client

# Verify installation
python3 -c "import googleapiclient; print('✓ Installed')"
```

### "No module named 'google_sheets_integration'"

**Symptoms:**
- Cannot import the library
- Module not found error

**Solutions:**

```bash
# Ensure you're in the correct directory
cd /path/to/google-sheets-api-integration

# Verify files exist
ls -la google_sheets_integration.py

# Run from same directory or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/google-sheets-api-integration"

# Or install in development mode
pip install -e .
```

## macOS Specific Issues

### "security: command not found"

**Symptoms:**
- Keychain operations fail
- Command not found error

**Solution:**
- The `security` command is macOS-only
- Use environment variable method on other operating systems
- Or use 1Password CLI (cross-platform)

### "User interaction is not allowed"

**Symptoms:**
- Keychain access denied
- Can't retrieve password programmatically

**Solutions:**

```bash
# Grant Terminal/iTerm access to Keychain
# System Preferences > Security & Privacy > Privacy > Automation
# Enable terminal application

# Or store with "always allow" flag
security add-generic-password \
  -s "Google Sheets Service Account" \
  -a "$USER" \
  -w "/path/to/creds.json" \
  -T ""  # Allow all applications
```

## Debugging Tips

### Enable Verbose Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Run your operations
result = read_sheet(spreadsheet_id, sheet_name)
```

### Test Authentication Separately

```python
from google_sheets_integration import get_service_account_credentials

try:
    creds = get_service_account_credentials()
    print(f"✓ Credentials loaded")
    print(f"  Email: {creds.service_account_email}")
    print(f"  Project: {creds.project_id}")
except Exception as e:
    print(f"✗ Authentication failed")
    print(f"  Error: {e}")
```

### Verify Sheet Access

```python
# Test with a simple read
result = read_sheet(spreadsheet_id, sheet_name, "A1:A1")

if result["success"]:
    print("✓ Can access sheet")
else:
    print(f"✗ Cannot access sheet: {result['error']}")
```

### Check Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Check "APIs & Services" > "Dashboard" for:
   - API traffic
   - Error rates
   - Quota usage

## Getting Help

If you're still stuck:

1. **Check the documentation**
   - [Setup Guide](setup.md)
   - [Service Account Setup](service-account-setup.md)
   - [README](../README.md)

2. **Gather error information**
   ```python
   import traceback

   try:
       result = read_sheet(spreadsheet_id, sheet_name)
       print(result)
   except Exception as e:
       print(traceback.format_exc())
   ```

3. **Create a GitHub issue**
   - Include error message
   - Include relevant code (remove sensitive data)
   - Include Python version: `python3 --version`
   - Include package versions: `pip list | grep google`

4. **Check Google's status**
   - [Google Cloud Status Dashboard](https://status.cloud.google.com)
   - [Google Workspace Status](https://www.google.com/appsstatus/dashboard/)

## Common Error Messages Reference

| Error Message | Likely Cause | Solution |
|--------------|--------------|----------|
| "Unable to retrieve credentials" | Environment not configured | Set `GOOGLE_SHEETS_SERVICE_ACCOUNT` |
| "Spreadsheet not found" | Wrong ID or not shared | Verify ID and share with service account |
| "The caller does not have permission" | Not shared with service account | Share spreadsheet with `client_email` |
| "API has not been used" | Sheets API not enabled | Enable in Cloud Console |
| "Invalid grant" | Service account deleted/disabled | Recreate service account |
| "Quota exceeded" | Rate limit hit | Add delays or request increase |
| "Invalid JSON" | Corrupted credentials file | Re-download from Cloud Console |
