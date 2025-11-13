#!/usr/bin/env python3
"""
Google Sheets API Integration
Provides functions for reading from and writing to Google Sheets programmatically
"""

import json
import os
import subprocess
from typing import Any, Callable, Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes for Google Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


# ===== Custom Exceptions =====


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


# ===== Authentication Functions =====


def _from_env() -> Optional[str]:
    """Get service account credential path or JSON from environment variable"""
    value = os.getenv("GOOGLE_SHEETS_SERVICE_ACCOUNT")
    return value.strip() if value else None


def _from_keychain() -> Optional[str]:
    """Get service account credentials from macOS Keychain"""
    service = "Google Sheets Service Account"
    account = os.getenv("USER", "default")

    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()
        return output or None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _from_1password() -> Optional[str]:
    """Get service account credentials from 1Password using op CLI"""
    item_path = os.getenv(
        "GOOGLE_SHEETS_1PASSWORD_PATH",
        "op://Personal/Google Sheets Service Account/credential",
    )

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

def _from_json_env() -> Optional[str]:
    """Get credential JSON string directly from environment"""
    value = os.getenv("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON")
    return value.strip() if value else None


# Credential source mapping
CREDENTIAL_SOURCES: Dict[str, Callable[[], Optional[str]]] = {
    "json": _from_json_env,
    "env": _from_env,
    "keychain": _from_keychain,
    "1password": _from_1password,
}


def get_service_account_credentials() -> service_account.Credentials:
    """
    Retrieve Google Service Account credentials from various sources

    Tries sources in order:
    1. Environment variable GOOGLE_SHEETS_SERVICE_ACCOUNT (file path or 1Password ref)
    2. macOS Keychain (service: "Google Sheets Service Account")
    3. 1Password CLI (default item path)

    Returns:
        Service account credentials object

    Raises:
        GoogleSheetsAuthError: If credentials cannot be retrieved
    """
    source_env = os.getenv("GOOGLE_SHEETS_CREDENTIAL_SOURCES")
    if source_env:
        preferred_sources = [
            item.strip().lower() for item in source_env.split(",") if item.strip()
        ]
    else:
        preferred_sources = ["json", "env", "keychain", "1password"]

    tried: List[str] = []
    credential_data: Optional[str] = None

    for source in preferred_sources:
        retriever = CREDENTIAL_SOURCES.get(source)
        if not retriever:
            tried.append(f"{source} (unknown)")
            continue

        value = retriever()
        if value:
            credential_data = value
            break
        tried.append(source)

    if not credential_data:
        error_msg = "Unable to retrieve Google Sheets service account credentials.\n"
        if tried:
            error_msg += f"Tried sources: {', '.join(tried)}\n"
        error_msg += (
            "Set GOOGLE_SHEETS_SERVICE_ACCOUNT environment variable, "
            "store credentials in Keychain, or configure 1Password.\n"
            "Override lookup order via GOOGLE_SHEETS_CREDENTIAL_SOURCES (comma separated)."
        )
        raise GoogleSheetsAuthError(error_msg)

    # Check if it's a 1Password reference
    if credential_data.startswith("op://"):
        # Try to read it via 1Password
        try:
            result = subprocess.run(
                ["op", "read", credential_data],
                capture_output=True,
                text=True,
                check=True,
            )
            credential_data = result.stdout.strip()
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            raise GoogleSheetsAuthError(
                f"Failed to read 1Password reference: {credential_data}"
            ) from e

    # Try to parse as JSON (direct credential content)
    try:
        creds_dict = json.loads(credential_data)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=SCOPES
        )
        return credentials
    except json.JSONDecodeError:
        # Not JSON, treat as file path
        pass

    # Try to load from file path
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credential_data, scopes=SCOPES
        )
        return credentials
    except FileNotFoundError as e:
        raise GoogleSheetsAuthError(
            f"Service account file not found: {credential_data}"
        ) from e
    except Exception as e:
        raise GoogleSheetsAuthError(
            f"Failed to load service account credentials: {e}"
        ) from e


