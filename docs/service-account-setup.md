# Service Account Setup

Step-by-step guide to creating a Google Service Account for Sheets API access.

## Overview

Service accounts are special Google accounts designed for automated processes. They don't require interactive login and are ideal for server-to-server applications.

## Prerequisites

- Google account
- Access to [Google Cloud Console](https://console.cloud.google.com)

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click project dropdown at top
3. Click "New Project"
4. Enter project name (e.g., "Google Sheets Integration")
5. Click "Create"
6. Wait for project creation (usually ~30 seconds)
7. Select the new project from dropdown

## Step 2: Enable Google Sheets API

1. In your project, go to "APIs & Services" > "Library"
   - Or visit: https://console.cloud.google.com/apis/library
2. Search for "Google Sheets API"
3. Click on "Google Sheets API"
4. Click "Enable"
5. Wait for API to be enabled

## Step 3: Create Service Account

1. Go to "APIs & Services" > "Credentials"
   - Or visit: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" dropdown
3. Select "Service Account"
4. Fill in service account details:
   - **Name:** `google-sheets-integration` (or your preference)
   - **Description:** "Service account for Google Sheets API access"
5. Click "Create and Continue"
6. For "Grant this service account access to project":
   - You can skip this (click "Continue")
   - Or select "Editor" role for broader access
7. Click "Continue"
8. For "Grant users access to this service account":
   - Skip this (click "Done")

## Step 4: Create and Download Key

1. In the Credentials page, find your service account in the list
2. Click on the service account name
3. Go to "Keys" tab
4. Click "Add Key" > "Create new key"
5. Select "JSON" format
6. Click "Create"
7. JSON file downloads automatically
8. **Save this file securely** - you cannot download it again

### Important Security Notes

- **Never commit this file to version control**
- Store it in a secure location (e.g., `~/.config/google/`)
- Set restrictive file permissions: `chmod 600 service-account.json`
- Consider using 1Password or similar password manager

## Step 5: Note the Service Account Email

1. Open the downloaded JSON file
2. Find the `client_email` field
3. Copy the email address (format: `name@project-id.iam.gserviceaccount.com`)
4. You'll need this to share spreadsheets

## Step 6: Share Spreadsheets

For each Google Sheet you want to access:

1. Open the Google Sheet in your browser
2. Click "Share" button (top right)
3. Paste the service account email
4. Set permission to "Editor" (or "Viewer" for read-only)
5. Uncheck "Notify people" (service accounts don't receive emails)
6. Click "Share" or "Send"

**Note:** You must do this for every spreadsheet you want to access.

## Step 7: Store Credentials

Choose your preferred storage method:

### Option 1: Environment Variable

```bash
# Create secure directory
mkdir -p ~/.config/google
chmod 700 ~/.config/google

# Move service account file
mv ~/Downloads/service-account-*.json ~/.config/google/sheets-service-account.json
chmod 600 ~/.config/google/sheets-service-account.json

# Add to shell profile
echo 'export GOOGLE_SHEETS_SERVICE_ACCOUNT="$HOME/.config/google/sheets-service-account.json"' >> ~/.zshrc
source ~/.zshrc
```

### Option 2: macOS Keychain

```bash
# Store file path in Keychain
security add-generic-password \
  -s "Google Sheets Service Account" \
  -a "$USER" \
  -w "$HOME/.config/google/sheets-service-account.json"

# Verify it was stored
security find-generic-password -s "Google Sheets Service Account" -w
```

### Option 3: 1Password

1. Install 1Password CLI: `brew install 1password-cli`
2. Open 1Password application
3. Create new item:
   - Vault: "Personal" (or your preference)
   - Type: "Secure Note"
   - Title: "Google Sheets Service Account"
4. Add custom field:
   - Field name: "credential"
   - Field value: Paste entire JSON content from service account file
5. Save item

Set environment variable to reference 1Password:

```bash
export GOOGLE_SHEETS_SERVICE_ACCOUNT="op://Personal/Google Sheets Service Account/credential"
```

## Verify Setup

Test that credentials work:

```python
from google_sheets_integration import get_service_account_credentials

try:
    creds = get_service_account_credentials()
    print(f"✓ Authentication successful")
    print(f"  Service account: {creds.service_account_email}")
except Exception as e:
    print(f"✗ Authentication failed: {e}")
```

## Troubleshooting

### "Unable to retrieve credentials"

**Problem:** Environment variable not set or file not found.

**Solution:**
```bash
# Check environment variable
echo $GOOGLE_SHEETS_SERVICE_ACCOUNT

# Verify file exists
ls -la ~/.config/google/sheets-service-account.json
```

### "Permission denied" when reading credentials file

**Problem:** File permissions too restrictive or file owned by different user.

**Solution:**
```bash
# Fix ownership
sudo chown $USER ~/.config/google/sheets-service-account.json

# Fix permissions
chmod 600 ~/.config/google/sheets-service-account.json
```

### "Sheets API has not been used in project"

**Problem:** Google Sheets API not enabled for project.

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Go to "APIs & Services" > "Library"
4. Search "Google Sheets API"
5. Click "Enable"

### "The caller does not have permission"

**Problem:** Spreadsheet not shared with service account.

**Solution:**
1. Open the JSON file and copy `client_email`
2. Open your Google Sheet
3. Click "Share"
4. Add the service account email with Editor permissions

### "Invalid JSON" error

**Problem:** JSON file corrupted or incomplete.

**Solution:**
1. Verify JSON is valid: `python3 -m json.tool service-account.json`
2. Check file isn't truncated: `tail service-account.json`
3. Re-download key from Google Cloud Console if needed

## Security Best Practices

### 1. Restrict Service Account Permissions

Only grant minimal required permissions:
- For Google Sheets only: Enable only Sheets API
- For read-only access: Share sheets as "Viewer"
- Avoid granting project-wide "Owner" role

### 2. Rotate Keys Regularly

Service account keys don't expire by default:
1. Create new key every 90 days
2. Update applications with new key
3. Delete old key from Google Cloud Console

### 3. Monitor Service Account Usage

Check audit logs for unexpected activity:
1. Go to Google Cloud Console
2. Navigate to "IAM & Admin" > "Audit Logs"
3. Filter by service account email

### 4. Use Separate Service Accounts

Create different service accounts for:
- Production vs. development
- Different applications
- Read-only vs. read-write access

## Next Steps

- Return to [Setup Guide](setup.md)
- Review [Troubleshooting](troubleshooting.md)
- Explore usage examples in [README](../README.md)

## Additional Resources

- [Google Cloud Service Accounts Documentation](https://cloud.google.com/iam/docs/service-accounts)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Best Practices for Service Accounts](https://cloud.google.com/iam/docs/best-practices-service-accounts)
