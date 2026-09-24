"""
Extract and reconstruct AmazonHelp customer-support conversations from TWCS.

Two-pass memory-efficient approach:
  Pass 1 – Build Union-Find and identify AmazonHelp conversations (lightweight).
  Pass 2 – Re-read CSV, store full data only for AmazonHelp conversations.

Usage:
    python -m src.data.extract_brand

Outputs:
    data/processed/amazonhelp_conversations.jsonl
    data/processed/amazonhelp_conversations.csv
    reports/amazonhelp_conversation_analysis.md
"""

import csv
import io
import json
import random
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).resolve().parents[2]
CSV_PATH  = WORKSPACE / "data" / "raw" / "twcs.csv"
OUT_JSONL = WORKSPACE / "data" / "processed" / "amazonhelp_conversations.jsonl"
OUT_CSV   = WORKSPACE / "data" / "processed" / "amazonhelp_conversations.csv"
REPORT    = WORKSPACE / "reports" / "amazonhelp_conversation_analysis.md"

BRAND = "AmazonHelp"
BRAND_LOWER = BRAND.lower()
TWITTER_DATE_FMT = "%a %b %d %H:%M:%S %z %Y"


# ── Union-Find ─────────────────────────────────────────────────────────────
class UnionFind:
    """Disjoint-set with path compression and union by rank."""
    __slots__ = ("p", "r")

    def __init__(self):
        self.p: dict[int, int] = {}
        self.r: dict[int, int] = {}

    def find(self, x: int) -> int:
        if x not in self.p:
            self.p[x] = x
            self.r[x] = 0
        root = x
        while self.p[root] != root:
            root = self.p[root]
        while self.p[x] != root:
            self.p[x], x = root, self.p[x]
        return root

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1


# ── Utility functions (importable for tests) ──────────────────────────────
def _safe_int(val: str) -> int | None:
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def parse_twitter_date(s: str) -> datetime | None:
    """Parse a Twitter-style date string into a timezone-aware datetime."""
    if not s or not s.strip():
        return None
    try:
        return datetime.strptime(s.strip(), TWITTER_DATE_FMT)
    except (ValueError, TypeError):
        return None


def identify_speaker(author_id: str, brand_accounts_lower: set[str]) -> str:
    """Return 'brand' if author is a known brand account, else 'customer'."""
    return "brand" if author_id.lower() in brand_accounts_lower else "customer"


def sort_turns(turns: list[dict]) -> list[dict]:
    """Sort turns chronologically, with tweet_id as tiebreaker.

    Turns with unparseable dates are placed last, ordered by tweet_id.
    """
    def _key(t):
        dt = t.get("_dt")
        if dt is not None:
            return (0, dt, t["tweet_id"])
        return (1, datetime.min, t["tweet_id"])
    return sorted(turns, key=_key)


def validate_conversation(turns: list[dict], conv_tid_set: set[int]) -> list[str]:
    """Return a list of flag reasons for structural issues."""
    flags: list[str] = []

    # Unparseable timestamps
    bad_ts = sum(1 for t in turns if t.get("_dt") is None)
    if bad_ts:
        flags.append(f"{bad_ts}/{len(turns)} unparseable timestamps")

    # References to tweets missing from this conversation
    missing = 0
    for t in turns:
        irt_str = t.get("in_response_to_tweet_id", "")
        if irt_str:
            irt = _safe_int(irt_str)
            if irt is not None and irt not in conv_tid_set:
                missing += 1
    if missing:
        flags.append(f"{missing} referenced tweet(s) outside conversation")

    return flags


