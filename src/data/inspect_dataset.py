"""
Inspect and verify the raw TWCS dataset.

Usage:
    python -m src.data.inspect_dataset

Reads  : data/raw/twcs.csv
Writes : reports/dataset_inspection.md
"""

import csv
import sys
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (relative to workspace root, which is the cwd when run as a module)
# ---------------------------------------------------------------------------
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = WORKSPACE_ROOT / "data" / "raw" / "twcs.csv"
REPORT_DIR = WORKSPACE_ROOT / "reports"
REPORT_PATH = REPORT_DIR / "dataset_inspection.md"

EXPECTED_COLUMNS = [
    "tweet_id",
    "author_id",
    "inbound",
    "created_at",
    "text",
    "response_tweet_id",
    "in_response_to_tweet_id",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def detect_encoding(path: Path, sample_bytes: int = 1_000_000) -> str:
    """Try UTF-8 first; fall back to latin-1 (which never fails)."""
    with open(path, "rb") as f:
        raw = f.read(sample_bytes)
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass
    try:
        raw.decode("utf-8-sig")
        return "utf-8-sig"
    except UnicodeDecodeError:
        pass
    # latin-1 accepts any byte sequence
    return "latin-1"


def _is_int(s: str) -> bool:
    try:
        int(s.strip())
        return True
    except ValueError:
        return False


def _is_float(s: str) -> bool:
    try:
        float(s.strip())
        return True
    except ValueError:
        return False


def inspect(path: Path) -> dict:
    """Read the CSV in a single streaming pass and collect all stats."""
    encoding = detect_encoding(path)
    print(f"Detected encoding: {encoding}")

    first_rows: list[dict] = []
    row_count = 0
    col_names: list[str] = []
    missing_counts: Counter = Counter()
    duplicate_count = 0
    seen_rows: set[int] = set()
    unique_tweet_ids: set[str] = set()
    inbound_count = 0
    outbound_count = 0
    sample_values: dict[str, list[str]] = {}

    inbound_col: str | None = None
    tweet_id_col: str | None = None

    with open(path, "r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        col_names = list(reader.fieldnames or [])

        # Locate key columns (case-insensitive)
        col_lower_map = {c.lower(): c for c in col_names}
        inbound_col = col_lower_map.get("inbound")
        tweet_id_col = col_lower_map.get("tweet_id")

        for col in col_names:
            sample_values[col] = []

        for row in reader:
            row_count += 1

            # --- first 5 rows ---
            if row_count <= 5:
                first_rows.append(dict(row))

            # --- sample values for type inference (first 20 non-empty) ---
            if row_count <= 100:
                for col in col_names:
                    val = row.get(col, "")
                    if val.strip() and len(sample_values[col]) < 20:
                        sample_values[col].append(val)

            # --- missing values ---
            for col in col_names:
                val = row.get(col)
                if val is None or val.strip() == "":
                    missing_counts[col] += 1

            # --- duplicates (hash of full row) ---
            row_hash = hash(tuple(row.get(c, "") for c in col_names))
            if row_hash in seen_rows:
                duplicate_count += 1
            else:
                seen_rows.add(row_hash)

            # --- unique tweet IDs ---
            if tweet_id_col:
                tid = row.get(tweet_id_col, "").strip()
                if tid:
                    unique_tweet_ids.add(tid)

            # --- inbound / outbound ---
            if inbound_col:
                ib = row.get(inbound_col, "").strip().lower()
                if ib in ("true", "1", "yes"):
                    inbound_count += 1
                elif ib in ("false", "0", "no"):
                    outbound_count += 1

            # Progress indicator every 500k rows
            if row_count % 500_000 == 0:
                print(f"  ... processed {row_count:,} rows")

    # --- infer data types from sample values ---
    col_types: dict[str, str] = {}
    for col in col_names:
        vals = [v for v in sample_values[col] if v.strip()]
        if not vals:
            col_types[col] = "unknown (all sampled values empty)"
            continue
        all_int = all(_is_int(v) for v in vals)
        all_float = all(_is_float(v) for v in vals)
        all_bool = all(v.strip().lower() in ("true", "false") for v in vals)
        if all_bool:
            col_types[col] = "bool"
        elif all_int:
            col_types[col] = "int"
        elif all_float:
            col_types[col] = "float"
        else:
            col_types[col] = "str"

    return {
        "encoding": encoding,
        "row_count": row_count,
        "col_count": len(col_names),
        "col_names": col_names,
        "first_rows": first_rows,
        "col_types": col_types,
        "missing_counts": dict(missing_counts),
        "duplicate_count": duplicate_count,
        "unique_tweet_ids": len(unique_tweet_ids),
        "inbound_count": inbound_count,
        "outbound_count": outbound_count,
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def format_report(stats: dict) -> str:
    lines: list[str] = []
    lines.append("# Dataset Inspection Report")
    lines.append("")
    lines.append(f"**File encoding:** {stats['encoding']}")
    lines.append(f"**Number of rows:** {stats['row_count']:,}")
    lines.append(f"**Number of columns:** {stats['col_count']}")
    lines.append("")

    # Column names
    lines.append("## Column Names")
    lines.append("")
    for i, col in enumerate(stats["col_names"], 1):
        lines.append(f"{i}. `{col}`")
    lines.append("")

    # Expected columns check
    lines.append("## Expected Columns Check")
    lines.append("")
    found = set(c.lower() for c in stats["col_names"])
    for col in EXPECTED_COLUMNS:
        status = "✅ present" if col.lower() in found else "❌ **MISSING**"
        lines.append(f"- `{col}`: {status}")
    lines.append("")

    # Data types
    lines.append("## Inferred Data Types")
    lines.append("")
    lines.append("| Column | Type |")
    lines.append("|--------|------|")
    for col in stats["col_names"]:
        lines.append(f"| `{col}` | {stats['col_types'].get(col, 'unknown')} |")
    lines.append("")

    # Missing values
    lines.append("## Missing-Value Counts")
    lines.append("")
    lines.append("| Column | Missing |")
    lines.append("|--------|---------|")
    for col in stats["col_names"]:
        cnt = stats["missing_counts"].get(col, 0)
        lines.append(f"| `{col}` | {cnt:,} |")
    lines.append("")

    # Duplicate rows
    lines.append("## Duplicate Rows")
    lines.append("")
    lines.append(f"**Duplicate-row count:** {stats['duplicate_count']:,}")
    lines.append("")

    # Unique tweet IDs
    lines.append("## Unique Tweet IDs")
    lines.append("")
    lines.append(f"**Unique tweet IDs:** {stats['unique_tweet_ids']:,}")
    lines.append("")

    # Inbound / Outbound
    lines.append("## Inbound vs Outbound Tweets")
    lines.append("")
    lines.append(f"- **Inbound:** {stats['inbound_count']:,}")
    lines.append(f"- **Outbound:** {stats['outbound_count']:,}")
    lines.append("")

    # First 5 rows
    lines.append("## First 5 Rows")
    lines.append("")
    if stats["first_rows"]:
        cols = stats["col_names"]
        header = "| " + " | ".join(f"`{c}`" for c in cols) + " |"
        sep = "| " + " | ".join("---" for _ in cols) + " |"
        lines.append(header)
        lines.append(sep)
        for row in stats["first_rows"]:
            cells = []
            for c in cols:
                val = str(row.get(c, ""))
                if len(val) > 80:
                    val = val[:77] + "..."
                val = val.replace("|", "\\|")
                cells.append(val)
            lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    return "\n".join(lines)


def print_summary(stats: dict) -> None:
    print("=" * 60)
    print("DATASET INSPECTION SUMMARY")
    print("=" * 60)
    print(f"Rows            : {stats['row_count']:,}")
    print(f"Columns         : {stats['col_count']}")
    print(f"Column names    : {stats['col_names']}")
    print()
    print("--- First 5 rows ---")
    for i, row in enumerate(stats["first_rows"], 1):
        print(f"  Row {i}: {row}")
    print()
    print("--- Data types (inferred from sample) ---")
    for col, dtype in stats["col_types"].items():
        print(f"  {col:30s} : {dtype}")
    print()
    print("--- Missing-value counts ---")
    for col in stats["col_names"]:
        cnt = stats["missing_counts"].get(col, 0)
        print(f"  {col:30s} : {cnt:,}")
    print()
    print(f"Duplicate rows  : {stats['duplicate_count']:,}")
    print(f"Unique tweet IDs: {stats['unique_tweet_ids']:,}")
    print(f"Inbound tweets  : {stats['inbound_count']:,}")
    print(f"Outbound tweets : {stats['outbound_count']:,}")
    print()

    # Expected columns
    found = set(c.lower() for c in stats["col_names"])
    print("--- Expected columns check ---")
    for col in EXPECTED_COLUMNS:
        status = "PRESENT" if col.lower() in found else "MISSING"
        print(f"  {col:30s} : {status}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not CSV_PATH.exists():
        print(f"ERROR: Could not find {CSV_PATH}")
        sys.exit(1)

    print(f"Inspecting: {CSV_PATH}")
    file_size_mb = CSV_PATH.stat().st_size / (1024 * 1024)
    print(f"File size : {file_size_mb:.1f} MB")
    print()

    stats = inspect(CSV_PATH)
    print_summary(stats)

    # Write report
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_text = format_report(stats)
    REPORT_PATH.write_text(report_text, encoding="utf-8")
    print(f"\nReport written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
