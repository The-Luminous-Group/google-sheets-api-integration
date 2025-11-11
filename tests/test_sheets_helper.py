"""
Tests for sheets_helper module
"""

from unittest.mock import Mock, patch

import pytest

import sheets_helper

# ===== Test sheets_from_spec Function =====


def test_sheets_from_spec_missing_required_fields() -> None:
    """Test that missing required fields are detected"""
    spec = {"spreadsheet_id": "test"}  # Missing sheet_name and operation

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is False
    assert "Missing required fields" in result["error"]


@patch("sheets_helper.read_sheet")
def test_sheets_from_spec_read_operation(mock_read: Mock) -> None:
    """Test sheets_from_spec with read operation"""
    mock_read.return_value = {"success": True, "data": [[]], "rows": 0, "columns": 0}

    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "read",
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is True
    mock_read.assert_called_once_with("test-id", "Sheet1", None)


@patch("sheets_helper.read_sheet")
def test_sheets_from_spec_read_with_range(mock_read: Mock) -> None:
    """Test sheets_from_spec read with range notation"""
    mock_read.return_value = {"success": True, "data": [[]], "rows": 0, "columns": 0}

    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "read",
        "range_notation": "A1:B10",
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is True
    mock_read.assert_called_once_with("test-id", "Sheet1", "A1:B10")


@patch("sheets_helper.read_sheet_as_dicts")
def test_sheets_from_spec_read_dicts_operation(mock_read_dicts: Mock) -> None:
    """Test sheets_from_spec with read_dicts operation"""
    mock_read_dicts.return_value = {
        "success": True,
        "data": [],
        "rows": 0,
        "headers": [],
    }

    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "read_dicts",
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is True
    mock_read_dicts.assert_called_once_with("test-id", "Sheet1", None)


@patch("sheets_helper.append_row")
def test_sheets_from_spec_append_operation(mock_append: Mock) -> None:
    """Test sheets_from_spec with append operation"""
    mock_append.return_value = {
        "success": True,
        "updated_range": "Sheet1!A10",
        "updated_rows": 1,
    }

    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "append",
        "values": ["Value1", "Value2", "Value3"],
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is True
    mock_append.assert_called_once_with("test-id", "Sheet1", ["Value1", "Value2", "Value3"])


def test_sheets_from_spec_append_missing_values() -> None:
    """Test append operation without values field"""
    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "append",
        # Missing "values"
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is False
    assert "Missing 'values'" in result["error"]


@patch("sheets_helper.append_rows")
def test_sheets_from_spec_append_rows_operation(mock_append_rows: Mock) -> None:
    """Test sheets_from_spec with append_rows operation"""
    mock_append_rows.return_value = {
        "success": True,
        "updated_range": "Sheet1!A10:C11",
        "updated_rows": 2,
    }

    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "append_rows",
        "rows": [["Val1", "Val2"], ["Val3", "Val4"]],
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is True
    mock_append_rows.assert_called_once_with(
        "test-id", "Sheet1", [["Val1", "Val2"], ["Val3", "Val4"]]
    )


def test_sheets_from_spec_append_rows_missing_rows() -> None:
    """Test append_rows operation without rows field"""
    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "append_rows",
        # Missing "rows"
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is False
    assert "Missing 'rows'" in result["error"]


@patch("sheets_helper.update_range")
def test_sheets_from_spec_update_operation(mock_update: Mock) -> None:
    """Test sheets_from_spec with update operation"""
    mock_update.return_value = {
        "success": True,
        "updated_range": "Sheet1!E5",
        "updated_rows": 1,
        "updated_cells": 1,
    }

    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "update",
        "range_notation": "E5",
        "values": [["New Value"]],
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is True
    mock_update.assert_called_once_with("test-id", "Sheet1", "E5", [["New Value"]])


def test_sheets_from_spec_update_missing_range() -> None:
    """Test update operation without range_notation"""
    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "update",
        "values": [["Value"]],
        # Missing "range_notation"
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is False
    assert "Missing 'range_notation'" in result["error"]