def build_conversation(
    tweet_data: dict[int, dict],
    tweet_ids: list[int],
    conv_id: str,
    brand_accounts_lower: set[str],
) -> dict:
    """Build a structured conversation dict from raw tweet data.

    Parameters
    ----------
    tweet_data : mapping of tid -> tweet dict (must contain keys:
                 author_id, inbound, created_at, text,
                 response_tweet_id, in_response_to_tweet_id)
    tweet_ids  : tweet IDs belonging to this conversation
    conv_id    : conversation identifier string
    brand_accounts_lower : lowercased brand author-id set
    """
    # Build turns with temporary _dt field for sorting
    turns: list[dict] = []
    brand_authors: set[str] = set()
    customer_authors: set[str] = set()

    for tid in tweet_ids:
        tw = tweet_data.get(tid)
        if tw is None:
            continue
        speaker = identify_speaker(tw["author_id"], brand_accounts_lower)
        dt = parse_twitter_date(tw["created_at"])

        turns.append({
            "tweet_id": tid,
            "author_id": tw["author_id"],
            "speaker": speaker,
            "inbound": tw["inbound"],
            "text": tw["text"],
            "created_at": tw["created_at"],
            "response_tweet_id": tw["response_tweet_id"],
            "in_response_to_tweet_id": tw["in_response_to_tweet_id"],
            "_dt": dt,
        })
        (brand_authors if speaker == "brand" else customer_authors).add(tw["author_id"])

    if not turns:
        return None

    # Validate before we strip internal fields
    conv_tid_set = set(tweet_ids)
    flags = validate_conversation(turns, conv_tid_set)

    # Sort & assign turn numbers
    turns = sort_turns(turns)
    for i, t in enumerate(turns, 1):
        t["turn_number"] = i

    # Metadata
    has_brand = any(t["speaker"] == "brand" for t in turns)
    has_customer = any(t["speaker"] == "customer" for t in turns)
    brand_responded = has_brand and has_customer
    num_turns = len(turns)
    is_multi_turn = num_turns >= 3 and brand_responded

    # Check for customer->brand sequence (resolution suitability)
    has_cust_brand_seq = False
    for i in range(len(turns) - 1):
        if turns[i]["speaker"] == "customer" and turns[i + 1]["speaker"] == "brand":
            has_cust_brand_seq = True
            break

    customer_msg_count = sum(1 for t in turns if t["speaker"] == "customer")
    suitable_for_resolution = (
        is_multi_turn
        and brand_responded
        and has_cust_brand_seq
        and not flags
    )

    start_time = turns[0]["created_at"]
    end_time = turns[-1]["created_at"]
    customer_author = sorted(customer_authors)[0] if customer_authors else ""
    brand_author = sorted(brand_authors)[0] if brand_authors else ""

    # Strip internal _dt before output
    clean_turns = []
    for t in turns:
        ct = {k: v for k, v in t.items() if k != "_dt"}
        clean_turns.append(ct)

    return {
        "conversation_id": conv_id,
        "customer_author": customer_author,
        "brand_author": brand_author,
        "start_time": start_time,
        "end_time": end_time,
        "num_turns": num_turns,
        "brand_responded": brand_responded,
        "is_multi_turn": is_multi_turn,
        "customer_message_count": customer_msg_count,
        "is_flagged": bool(flags),
        "flag_reason": "; ".join(flags),
        "suitable_for_resolution": suitable_for_resolution,
        "turns": clean_turns,
    }


