#!/usr/bin/env python3
"""
Helper script for Google Sheets operations
Provides a simplified interface for AI coding assistants
"""

from typing import Any, Dict

from google_sheets_integration import (
    append_row,
    append_rows,
    find_row,
    read_sheet,
    read_sheet_as_dicts,
    update_range,
)


def sheets_from_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Google Sheets operation from specification dictionary

    Expected spec format:
    {
        "spreadsheet_id": str,      # Required
        "sheet_name": str,          # Required
        "operation": str,           # Required: "read", "read_dicts", "append",
                                    #          "append_rows", "update", "find"
        "values": list,             # For write operations (append, update)
        "rows": list[list],         # For append_rows operation
        "range_notation": str,      # Optional for read/update, required for update
        "column": str,              # Required for find operation
        "value": str,               # Required for find operation
    }

    Returns:
        Result dictionary from the operation

    Examples:
        # Read as lists
        result = sheets_from_spec({
            "spreadsheet_id": "1ABC...XYZ",
            "sheet_name": "Lead Tracker",
            "operation": "read"
        })

        # Read as dicts
        result = sheets_from_spec({
            "spreadsheet_id": "1ABC...XYZ",
            "sheet_name": "Lead Tracker",
            "operation": "read_dicts"
        })

        # Append single row
        result = sheets_from_spec({
            "spreadsheet_id": "1ABC...XYZ",
            "sheet_name": "Lead Tracker",
            "operation": "append",
            "values": ["Acme Corp", "John Doe", "CEO"]
        })

        # Append multiple rows
        result = sheets_from_spec({
            "spreadsheet_id": "1ABC...XYZ",
            "sheet_name": "Lead Tracker",
            "operation": "append_rows",
            "rows": [
                ["Company A", "Contact A"],
                ["Company B", "Contact B"]
            ]
        })

        # Update range
        result = sheets_from_spec({
            "spreadsheet_id": "1ABC...XYZ",
            "sheet_name": "Lead Tracker",
            "operation": "update",
            "range_notation": "E5",
            "values": [["Outreach Sent"]]
        })

        # Find row
        result = sheets_from_spec({
            "spreadsheet_id": "1ABC...XYZ",
            "sheet_name": "Lead Tracker",
            "operation": "find",
            "column": "A",
            "value": "Acme Corp"
        })
    """

    # Validate required fields
    required = ["spreadsheet_id", "sheet_name", "operation"]
    missing = [f for f in required if f not in spec]
    if missing:
        return {
            "success": False,
            "error": f"Missing required fields: {', '.join(missing)}",
        }

    spreadsheet_id = spec["spreadsheet_id"]
    sheet_name = spec["sheet_name"]
    operation = spec["operation"]
    range_notation = spec.get("range_notation")

    # Route to appropriate function
    if operation == "read":
        return read_sheet(spreadsheet_id, sheet_name, range_notation)

    elif operation == "read_dicts":
        return read_sheet_as_dicts(spreadsheet_id, sheet_name, range_notation)

    elif operation == "append":
        if "values" not in spec:
            return {"success": False, "error": "Missing 'values' field for append operation"}
        return append_row(spreadsheet_id, sheet_name, spec["values"])

    elif operation == "append_rows":
        if "rows" not in spec:
            return {"success": False, "error": "Missing 'rows' field for append_rows operation"}
        return append_rows(spreadsheet_id, sheet_name, spec["rows"])

    elif operation == "update":
        if "range_notation" not in spec:
            return {
                "success": False,
                "error": "Missing 'range_notation' field for update operation",
            }
        if "values" not in spec:
            return {"success": False, "error": "Missing 'values' field for update operation"}
        return update_range(
            spreadsheet_id, sheet_name, spec["range_notation"], spec["values"]
        )

    elif operation == "find":
        if "column" not in spec:
            return {"success": False, "error": "Missing 'column' field for find operation"}
        if "value" not in spec:
            return {"success": False, "error": "Missing 'value' field for find operation"}
        return find_row(
            spreadsheet_id, sheet_name, spec["column"], spec["value"], range_notation
        )

    else:
        return {"success": False, "error": f"Unknown operation: {operation}"}


def print_result_summary(result: Dict[str, Any], operation: str = "operation") -> None:
    """Print a formatted summary of the operation result"""
    if result.get("success"):
        print(f"\n✓ {operation.capitalize()} completed successfully!")

        # Print operation-specific details
        if "data" in result:
            print(f"  Rows: {result.get('rows', 0)}")
            if "columns" in result:
                print(f"  Columns: {result['columns']}")
            if "headers" in result:
                print(f"  Headers: {', '.join(result['headers'])}")

        if "updated_range" in result:
            print(f"  Updated range: {result['updated_range']}")
        if "updated_rows" in result:
            print(f"  Updated rows: {result['updated_rows']}")
        if "updated_cells" in result:
            print(f"  Updated cells: {result['updated_cells']}")

        if "row" in result:
            if result["row"] is not None:
                print(f"  Found at row: {result['row']}")
            else:
                print("  Not found")

    else:
        print(f"\n✗ {operation.capitalize()} failed")
        print(f"  Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    print("Google Sheets Helper Library")
    print("Import this module to use sheets_from_spec() function")
    print("\nExample usage:")
    print("""
    from sheets_helper import sheets_from_spec

    result = sheets_from_spec({
        "spreadsheet_id": "1ABC...XYZ",
        "sheet_name": "Sheet1",
        "operation": "read_dicts"
    })

    if result["success"]:
        for row in result["data"]:
            print(row)
    """)
