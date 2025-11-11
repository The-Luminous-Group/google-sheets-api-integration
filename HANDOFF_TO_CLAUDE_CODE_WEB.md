# Handoff to Claude Code Web

**Date:** 11 November 2025
**From:** Guido (Luminous CTO-in-Residence)
**To:** Claude Code Web
**Task:** Implement Google Sheets API Integration (Phase 1)

---

## Repository

**URL:** https://github.com/The-Luminous-Group/google-sheets-api-integration

**Current state:** Repository created with comprehensive specification

---

## Your Task

Implement **Phase 1 (MVP)** of the Google Sheets API integration as specified in `SPECIFICATION.md`.

### Phase 1 Deliverables

1. **Core functionality:**
   - Service account authentication
   - `read_sheet()` - Read data from sheet
   - `read_sheet_as_dicts()` - Read with column headers as dict keys
   - `append_row()` - Append new row
   - `append_rows()` - Append multiple rows
   - `update_range()` - Update specific cells

2. **Error handling:**
   - Custom exception classes (GoogleSheetsError, GoogleSheetsAuthError, etc.)
   - Proper error messages
   - Return dicts with success/error for AI-friendly usage

3. **Testing:**
   - pytest test suite with mocked Google API calls
   - Test authentication, read operations, write operations
   - Test error cases
   - All tests must pass

4. **Code quality:**
   - Configure ruff and mypy in pyproject.toml
   - All functions have type hints
   - All public functions have docstrings
   - Code passes `ruff check .` and `mypy .`

5. **Documentation:**
   - Comprehensive README.md with:
     - Installation instructions
     - Authentication setup (service account)
     - Usage examples for all core functions
     - Troubleshooting section
   - `docs/setup.md` with detailed setup steps
   - `docs/service-account-setup.md` with Google Cloud setup

6. **Project structure:**
   ```
   google-sheets-api/
   ├── README.md
   ├── pyproject.toml
   ├── requirements.txt
   ├── requirements-dev.txt
   ├── google_sheets_integration.py
   ├── sheets_helper.py
   ├── docs/
   │   ├── setup.md
   │   ├── service-account-setup.md
   │   └── troubleshooting.md
   └── tests/
       ├── __init__.py
       ├── test_google_sheets_integration.py
       └── test_sheets_helper.py
   ```

---

## Important Notes

### Follow Luminous Patterns

This integration should match the style and structure of:
- `linear_API` repository
- `github_api` repository

**Specifically:**
- Same pyproject.toml structure (ruff/mypy config)
- Same documentation style (British English)
- Same error handling patterns (custom exceptions + return dicts)
- Same testing approach (mocked external APIs)

### Authentication Priority

**Phase 1:** Service account only (automation-friendly)
- Read service account JSON from file path
- Support environment variable for path
- Support 1Password CLI integration (`op read`)

**Don't implement OAuth in Phase 1** - that's Phase 3

### YAGNI Principle

**Build only what's specified.** Don't add:
- Batch operations (not needed yet)
- Caching (no performance issues yet)
- Sheet discovery/listing (not in spec)
- Data type validation beyond basics
- Formatting or styling operations

**If in doubt, ask or wait.** Don't guess at requirements.

### Testing Requirements

- Mock all Google API calls using `unittest.mock` or `pytest-mock`
- No real API calls in tests
- Test both success and failure cases
- Cover authentication errors, API errors, not found errors
- Aim for >70% coverage (>80% is Phase 3)

### Dependencies

Use official Google libraries:
- `google-auth` for authentication
- `google-auth-oauthlib` for OAuth (Phase 3)
- `google-api-python-client` for Sheets API

**Don't write custom OAuth flows or API wrappers** - use what Google provides.

---

## Success Criteria

**Phase 1 is complete when:**

1. ✅ All core functions implemented and working
2. ✅ Service account authentication works
3. ✅ All tests passing (`pytest tests/`)
4. ✅ Linting passes (`ruff check .`)
5. ✅ Type checking passes (`mypy .`)
6. ✅ README has clear examples for all operations
7. ✅ Documentation covers service account setup
8. ✅ Code follows Luminous patterns (check linear_API for reference)

**When complete:**
- Create PR to main
- Request review from Guido
- Include test results in PR description

---

## Reference Repositories

For style and structure reference:

**linear_API:**
- https://github.com/The-Luminous-Group/linear-api-integration
- Check: authentication patterns, error handling, README structure

**github_api:**
- https://github.com/The-Luminous-Group/github-api-integration
- Check: testing approach, pyproject.toml config, documentation

---

## Questions?

If anything in SPECIFICATION.md is unclear:
1. Check the reference repositories first
2. If still unclear, ask specific questions
3. Document assumptions in your PR description

---

## Getting Started

1. Clone the repository
2. Read SPECIFICATION.md thoroughly
3. Review linear_API and github_api for patterns
4. Create feature branch: `git checkout -b feat/phase-1-implementation`
5. Implement Phase 1 deliverables
6. Ensure all tests and checks pass
7. Create PR with comprehensive description

Good luck! Looking forward to reviewing your implementation.

— Guido
