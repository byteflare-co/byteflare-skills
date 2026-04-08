"""Spec document and code consistency check script (reference implementation).

Example implementation for the addplus-proxy project.
Used as a reference when /spec-skills-generator generates a customized
check_spec_drift.py for each project.

Main checks:
  1. Component count matching (actual entities in code vs table rows in spec)
  2. File name coverage (files that exist in code but are not listed in spec)
  3. Spec metadata freshness (whether "Last verified" date is within 30 days)

Customization points:
  - Adjust PROJECT_ROOT, SPEC_DIR, source directories, etc. to match your project
  - Add or modify _count_*() functions to match your project's component structure
  - _count_table_rows() is generic and can be reused in most projects as-is
  - Adjust regex patterns in _count_spec_*() functions to match your spec headings
  - If there is no IaC, omit the Terraform-related checks

Usage:
    python scripts/check_spec_drift.py
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================================
# Project-specific path settings (customization point)
# ============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = PROJECT_ROOT / "docs" / "specification"
LAMBDA_DIR = PROJECT_ROOT / "lambda_functions"
LAYER_DIR = PROJECT_ROOT / "lambda_layer" / "python"
TERRAFORM_DIR = PROJECT_ROOT / "terraform"

OVERVIEW = SPEC_DIR / "01_overview.md"
BUSINESS = SPEC_DIR / "02_business_spec.md"
TECHNICAL = SPEC_DIR / "03_technical_spec.md"

IGNORED_FILES = {"__init__.py"}
IGNORED_DIRS = {"__pycache__", "__init__.py"}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Component count matching
# ---------------------------------------------------------------------------
# Customization point: Add or modify _count_*() functions
# to match your project's component structure


def _count_lambda_dirs() -> list[str]:
    """Get Lambda function directory names under lambda_functions/."""
    return sorted(
        d.name
        for d in LAMBDA_DIR.iterdir()
        if d.is_dir() and d.name not in IGNORED_DIRS
    )


def _count_layer_modules() -> list[str]:
    """Get shared module names under lambda_layer/python/."""
    return sorted(
        f.name for f in LAYER_DIR.glob("*.py") if f.name not in IGNORED_FILES
    )


def _count_dynamodb_tables_in_terraform() -> list[str]:
    """Get aws_dynamodb_table resource names from terraform/dynamodb.tf."""
    content = _read(TERRAFORM_DIR / "dynamodb.tf")
    return re.findall(r'resource\s+"aws_dynamodb_table"\s+"(\w+)"', content)


def _count_api_routes_in_terraform() -> list[str]:
    """Get aws_apigatewayv2_route resource names from terraform/api_gateway.tf."""
    content = _read(TERRAFORM_DIR / "api_gateway.tf")
    return re.findall(r'resource\s+"aws_apigatewayv2_route"\s+"(\w+)"', content)


# ---------------------------------------------------------------------------
# Generic helper: Count spec table rows
# ---------------------------------------------------------------------------
# This function can be reused in most projects as-is


def _count_table_rows(text: str, section_pattern: str, stop_pattern: str) -> int:
    """Count data rows in a markdown table within a spec document.

    Detects section start with section_pattern and end with stop_pattern.
    Returns the number of data rows excluding the table header row (|---|).
    """
    in_section = False
    in_table = False
    count = 0
    for line in text.splitlines():
        if not in_section:
            if re.search(section_pattern, line):
                in_section = True
            continue
        if re.search(stop_pattern, line):
            break
        stripped = line.strip()
        if stripped.startswith("|") and not re.match(r"^\|[\s\-|]+\|$", stripped):
            if in_table:
                count += 1
            else:
                in_table = True  # First row is the table header
        elif in_table and not stripped.startswith("|"):
            break  # Exited the table
    return count


# ---------------------------------------------------------------------------
# Customization point: Regex patterns matched to spec section headings
# ---------------------------------------------------------------------------


def _count_spec_lambda_functions(overview_text: str) -> int:
    """Count rows in the Lambda functions table in 01_overview.md (API + batch)."""
    api_count = _count_table_rows(
        overview_text,
        r"####\s+API\s+Endpoint\s+Integration",
        r"####\s+Monthly\s+Rank\s+Batch",
    )
    batch_count = _count_table_rows(
        overview_text,
        r"####\s+Monthly\s+Rank\s+Batch",
        r"###\s+3\.2",
    )
    return api_count + batch_count


def _count_spec_layer_modules(overview_text: str) -> int:
    """Count rows in the shared layer modules table in 01_overview.md."""
    return _count_table_rows(
        overview_text,
        r"###\s+3\.2\s+Shared\s+Layer\s+Modules",
        r"###\s+3\.3",
    )


def _count_spec_dynamodb_tables(overview_text: str) -> int:
    """Count rows in the DynamoDB tables table in 01_overview.md."""
    return _count_table_rows(
        overview_text,
        r"###\s+3\.3\s+DynamoDB",
        r"###\s+3\.4",
    )


# ---------------------------------------------------------------------------
# 2. File name coverage check
# ---------------------------------------------------------------------------


def _find_missing_in_spec(names: list[str], *spec_texts: str) -> list[str]:
    """Check whether file/directory names appear in any of the spec texts."""
    combined = "\n".join(spec_texts)
    missing = []
    for name in names:
        search_name = name.replace(".py", "")
        if search_name not in combined:
            missing.append(name)
    return missing


# ---------------------------------------------------------------------------
# 3. Spec metadata freshness check
# ---------------------------------------------------------------------------


def _parse_last_verified_date(spec_text: str) -> datetime | None:
    """Parse 'Last verified: YYYY-MM-DD' from the end of a spec document."""
    match = re.search(r"Last verified:\s*(\d{4}-\d{2}-\d{2})", spec_text)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d")
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print("=== Spec Document Consistency Check ===\n")

    warnings = 0

    overview_text = _read(OVERVIEW)
    technical_text = _read(TECHNICAL)

    # --- 1. Component count matching ---
    lambda_dirs = _count_lambda_dirs()
    layer_modules = _count_layer_modules()
    dynamodb_tables = _count_dynamodb_tables_in_terraform()
    api_routes = _count_api_routes_in_terraform()

    spec_lambda_count = _count_spec_lambda_functions(overview_text)
    spec_layer_count = _count_spec_layer_modules(overview_text)
    spec_dynamodb_count = _count_spec_dynamodb_tables(overview_text)

    # Lambda functions
    code_lambda_count = len(lambda_dirs)
    if code_lambda_count == spec_lambda_count:
        print(f"[OK] Lambda functions: {code_lambda_count} (code) = {spec_lambda_count} (spec)")
    else:
        print(
            f"[WARN] Lambda functions: {code_lambda_count} (code) != {spec_lambda_count} (spec) <- needs review"
        )
        warnings += 1

    # Shared modules
    code_layer_count = len(layer_modules)
    if code_layer_count == spec_layer_count:
        print(f"[OK] Shared modules: {code_layer_count} (code) = {spec_layer_count} (spec)")
    else:
        print(
            f"[WARN] Shared modules: {code_layer_count} (code) != {spec_layer_count} (spec) <- needs review"
        )
        warnings += 1

    # DynamoDB tables
    code_dynamodb_count = len(dynamodb_tables)
    if code_dynamodb_count == spec_dynamodb_count:
        print(f"[OK] DynamoDB tables: {code_dynamodb_count} (code) = {spec_dynamodb_count} (spec)")
    else:
        print(
            f"[WARN] DynamoDB tables: {code_dynamodb_count} (code) != {spec_dynamodb_count} (spec) <- needs review"
        )
        warnings += 1

    # API routes
    code_api_count = len(api_routes)
    api_sections = re.findall(r"###\s+1\.\d+\s+(?:POST|GET)\s+/", technical_text)
    spec_api_count = len(api_sections)
    if code_api_count == spec_api_count:
        print(f"[OK] API routes: {code_api_count} (code) = {spec_api_count} (spec)")
    else:
        print(
            f"[WARN] API routes: {code_api_count} (code) != {spec_api_count} (spec) <- needs review"
        )
        warnings += 1

    # --- 2. File name coverage check ---
    missing_lambdas = _find_missing_in_spec(lambda_dirs, technical_text, overview_text)
    missing_modules = _find_missing_in_spec(layer_modules, technical_text, overview_text)

    if missing_lambdas or missing_modules:
        print("\nFiles not listed in spec:")
        for name in missing_lambdas:
            print(f"  - lambda_functions/{name}/ -> not listed in 03_technical_spec.md")
            warnings += 1
        for name in missing_modules:
            print(f"  - lambda_layer/python/{name} -> not listed in 03_technical_spec.md")
            warnings += 1

    # --- 3. Spec metadata freshness check ---
    today = datetime.now()
    threshold = timedelta(days=30)

    for spec_file in [OVERVIEW, BUSINESS, TECHNICAL]:
        spec_text = _read(spec_file)
        last_verified = _parse_last_verified_date(spec_text)
        if last_verified is None:
            print(f"\n[WARN] Last verified date not set: {spec_file.name}")
            warnings += 1
        elif today - last_verified > threshold:
            print(
                f"[WARN] Last verified date is over 30 days old: {spec_file.name} (last: {last_verified.strftime('%Y-%m-%d')})"
            )
            warnings += 1

    # --- Result summary ---
    print()
    if warnings == 0:
        print("Result: All OK - spec documents and code are consistent")
    else:
        print(f"Result: {warnings} warning(s) found - consider updating spec documents")

    return 1 if warnings > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
