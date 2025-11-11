"""
Tests for google_sheets_integration module
"""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest

import google_sheets_integration as gsi

# ===== Test Custom Exceptions =====


def test_exception_hierarchy() -> None:
    """Test that custom exceptions are properly defined"""
    assert issubclass(gsi.GoogleSheetsError, Exception)
    assert issubclass(gsi.GoogleSheetsAuthError, gsi.GoogleSheetsError)
    assert issubclass(gsi.GoogleSheetsAPIError, gsi.GoogleSheetsError)
    assert issubclass(gsi.GoogleSheetsNotFoundError, gsi.GoogleSheetsError)


# ===== Test Authentication Functions =====


def test_from_env_with_value(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test _from_env returns value when env var is set"""
    monkeypatch.setenv("GOOGLE_SHEETS_SERVICE_ACCOUNT", "/path/to/creds.json")
    result = gsi._from_env()
    assert result == "/path/to/creds.json"


def test_from_env_without_value(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test _from_env returns None when env var is not set"""
    monkeypatch.delenv("GOOGLE_SHEETS_SERVICE_ACCOUNT", raising=False)
    result = gsi._from_env()
    assert result is None


@patch("subprocess.run")
def test_from_keychain_success(mock_run: Mock) -> None:
    """Test _from_keychain successfully retrieves from Keychain"""
    mock_run.return_value = Mock(stdout="service-account-json-content\n")
    result = gsi._from_keychain()
    assert result == "service-account-json-content"


@patch("subprocess.run")
def test_from_keychain_failure(mock_run: Mock) -> None:
    """Test _from_keychain returns None on failure"""
    mock_run.side_effect = FileNotFoundError()
    result = gsi._from_keychain()
    assert result is None


@patch("subprocess.run")
def test_from_1password_success(mock_run: Mock) -> None:
    """Test _from_1password successfully retrieves from 1Password"""
    mock_run.return_value = Mock(stdout="service-account-json-content\n")
    result = gsi._from_1password()
    assert result == "service-account-json-content"


@patch("subprocess.run")
def test_from_1password_failure(mock_run: Mock) -> None:
    """Test _from_1password returns None on failure"""
    mock_run.side_effect = FileNotFoundError()
    result = gsi._from_1password()
    assert result is None


@patch("google_sheets_integration.service_account.Credentials.from_service_account_info")
def test_get_service_account_credentials_from_json(
    mock_creds: Mock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test getting credentials from JSON string"""
    json_content = json.dumps({"type": "service_account", "project_id": "test"})
    monkeypatch.setenv("GOOGLE_SHEETS_SERVICE_ACCOUNT", json_content)

    mock_creds.return_value = Mock()

    result = gsi.get_service_account_credentials()
    assert result is not None
    mock_creds.assert_called_once()


@patch("google_sheets_integration.service_account.Credentials.from_service_account_file")
def test_get_service_account_credentials_from_file(
    mock_creds: Mock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test getting credentials from file path"""
    monkeypatch.setenv("GOOGLE_SHEETS_SERVICE_ACCOUNT", "/path/to/creds.json")

    mock_creds.return_value = Mock()

    result = gsi.get_service_account_credentials()
    assert result is not None
    mock_creds.assert_called_once()


def test_get_service_account_credentials_no_source(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that auth error is raised when no credential source is available"""
    monkeypatch.delenv("GOOGLE_SHEETS_SERVICE_ACCOUNT", raising=False)

    with pytest.raises(gsi.GoogleSheetsAuthError):
        gsi.get_service_account_credentials()


# ===== Test Read Functions =====


@patch("google_sheets_integration._get_sheets_service")
def test_read_sheet_success(mock_service: Mock) -> None:
    """Test successful sheet read"""
    mock_sheets = MagicMock()
    mock_service.return_value = mock_sheets

    mock_sheets.spreadsheets().values().get().execute.return_value = {
        "values": [
            ["Header1", "Header2"],
            ["Value1", "Value2"],
            ["Value3", "Value4"],
        ]
    }

    result = gsi.read_sheet("test-spreadsheet-id", "Sheet1")

    assert result["success"] is True
    assert result["rows"] == 3
    assert result["columns"] == 2
    assert len(result["data"]) == 3


@patch("google_sheets_integration._get_sheets_service")
def test_read_sheet_with_range(mock_service: Mock) -> None:
    """Test sheet read with range notation"""
    mock_sheets = MagicMock()
    mock_service.return_value = mock_sheets

    mock_sheets.spreadsheets().values().get().execute.return_value = {
        "values": [["Value1", "Value2"]]
    }

    result = gsi.read_sheet("test-spreadsheet-id", "Sheet1", "A1:B1")

    assert result["success"] is True
    assert result["rows"] == 1


@patch("google_sheets_integration._get_sheets_service")
def test_read_sheet_not_found(mock_service: Mock) -> None:
    """Test read sheet when spreadsheet not found"""
    from googleapiclient.errors import HttpError

    mock_sheets = MagicMock()
    mock_service.return_value = mock_sheets

    # Mock HTTP 404 error
    resp = Mock()
    resp.status = 404
    mock_sheets.spreadsheets().values().get().execute.side_effect = HttpError(
        resp=resp, content=b"Not found"
    )

    result = gsi.read_sheet("test-spreadsheet-id", "Sheet1")

    assert result["success"] is False
    assert "not found" in result["error"].lower()


@patch("google_sheets_integration._get_sheets_service")
def test_read_sheet_as_dicts_success(mock_service: Mock) -> None:
    """Test successful read_sheet_as_dicts"""
    mock_sheets = MagicMock()
    mock_service.return_value = mock_sheets

    mock_sheets.spreadsheets().values().get().execute.return_value = {
        "values": [
            ["Company", "Contact", "Status"],
            ["Acme Corp", "John Doe", "Qualified"],
            ["Beta Inc", "Jane Smith", "Pending"],
        ]
    }

    result = gsi.read_sheet_as_dicts("test-spreadsheet-id", "Sheet1")

    assert result["success"] is True
    assert result["rows"] == 2
    assert result["headers"] == ["Company", "Contact", "Status"]
    assert result["data"][0]["Company"] == "Acme Corp"
    assert result["data"][1]["Contact"] == "Jane Smith"


@patch("google_sheets_integration._get_sheets_service")
def test_read_sheet_as_dicts_empty(mock_service: Mock) -> None:
    """Test read_sheet_as_dicts with empty sheet"""
    mock_sheets = MagicMock()
    mock_service.return_value = mock_sheets

    mock_sheets.spreadsheets().values().get().execute.return_value = {"values": []}

    result = gsi.read_sheet_as_dicts("test-spreadsheet-id", "Sheet1")

    assert result["success"] is True
    assert result["rows"] == 0
    assert result["data"] == []


# ===== Test Write Functions =====


@patch("google_sheets_integration._get_sheets_service")
def test_append_row_success(mock_service: Mock) -> None:
    """Test successful append_row"""
    mock_sheets = MagicMock()
    mock_service.return_value = mock_sheets

    mock_sheets.spreadsheets().values().append().execute.return_value = {
        "updates": {
            "updatedRange": "Sheet1!A10:C10",
            "updatedRows": 1,
        }
    }

    result = gsi.append_row("test-spreadsheet-id", "Sheet1", ["Value1", "Value2", "Value3"])

    assert result["success"] is True
    assert result["updated_rows"] == 1


@patch("google_sheets_integration._get_sheets_service")
def test_append_rows_success(mock_service: Mock) -> None:
    """Test successful append_rows"""
    mock_sheets = MagicMock()
    mock_service.return_value = mock_sheets

    mock_sheets.spreadsheets().values().append().execute.return_value = {
        "updates": {
            "updatedRange": "Sheet1!A10:C11",
            "updatedRows": 2,
        }
    }

    rows = [["Value1", "Value2"], ["Value3", "Value4"]]
    result = gsi.append_rows("test-spreadsheet-id", "Sheet1", rows)

    assert result["success"] is True
    assert result["updated_rows"] == 2


@patch("google_sheets_integration._get_sheets_service")
def test_update_range_success(mock_service: Mock) -> None:
    """Test successful update_range"""
    mock_sheets = MagicMock()
    mock_service.return_value = mock_sheets

    mock_sheets.spreadsheets().values().update().execute.return_value = {
        "updatedRange": "Sheet1!E5",
        "updatedRows": 1,
        "updatedCells": 1,
    }

    result = gsi.update_range("test-spreadsheet-id", "Sheet1", "E5", [["New Value"]])

    assert result["success"] is True
    assert result["updated_rows"] == 1
    assert result["updated_cells"] == 1


@patch("google_sheets_integration._get_sheets_service")
def test_update_range_multiple_cells(mock_service: Mock) -> None:
    """Test update_range with multiple cells"""
    mock_sheets = MagicMock()
    mock_service.return_value = mock_sheets

    mock_sheets.spreadsheets().values().update().execute.return_value = {
        "updatedRange": "Sheet1!A2:C4",
        "updatedRows": 3,
        "updatedCells": 9,
    }

    values = [
        ["A1", "B1", "C1"],
        ["A2", "B2", "C2"],
        ["A3", "B3", "C3"],
    ]
    result = gsi.update_range("test-spreadsheet-id", "Sheet1", "A2:C4", values)

    assert result["success"] is True
    assert result["updated_rows"] == 3
    assert result["updated_cells"] == 9


# ===== Test Helper Functions =====


@patch("google_sheets_integration._get_sheets_service")
def test_find_row_found(mock_service: Mock) -> None:
    """Test find_row when value is found"""
    mock_sheets = MagicMock()
    mock_service.return_value = mock_sheets

    mock_sheets.spreadsheets().values().get().execute.return_value = {
        "values": [["Company A"], ["Company B"], ["Acme Corp"], ["Company D"]]
    }

    result = gsi.find_row("test-spreadsheet-id", "Sheet1", "A", "Acme Corp")

    assert result["success"] is True
    assert result["row"] == 3


@patch("google_sheets_integration._get_sheets_service")
def test_find_row_not_found(mock_service: Mock) -> None:
    """Test find_row when value is not found"""
    mock_sheets = MagicMock()
    mock_service.return_value = mock_sheets

    mock_sheets.spreadsheets().values().get().execute.return_value = {
        "values": [["Company A"], ["Company B"], ["Company C"]]
    }

    result = gsi.find_row("test-spreadsheet-id", "Sheet1", "A", "Nonexistent Corp")

    assert result["success"] is True
    assert result["row"] is None


@patch("google_sheets_integration._get_sheets_service")
def test_find_row_with_range(mock_service: Mock) -> None:
    """Test find_row with specific range"""
    mock_sheets = MagicMock()
    mock_service.return_value = mock_sheets

    mock_sheets.spreadsheets().values().get().execute.return_value = {
        "values": [["Value1"], ["Value2"], ["Value3"]]
    }

    result = gsi.find_row("test-spreadsheet-id", "Sheet1", "A", "Value2", "A1:A10")

    assert result["success"] is True
    assert result["row"] == 2


# ===== Test Error Handling =====


@patch("google_sheets_integration._get_sheets_service")
def test_auth_error_handling(mock_service: Mock) -> None:
    """Test that auth errors are properly handled"""
    mock_service.side_effect = gsi.GoogleSheetsAuthError("Auth failed")

    result = gsi.read_sheet("test-spreadsheet-id", "Sheet1")

    assert result["success"] is False
    assert "Authentication failed" in result["error"]


@patch("google_sheets_integration._get_sheets_service")
def test_api_error_handling(mock_service: Mock) -> None:
    """Test that API errors are properly handled"""
    from googleapiclient.errors import HttpError

    mock_sheets = MagicMock()
    mock_service.return_value = mock_sheets

    resp = Mock()
    resp.status = 500
    mock_sheets.spreadsheets().values().get().execute.side_effect = HttpError(
        resp=resp, content=b"Server error"
    )

    result = gsi.read_sheet("test-spreadsheet-id", "Sheet1")

    assert result["success"] is False
    assert "API error" in result["error"]