def test_sheets_from_spec_update_missing_values() -> None:
    """Test update operation without values"""
    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "update",
        "range_notation": "E5",
        # Missing "values"
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is False
    assert "Missing 'values'" in result["error"]


@patch("sheets_helper.find_row")
def test_sheets_from_spec_find_operation(mock_find: Mock) -> None:
    """Test sheets_from_spec with find operation"""
    mock_find.return_value = {"success": True, "row": 5}

    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "find",
        "column": "A",
        "value": "Acme Corp",
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is True
    assert result["row"] == 5
    mock_find.assert_called_once_with("test-id", "Sheet1", "A", "Acme Corp", None)


@patch("sheets_helper.find_row")
def test_sheets_from_spec_find_with_range(mock_find: Mock) -> None:
    """Test find operation with range notation"""
    mock_find.return_value = {"success": True, "row": 3}

    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "find",
        "column": "A",
        "value": "Test Value",
        "range_notation": "A1:A100",
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is True
    mock_find.assert_called_once_with("test-id", "Sheet1", "A", "Test Value", "A1:A100")


def test_sheets_from_spec_find_missing_column() -> None:
    """Test find operation without column field"""
    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "find",
        "value": "Test Value",
        # Missing "column"
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is False
    assert "Missing 'column'" in result["error"]


def test_sheets_from_spec_find_missing_value() -> None:
    """Test find operation without value field"""
    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "find",
        "column": "A",
        # Missing "value"
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is False
    assert "Missing 'value'" in result["error"]


def test_sheets_from_spec_unknown_operation() -> None:
    """Test with unknown operation type"""
    spec = {
        "spreadsheet_id": "test-id",
        "sheet_name": "Sheet1",
        "operation": "invalid_operation",
    }

    result = sheets_helper.sheets_from_spec(spec)

    assert result["success"] is False
    assert "Unknown operation" in result["error"]


# ===== Test print_result_summary Function =====


def test_print_result_summary_success(capsys: pytest.CaptureFixture) -> None:
    """Test print_result_summary with successful result"""
    result = {
        "success": True,
        "data": [["row1"], ["row2"]],
        "rows": 2,
        "columns": 1,
    }

    sheets_helper.print_result_summary(result, "read")

    captured = capsys.readouterr()
    assert "✓" in captured.out
    assert "Read completed successfully" in captured.out
    assert "Rows: 2" in captured.out


def test_print_result_summary_failure(capsys: pytest.CaptureFixture) -> None:
    """Test print_result_summary with failed result"""
    result = {"success": False, "error": "Test error message"}

    sheets_helper.print_result_summary(result, "append")

    captured = capsys.readouterr()
    assert "✗" in captured.out
    assert "Append failed" in captured.out
    assert "Test error message" in captured.out


def test_print_result_summary_with_updates(capsys: pytest.CaptureFixture) -> None:
    """Test print_result_summary with update information"""
    result = {
        "success": True,
        "updated_range": "Sheet1!A10:C10",
        "updated_rows": 1,
        "updated_cells": 3,
    }

    sheets_helper.print_result_summary(result, "update")

    captured = capsys.readouterr()
    assert "✓" in captured.out
    assert "Updated range: Sheet1!A10:C10" in captured.out
    assert "Updated rows: 1" in captured.out
    assert "Updated cells: 3" in captured.out


def test_print_result_summary_with_find_found(capsys: pytest.CaptureFixture) -> None:
    """Test print_result_summary with find result (found)"""
    result = {"success": True, "row": 5}

    sheets_helper.print_result_summary(result, "find")

    captured = capsys.readouterr()
    assert "✓" in captured.out
    assert "Found at row: 5" in captured.out


def test_print_result_summary_with_find_not_found(capsys: pytest.CaptureFixture) -> None:
    """Test print_result_summary with find result (not found)"""
    result = {"success": True, "row": None}

    sheets_helper.print_result_summary(result, "find")

    captured = capsys.readouterr()
    assert "✓" in captured.out
    assert "Not found" in captured.out
