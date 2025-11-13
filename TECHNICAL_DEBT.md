# Technical Debt

## Date Storage and Formatting

**Priority:** Medium
**Effort:** Medium
**Impact:** High (affects reporting, filtering, time-series analysis)

### Problem

Currently, dates throughout the spreadsheet are stored inconsistently:

1. **Most date columns** (Companies.Date Added, Contacts.Date Added, Signals.Date Received, Interactions.Date):
   - Stored as **text strings** (e.g., `'2025-11-10'`)
   - Display correctly but are not true dates
   - Cannot be used in date calculations, filters, or aggregations

2. **Calculated date columns** (Interactions.Follow-up 30d/60d/90d):
   - Formulas like `=B6+30` produce **date serial numbers**
   - Require explicit date formatting to display correctly
   - Format must be applied to table columns manually

### Impact

**Current limitations:**
- Cannot filter by date range (e.g., "show all interactions in November")
- Cannot sort chronologically (text sort gives incorrect order)
- Cannot use date-based formulas (MONTH(), YEAR(), date comparisons)
- Dashboard cannot aggregate by month/quarter/year
- Time-series analysis not possible
- Reporting tools cannot recognize dates as temporal data

**Example broken queries:**
```
=COUNTIFS(Interactions!B:B, ">=2025-11-01", Interactions!B:B, "<2025-12-01")  // Won't work with text dates
=FILTER(Contacts, Contacts!M:M < TODAY()-30)  // Won't work with text dates
```

### Root Cause

When dates are sent to Google Sheets API as strings (e.g., `'2025-11-10'`), they are stored as text, not as date serial numbers. Google Sheets displays them correctly but treats them as text internally.

### Solution

#### Phase 1: Update API Code (google-sheets-api-integration)

Modify `append_rows_to_table()` to automatically convert date strings to serial numbers:

```python
from datetime import datetime

def date_string_to_serial(date_string: str) -> float:
    """
    Convert YYYY-MM-DD string to Google Sheets serial number

    Google Sheets epoch: December 30, 1899
    Serial number = days since epoch
    """
    if not date_string or not isinstance(date_string, str):
        return date_string

    try:
        # Try to parse as YYYY-MM-DD
        date = datetime.strptime(date_string, '%Y-%m-%d')
        epoch = datetime(1899, 12, 30)
        delta = date - epoch
        return float(delta.days)
    except ValueError:
        # Not a date string, return as-is
        return date_string

def append_rows_to_table(spreadsheet_id, sheet_name, rows):
    # ... existing code ...

    # Detect date columns from table metadata
    date_columns = _get_date_column_indices(table_metadata)

    # Convert date strings to serial numbers
    for row in rows:
        for col_idx in date_columns:
            if col_idx < len(row):
                row[col_idx] = date_string_to_serial(row[col_idx])

    # ... rest of function ...
```

**Alternative approach:** Accept date column indices as parameter:
```python
append_rows_to_table(
    spreadsheet_id,
    sheet_name,
    rows,
    date_columns=[1, 11, 12, 13]  # B, L, M, N (0-indexed)
)
```

#### Phase 2: Format Date Columns in Spreadsheet

For each sheet, apply date formatting to all date columns:

**Companies:**
- P (Date Added)
- Q (Last Updated)

**Contacts:**
- L (Date Added)
- M (Last Contact)
- N (Next Follow-up)

**Signals:**
- B (Date Received)

**Interactions:**
- B (Date)
- L (Follow-up 30d)
- M (Follow-up 60d)
- N (Follow-up 90d)
- O (Custom Follow-up)

**Format to apply:** Custom number format `yyyy-mm-dd` to match existing display

#### Phase 3: Migrate Existing Data (Optional)

If consistency is required, migrate existing text dates to serial numbers:

```python
def migrate_text_dates_to_serial(spreadsheet_id, sheet_name, date_columns):
    """
    Convert existing text dates to serial numbers in specified columns

    Args:
        spreadsheet_id: Spreadsheet ID
        sheet_name: Sheet name
        date_columns: List of column letters (e.g., ['B', 'L', 'M', 'N'])
    """
    # 1. Read all data
    # 2. For each date column, convert text to serial
    # 3. Write back using batchUpdate
    # 4. Apply date formatting to columns
```

**Caution:** This is destructive. Test thoroughly before running on production data.

### Decision Record

**Date:** 2025-11-13
**Context:** Discovered during implementation of `append_rows_to_table()` that date formulas produce serial numbers requiring manual formatting, while base date columns store text strings.

**Decision:** Document as technical debt rather than fix immediately due to:
- Token budget constraints (already used 50%)
- Need to test date conversion thoroughly
- Existing data migration risk
- Formatting must be verified across all sheets

**Future action:** Address when:
- Building dashboard/reporting features
- Implementing date-based filters
- Adding time-series analysis
- User requests date range queries

### Testing Checklist

When implementing the fix:
- [ ] Date strings convert to correct serial numbers
- [ ] Serial numbers display with correct formatting (yyyy-mm-dd)
- [ ] Existing formulas still work (=B6+30, etc.)
- [ ] Date filters work (>= date, < date)
- [ ] Date sorting works correctly
- [ ] MONTH(), YEAR() functions work
- [ ] TODAY(), NOW() comparisons work
- [ ] Cross-sheet date references work
- [ ] No data loss during migration
- [ ] All sheets tested (Companies, Contacts, Signals, Interactions)

### References

- Google Sheets date serial numbers: Days since December 30, 1899
- ISO 8601 date format: YYYY-MM-DD
- Google Sheets API: `userEnteredValue.numberValue` for dates
- Current implementation: `google-sheets-api/google_sheets_integration.py:473` (append_rows_to_table)