# ── Example selection ──────────────────────────────────────────────────────
def select_examples(conversations: list[dict], n: int = 20, seed: int = 42) -> list[dict]:
    """Select *n* representative conversations across length buckets.

    Buckets: short (2), medium (3-5), long (6-10), very long (11+).
    Selects from quality conversations (brand responded, not flagged).
    """
    rng = random.Random(seed)

    quality = [c for c in conversations
               if c["brand_responded"] and not c["is_flagged"] and c["num_turns"] >= 2]

    buckets = {
        "short": [c for c in quality if c["num_turns"] == 2],
        "medium": [c for c in quality if 3 <= c["num_turns"] <= 5],
        "long": [c for c in quality if 6 <= c["num_turns"] <= 10],
        "very_long": [c for c in quality if c["num_turns"] >= 11],
    }

    per_bucket = max(1, n // len(buckets))
    examples = []

    for label in ["short", "medium", "long", "very_long"]:
        pool = buckets[label]
        k = min(per_bucket, len(pool))
        if k > 0:
            examples.extend(rng.sample(pool, k))

    # Fill remaining slots from largest available bucket
    remaining = n - len(examples)
    if remaining > 0:
        all_remaining = [c for c in quality if c not in examples]
        if all_remaining:
            examples.extend(rng.sample(all_remaining, min(remaining, len(all_remaining))))

    return examples[:n]


# ── Export helpers ─────────────────────────────────────────────────────────
def export_jsonl(conversations: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for conv in conversations:
            f.write(json.dumps(conv, ensure_ascii=False) + "\n")


def export_csv(conversations: list[dict], path: Path) -> None:
    """Flatten: one row per turn, conversation metadata repeated."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "conversation_id", "turn_number", "tweet_id", "author_id", "speaker",
        "inbound", "created_at", "text", "response_tweet_id",
        "in_response_to_tweet_id", "customer_author", "brand_author",
        "conversation_start", "conversation_end", "num_turns",
        "brand_responded", "is_multi_turn", "is_flagged", "flag_reason",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for conv in conversations:
            for turn in conv["turns"]:
                writer.writerow({
                    "conversation_id": conv["conversation_id"],
                    "turn_number": turn["turn_number"],
                    "tweet_id": turn["tweet_id"],
                    "author_id": turn["author_id"],
                    "speaker": turn["speaker"],
                    "inbound": turn["inbound"],
                    "created_at": turn["created_at"],
                    "text": turn["text"],
                    "response_tweet_id": turn.get("response_tweet_id", ""),
                    "in_response_to_tweet_id": turn.get("in_response_to_tweet_id", ""),
                    "customer_author": conv["customer_author"],
                    "brand_author": conv["brand_author"],
                    "conversation_start": conv["start_time"],
                    "conversation_end": conv["end_time"],
                    "num_turns": conv["num_turns"],
                    "brand_responded": conv["brand_responded"],
                    "is_multi_turn": conv["is_multi_turn"],
                    "is_flagged": conv["is_flagged"],
                    "flag_reason": conv["flag_reason"],
                })


# ── Report ─────────────────────────────────────────────────────────────────
def generate_report(conversations: list[dict], examples: list[dict]) -> str:
    L: list[str] = []

    total = len(conversations)
    single = sum(1 for c in conversations if not c["is_multi_turn"])
    multi = sum(1 for c in conversations if c["is_multi_turn"])
    lengths = [c["num_turns"] for c in conversations]
    avg_turns = statistics.mean(lengths) if lengths else 0
    med_turns = statistics.median(lengths) if lengths else 0
    max_turns = max(lengths) if lengths else 0
    customers = set()
    brand_accts = set()
    for c in conversations:
        if c["customer_author"]:
            customers.add(c["customer_author"])
        if c["brand_author"]:
            brand_accts.add(c["brand_author"])
    responded = sum(1 for c in conversations if c["brand_responded"])
    cust_multi_msg = sum(1 for c in conversations if c.get("customer_message_count", 0) >= 2)
    suitable = sum(1 for c in conversations if c.get("suitable_for_resolution", False))
    flagged = sum(1 for c in conversations if c["is_flagged"])

    # Length distribution
    length_dist: Counter = Counter()
    for ln in lengths:
        if ln == 1:
            length_dist["1 turn"] += 1
        elif ln == 2:
            length_dist["2 turns"] += 1
        elif ln <= 5:
            length_dist["3-5 turns"] += 1
        elif ln <= 10:
            length_dist["6-10 turns"] += 1
        elif ln <= 20:
            length_dist["11-20 turns"] += 1
        else:
            length_dist["21+ turns"] += 1

    L.append("# AmazonHelp Conversation Analysis\n")

    L.append("## Summary Statistics\n")
    L.append("| Metric | Value |")
    L.append("|--------|-------|")
    L.append(f"| Total conversations | {total:,} |")
    L.append(f"| Single-turn conversations | {single:,} |")
    L.append(f"| Multi-turn conversations | {multi:,} |")
    L.append(f"| Average turns per conversation | {avg_turns:.2f} |")
    L.append(f"| Median turns per conversation | {med_turns:.1f} |")
    L.append(f"| Maximum conversation length | {max_turns} turns |")
    L.append(f"| Unique customers | {len(customers):,} |")
    L.append(f"| AmazonHelp support accounts | {len(brand_accts):,} |")
    L.append(f"| Brand responded | {responded:,} ({responded/total*100:.1f}%) |")
    L.append(f"| Customer sent multiple messages | {cust_multi_msg:,} ({cust_multi_msg/total*100:.1f}%) |")
    L.append(f"| Suitable for resolution learning | {suitable:,} ({suitable/total*100:.1f}%) |")
    L.append(f"| Flagged (structural issues) | {flagged:,} ({flagged/total*100:.1f}%) |")
    L.append("")

    L.append("## Conversation Length Distribution\n")
    L.append("| Length Bucket | Count | Percentage |")
    L.append("|--------------|-------|------------|")
    for bucket in ["1 turn", "2 turns", "3-5 turns", "6-10 turns", "11-20 turns", "21+ turns"]:
        cnt = length_dist.get(bucket, 0)
        pct = cnt / total * 100 if total else 0
        bar = "#" * int(pct / 2)
        L.append(f"| {bucket} | {cnt:,} | {pct:.1f}% {bar} |")
    L.append("")

    # Examples
    L.append("## 20 Representative Conversations\n")
    L.append("The following examples were sampled across short, medium, long, and very long")
    L.append("conversations to show the diversity of AmazonHelp support interactions.\n")

    for idx, conv in enumerate(examples, 1):
        nt = conv["num_turns"]
        if nt <= 2:
            cat = "Short"
        elif nt <= 5:
            cat = "Medium"
        elif nt <= 10:
            cat = "Long"
        else:
            cat = "Very long"

        L.append(f"### Example {idx} -- {cat} ({nt} turns)\n")
        L.append(f"**Conversation:** `{conv['conversation_id']}` | "
                 f"**Customer:** `{conv['customer_author']}` | "
                 f"**Brand responded:** {'Yes' if conv['brand_responded'] else 'No'}")
        if conv["is_flagged"]:
            L.append(f"**Flags:** {conv['flag_reason']}")
        L.append("")
        L.append("| Turn | Speaker | Text |")
        L.append("|------|---------|------|")
        for turn in conv["turns"]:
            text = turn["text"]
            if len(text) > 200:
                text = text[:197] + "..."
            text = text.replace("|", "\\|").replace("\n", " ")
            L.append(f"| {turn['turn_number']} | {turn['speaker']} | {text} |")
        L.append("")

    return "\n".join(L)


# ── Main ───────────────────────────────────────────────────────────────────
def main() -> None:
    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} not found"); sys.exit(1)

    # Force UTF-8 stdout on Windows
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print(f"Extracting {BRAND} conversations from: {CSV_PATH}")
    print(f"File size: {CSV_PATH.stat().st_size / 1024**2:.1f} MB\n")

    # ================================================================
    # PASS 1 -- lightweight: build Union-Find, identify AmazonHelp tids
    # ================================================================
    print("Pass 1: Building conversation graph (lightweight) ...")
    uf = UnionFind()
    amazon_tids: set[int] = set()

    with open(CSV_PATH, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for i, row in enumerate(reader, 1):
            tid = _safe_int(row["tweet_id"].strip())
            if tid is None:
                continue
            author = row["author_id"].strip()

            # Always register AmazonHelp tweets in UF
            if author.lower() == BRAND_LOWER:
                amazon_tids.add(tid)
                uf.find(tid)

            # Add edges
            irt = row.get("in_response_to_tweet_id", "").strip()
            if irt:
                irt_int = _safe_int(irt)
                if irt_int is not None:
                    uf.union(tid, irt_int)
            rt = row.get("response_tweet_id", "").strip()
            if rt:
                rt_int = _safe_int(rt)
                if rt_int is not None:
                    uf.union(tid, rt_int)

            if i % 500_000 == 0:
                print(f"  ... {i:,} rows")

    print(f"  AmazonHelp tweets: {len(amazon_tids):,}")

    # Find all conversation roots containing AmazonHelp
    amazon_roots: set[int] = set()
    for tid in amazon_tids:
        amazon_roots.add(uf.find(tid))
    print(f"  AmazonHelp conversation roots: {len(amazon_roots):,}")

    # Find ALL tweet IDs in those conversations
    conv_map: dict[int, int] = {}  # tid -> root
    for tid in uf.p:
        root = uf.find(tid)
        if root in amazon_roots:
            conv_map[tid] = root

    del uf, amazon_tids  # free ~500 MB
    print(f"  Total tweets in AmazonHelp conversations: {len(conv_map):,}\n")

    # ================================================================
    # PASS 2 -- read full data for AmazonHelp conversation tweets only
    # ================================================================
    print("Pass 2: Reading full tweet data for AmazonHelp conversations ...")
    tweet_data: dict[int, dict] = {}

    with open(CSV_PATH, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for i, row in enumerate(reader, 1):
            tid = _safe_int(row["tweet_id"].strip())
            if tid is None or tid not in conv_map:
                continue
            tweet_data[tid] = {
                "author_id": row["author_id"].strip(),
                "inbound": row["inbound"].strip().lower() in ("true", "1", "yes"),
                "created_at": row.get("created_at", "").strip(),
                "text": row.get("text", ""),
                "response_tweet_id": row.get("response_tweet_id", "").strip(),
                "in_response_to_tweet_id": row.get("in_response_to_tweet_id", "").strip(),
            }
            if i % 500_000 == 0:
                print(f"  ... {i:,} rows scanned")

    print(f"  Loaded {len(tweet_data):,} tweets\n")

    # ================================================================
    # Build conversations
    # ================================================================
    print("Building conversations ...")
    groups: dict[int, list[int]] = defaultdict(list)
    for tid, root in conv_map.items():
        if tid in tweet_data:
            groups[root].append(tid)

    del conv_map  # free memory

    brand_lower_set = {BRAND_LOWER}
    conversations: list[dict] = []
    for root, tids in groups.items():
        conv = build_conversation(tweet_data, tids, f"conv_{root}", brand_lower_set)
        if conv is not None:
            conversations.append(conv)

    del tweet_data, groups

    # Deduplicate by tweet-id set (safety check)
    seen_tid_sets: set[frozenset] = set()
    deduped: list[dict] = []
    for conv in conversations:
        tid_key = frozenset(t["tweet_id"] for t in conv["turns"])
        if tid_key not in seen_tid_sets:
            seen_tid_sets.add(tid_key)
            deduped.append(conv)
    dup_count = len(conversations) - len(deduped)
    conversations = deduped

    # Sort conversations by start time for stable output
    conversations.sort(key=lambda c: c["start_time"])

    print(f"  Conversations: {len(conversations):,}")
    if dup_count:
        print(f"  Duplicates removed: {dup_count}")

    # ================================================================
    # Export
    # ================================================================
    print("\nExporting ...")
    export_jsonl(conversations, OUT_JSONL)
    print(f"  JSONL -> {OUT_JSONL}")
    export_csv(conversations, OUT_CSV)
    print(f"  CSV   -> {OUT_CSV}")

    # ================================================================
    # Report & examples
    # ================================================================
    examples = select_examples(conversations, n=20)
    report_text = generate_report(conversations, examples)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report_text, encoding="utf-8")
    print(f"  Report -> {REPORT}")

    # ================================================================
    # Console summary
    # ================================================================
    total = len(conversations)
    multi = sum(1 for c in conversations if c["is_multi_turn"])
    single = total - multi
    lengths = [c["num_turns"] for c in conversations]
    suitable = sum(1 for c in conversations if c.get("suitable_for_resolution"))

    print("\n" + "=" * 70)
    print("AMAZONHELP CONVERSATION EXTRACTION SUMMARY")
    print("=" * 70)
    print(f"Total conversations       : {total:,}")
    print(f"Single-turn               : {single:,}")
    print(f"Multi-turn                : {multi:,}")
    print(f"Average turns             : {statistics.mean(lengths):.2f}")
    print(f"Median turns              : {statistics.median(lengths):.1f}")
    print(f"Max turns                 : {max(lengths)}")
    print(f"Suitable for resolution   : {suitable:,}")
    print("=" * 70)

    # Print examples
    print(f"\n{'='*70}")
    print(f"20 REPRESENTATIVE CONVERSATIONS")
    print(f"{'='*70}")
    for idx, conv in enumerate(examples, 1):
        nt = conv["num_turns"]
        print(f"\n--- Example {idx} ({nt} turns) | {conv['conversation_id']} ---")
        for turn in conv["turns"]:
            speaker = "CUST " if turn["speaker"] == "customer" else "BRAND"
            text = turn["text"]
            if len(text) > 300:
                text = text[:297] + "..."
            print(f"  [{turn['turn_number']}] {speaker}: {text}")


if __name__ == "__main__":
    main()