def _get_sheets_service() -> Any:
    """Get authenticated Google Sheets API service"""
    try:
        credentials = get_service_account_credentials()
        service = build("sheets", "v4", credentials=credentials)
        return service
    except Exception as e:
        raise GoogleSheetsAuthError(f"Failed to create Sheets service: {e}") from e


# ===== Core Read Functions =====


def read_sheet(
    spreadsheet_id: str,
    sheet_name: str,
    range_notation: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Read data from a Google Sheet

    Args:
        spreadsheet_id: The ID of the spreadsheet (from the URL)
        sheet_name: The name of the sheet/tab
        range_notation: Optional A1 notation range (e.g., "A1:E100")
                       If not provided, reads entire sheet

    Returns:
        Dictionary with:
            - success: bool
            - data: List[List[str]] (2D array of cell values)
            - rows: int (number of rows)
            - columns: int (number of columns in first row)
            - error: str (if success=False)

    Example:
        result = read_sheet("1ABC...XYZ", "Lead Tracker", "A1:E100")
        if result["success"]:
            data = result["data"]
            print(f"Read {result['rows']} rows")
    """
    try:
        service = _get_sheets_service()

        # Build range string
        range_str = f"{sheet_name}!{range_notation}" if range_notation else sheet_name

        # Execute API call
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_str)
            .execute()
        )

        values = result.get("values", [])

        return {
            "success": True,
            "data": values,
            "rows": len(values),
            "columns": len(values[0]) if values else 0,
        }

    except HttpError as e:
        if e.resp.status == 404:
            return {
                "success": False,
                "error": f"Spreadsheet or sheet not found: {spreadsheet_id}",
            }
        return {"success": False, "error": f"API error: {e}"}
    except GoogleSheetsAuthError as e:
        return {"success": False, "error": f"Authentication failed: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}


def read_sheet_as_dicts(
    spreadsheet_id: str,
    sheet_name: str,
    range_notation: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Read data from a Google Sheet and return as list of dictionaries

    First row is treated as headers and used as dictionary keys.

    Args:
        spreadsheet_id: The ID of the spreadsheet (from the URL)
        sheet_name: The name of the sheet/tab
        range_notation: Optional A1 notation range (e.g., "A1:E100")

    Returns:
        Dictionary with:
            - success: bool
            - data: List[Dict[str, str]] (list of row dicts)
            - rows: int (number of data rows, excluding header)
            - headers: List[str] (column headers)
            - error: str (if success=False)

    Example:
        result = read_sheet_as_dicts("1ABC...XYZ", "Lead Tracker")
        if result["success"]:
            for row in result["data"]:
                print(f"Company: {row['Company']}, Status: {row['Status']}")
    """
    read_result = read_sheet(spreadsheet_id, sheet_name, range_notation)

    if not read_result["success"]:
        return read_result

    values = read_result["data"]

    if not values:
        return {
            "success": True,
            "data": [],
            "rows": 0,
            "headers": [],
        }

    # First row is headers
    headers = values[0]
    data_rows = values[1:]

    # Convert rows to dictionaries
    dict_data = []
    for row in data_rows:
        # Pad row with empty strings if shorter than headers
        padded_row = row + [""] * (len(headers) - len(row))
        row_dict = dict(zip(headers, padded_row))
        dict_data.append(row_dict)

    return {
        "success": True,
        "data": dict_data,
        "rows": len(dict_data),
        "headers": headers,
    }


# ===== Core Write Functions =====


def append_row(
    spreadsheet_id: str,
    sheet_name: str,
    values: List[Any],
) -> Dict[str, Any]:
    """
    Append a single row to a Google Sheet

    Args:
        spreadsheet_id: The ID of the spreadsheet
        sheet_name: The name of the sheet/tab
        values: List of values to append as a new row

    Returns:
        Dictionary with:
            - success: bool
            - updated_range: str (range that was updated)
            - updated_rows: int
            - error: str (if success=False)

    Example:
        result = append_row(
            "1ABC...XYZ",
            "Lead Tracker",
            ["Acme Corp", "John Doe", "CEO", "Qualified"]
        )
    """
    try:
        service = _get_sheets_service()

        body = {"values": [values]}

        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=sheet_name,
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )

        return {
            "success": True,
            "updated_range": result.get("updates", {}).get("updatedRange", ""),
            "updated_rows": result.get("updates", {}).get("updatedRows", 0),
        }

    except HttpError as e:
        if e.resp.status == 404:
            return {
                "success": False,
                "error": f"Spreadsheet or sheet not found: {spreadsheet_id}",
            }
        return {"success": False, "error": f"API error: {e}"}
    except GoogleSheetsAuthError as e:
        return {"success": False, "error": f"Authentication failed: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}


def append_rows(
    spreadsheet_id: str,
    sheet_name: str,
    rows: List[List[Any]],
) -> Dict[str, Any]:
    """
    Append multiple rows to a Google Sheet

    Args:
        spreadsheet_id: The ID of the spreadsheet
        sheet_name: The name of the sheet/tab
        rows: List of rows, where each row is a list of values

    Returns:
        Dictionary with:
            - success: bool
            - updated_range: str
            - updated_rows: int
            - error: str (if success=False)

    Example:
        result = append_rows(
            "1ABC...XYZ",
            "Lead Tracker",
            [
                ["Acme Corp", "John Doe", "CEO"],
                ["Beta Inc", "Jane Smith", "CTO"]
            ]
        )
    """
    try:
        service = _get_sheets_service()

        body = {"values": rows}

        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=sheet_name,
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )

        return {
            "success": True,
            "updated_range": result.get("updates", {}).get("updatedRange", ""),
            "updated_rows": result.get("updates", {}).get("updatedRows", 0),
        }

    except HttpError as e:
        if e.resp.status == 404:
            return {
                "success": False,
                "error": f"Spreadsheet or sheet not found: {spreadsheet_id}",
            }
        return {"success": False, "error": f"API error: {e}"}
    except GoogleSheetsAuthError as e:
        return {"success": False, "error": f"Authentication failed: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}


def append_rows_to_table(
    spreadsheet_id: str,
    sheet_name: str,
    rows: List[List[Any]],
) -> Dict[str, Any]:
    """
    Append rows to a Google Sheets table with automatic formatting extension

    This function appends rows using AppendCellsRequest with table awareness,
    which automatically extends table formatting, data validation, and styling
    to newly added rows.

    Args:
        spreadsheet_id: The ID of the spreadsheet
        sheet_name: The name of the sheet/tab containing the table
        rows: List of rows, where each row is a list of values

    Returns:
        Dictionary with:
            - success: bool
            - table_id: str (the table that was appended to)
            - rows_added: int
            - error: str (if success=False)

    Example:
        result = append_rows_to_table(
            "1ABC...XYZ",
            "Interactions",
            [
                ["I001", "2025-11-10", "CT001", "John Doe", ...],
                ["I002", "2025-11-13", "CT001", "John Doe", ...]
            ]
        )

    Note:
        - The sheet must be formatted as a table in Google Sheets
        - Data validation, formulas, and formatting automatically extend
        - If no table exists, an error is returned
    """
    try:
        service = _get_sheets_service()

        # Step 1: Get spreadsheet metadata to find the table
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()

        # Step 2: Find the sheet and its table
        table_id = None
        sheet_id = None

        for sheet in spreadsheet.get('sheets', []):
            if sheet['properties']['title'] == sheet_name:
                sheet_id = sheet['properties']['sheetId']
                tables = sheet.get('tables', [])
                if tables:
                    table_id = tables[0]['tableId']  # Use first table in sheet
                break

        if not sheet_id:
            return {
                "success": False,
                "error": f"Sheet '{sheet_name}' not found in spreadsheet"
            }

        if not table_id:
            return {
                "success": False,
                "error": f"No table found in sheet '{sheet_name}'. Format the sheet as a table first."
            }

        # Step 3: Build AppendCellsRequest
        row_data = []
        for row in rows:
            values = []
            for cell_value in row:
                # Convert Python values to Google Sheets cell format
                cell_data = {"userEnteredValue": {}}

                if isinstance(cell_value, bool):
                    cell_data["userEnteredValue"]["boolValue"] = cell_value
                elif isinstance(cell_value, (int, float)):
                    cell_data["userEnteredValue"]["numberValue"] = cell_value
                elif isinstance(cell_value, str) and cell_value.startswith('='):
                    # Formula
                    cell_data["userEnteredValue"]["formulaValue"] = cell_value
                else:
                    # String or None
                    cell_data["userEnteredValue"]["stringValue"] = str(cell_value) if cell_value is not None else ""

                values.append(cell_data)

            row_data.append({"values": values})

        # Step 4: Execute batchUpdate with AppendCellsRequest
        request_body = {
            "requests": [
                {
                    "appendCells": {
                        "sheetId": sheet_id,
                        "tableId": table_id,
                        "rows": row_data,
                        "fields": "*"  # Update all fields
                    }
                }
            ]
        }

        result = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=request_body
        ).execute()

        return {
            "success": True,
            "table_id": table_id,
            "rows_added": len(rows),
            "batch_update_result": result
        }

    except HttpError as e:
        if e.resp.status == 404:
            return {
                "success": False,
                "error": f"Spreadsheet or sheet not found: {spreadsheet_id}"
            }
        return {"success": False, "error": f"API error: {e}"}
    except GoogleSheetsAuthError as e:
        return {"success": False, "error": f"Authentication failed: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}


def update_range(
    spreadsheet_id: str,
    sheet_name: str,
    range_notation: str,
    values: List[List[Any]],
) -> Dict[str, Any]:
    """
    Update a specific range of cells in a Google Sheet

    Args:
        spreadsheet_id: The ID of the spreadsheet
        sheet_name: The name of the sheet/tab
        range_notation: A1 notation range (e.g., "E5" or "A2:C4")
        values: 2D list of values to write

    Returns:
        Dictionary with:
            - success: bool
            - updated_range: str
            - updated_rows: int
            - updated_cells: int
            - error: str (if success=False)

    Example:
        # Update single cell
        result = update_range(
            "1ABC...XYZ",
            "Lead Tracker",
            "E5",
            [["Outreach Sent"]]
        )

        # Update range
        result = update_range(
            "1ABC...XYZ",
            "Lead Tracker",
            "A2:C4",
            [
                ["Company A", "Contact A", "Status A"],
                ["Company B", "Contact B", "Status B"],
                ["Company C", "Contact C", "Status C"]
            ]
        )
    """
    try:
        service = _get_sheets_service()

        range_str = f"{sheet_name}!{range_notation}"
        body = {"values": values}

        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_str,
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )

        return {
            "success": True,
            "updated_range": result.get("updatedRange", ""),
            "updated_rows": result.get("updatedRows", 0),
            "updated_cells": result.get("updatedCells", 0),
        }

    except HttpError as e:
        if e.resp.status == 404:
            return {
                "success": False,
                "error": f"Spreadsheet or sheet not found: {spreadsheet_id}",
            }
        return {"success": False, "error": f"API error: {e}"}
    except GoogleSheetsAuthError as e:
        return {"success": False, "error": f"Authentication failed: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}


# ===== Helper Functions =====


def find_row(
    spreadsheet_id: str,
    sheet_name: str,
    column: str,
    value: str,
    range_notation: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Find the row number where a column contains a specific value

    Args:
        spreadsheet_id: The ID of the spreadsheet
        sheet_name: The name of the sheet/tab
        column: Column letter (e.g., "A", "B", "C")
        value: Value to search for (case-sensitive)
        range_notation: Optional range to search within (e.g., "A1:A100")

    Returns:
        Dictionary with:
            - success: bool
            - row: Optional[int] (1-indexed row number, None if not found)
            - error: str (if success=False)

    Example:
        result = find_row("1ABC...XYZ", "Lead Tracker", "A", "Acme Corp")
        if result["success"] and result["row"]:
            print(f"Found at row {result['row']}")
    """
    try:
        # Build search range
        search_range = range_notation or f"{column}:{column}"

        # Read the column
        read_result = read_sheet(spreadsheet_id, sheet_name, search_range)

        if not read_result["success"]:
            return read_result

        values = read_result["data"]

        # Search for value
        for idx, row in enumerate(values, start=1):
            if row and row[0] == value:
                return {"success": True, "row": idx}

        # Not found
        return {"success": True, "row": None}

    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}


if __name__ == "__main__":
    print("Google Sheets Integration Library")
    print("Import this module to use its functions")
