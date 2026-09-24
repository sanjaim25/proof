"""
Brand analysis for the TWCS dataset.

Streams data/raw/twcs.csv in a single pass, infers brands from outbound
(support) accounts, reconstructs conversation threads via Union-Find, and
computes per-brand quality statistics to identify the best candidates for
the SupportProof project.

Usage:
    python -m src.data.analyze_brands

Outputs:
    data/processed/brand_statistics.csv
    reports/brand_analysis.md
"""

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).resolve().parents[2]
CSV_PATH  = WORKSPACE / "data" / "raw" / "twcs.csv"
OUT_CSV   = WORKSPACE / "data" / "processed" / "brand_statistics.csv"
REPORT    = WORKSPACE / "reports" / "brand_analysis.md"

MENTION_RE = re.compile(r"@(\w+)")


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


# ── Helpers ────────────────────────────────────────────────────────────────
def _safe_int(val: str) -> int | None:
    """Parse a string as int, returning None on failure."""
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


# ── Main ───────────────────────────────────────────────────────────────────
def main() -> None:
    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} not found")
        sys.exit(1)
    print(f"Analyzing: {CSV_PATH}  ({CSV_PATH.stat().st_size / 1024**2:.1f} MB)\n")

    # Force UTF-8 stdout on Windows to avoid cp1252 encoding errors
    import io
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    # -- Pass 1: stream CSV, collect metadata & build Union-Find ------------
    print("Reading tweets ...")

    # Core data structures (int tweet_ids for memory efficiency)
    meta: dict[int, tuple[str, bool]] = {}     # tid -> (author, is_inbound)
    mention: dict[int, str] = {}               # inbound tid -> first @mention (lowered)
    linked: set[int] = set()                   # tids with in_response_to
    brands: set[str] = set()                   # outbound author_ids
    uf = UnionFind()

    with open(CSV_PATH, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for i, row in enumerate(reader, 1):
            tid = _safe_int(row["tweet_id"].strip())
            if tid is None:
                continue
            author = row["author_id"].strip()
            is_ib = row["inbound"].strip().lower() in ("true", "1", "yes")
            text = row.get("text", "")

            meta[tid] = (author, is_ib)

            if not is_ib:
                brands.add(author)

            # Extract first @mention from inbound tweets
            if is_ib:
                m = MENTION_RE.search(text)
                if m:
                    mention[tid] = m.group(1).lower()

            # Build conversation edges
            irt = row.get("in_response_to_tweet_id", "").strip()
            if irt:
                irt_int = _safe_int(irt)
                if irt_int is not None:
                    uf.union(tid, irt_int)
                    linked.add(tid)

            rt = row.get("response_tweet_id", "").strip()
            if rt:
                rt_int = _safe_int(rt)
                if rt_int is not None:
                    uf.union(tid, rt_int)

            if i % 500_000 == 0:
                print(f"  ... {i:,} rows")

    n_tweets = len(meta)
    print(f"  Tweets: {n_tweets:,}  |  Brand accounts: {len(brands):,}\n")

    # -- Group tweets into conversations ------------------------------------
    print("Building conversations ...")
    convos: dict[int, list[int]] = defaultdict(list)
    for tid in meta:
        convos[uf.find(tid)].append(tid)
    del uf  # free ~300 MB
    print(f"  Conversations: {len(convos):,}\n")
    # Free Union-Find memory

    # brand name (lowered) -> original name, for @mention matching
    brand_lc: dict[str, str] = {b.lower(): b for b in brands}

    # -- Per-brand accumulators ---------------------------------------------
    print("Computing per-brand statistics ...")
    S: dict[str, dict] = {b: dict(
        total=0, ib=0, ob=0,
        customers=set(), support=set(),
        links=0,
        complete=0, multi=0,
        lengths=[],
        directed=0, responded=0,
    ) for b in brands}

    done = 0
    for root, tids in convos.items():
        done += 1
        if done % 200_000 == 0:
            print(f"  ... {done:,} / {len(convos):,} conversations")

        # Classify tweets in this conversation
        ib_authors: set[str] = set()
        ob_per_brand: dict[str, int] = defaultdict(int)
        n_ib = 0
        n_link = 0
        brands_responding: set[str] = set()
        brands_mentioned: set[str] = set()

        for tid in tids:
            m = meta.get(tid)
            if m is None:
                continue  # phantom tweet (referenced but not in dataset)
            author, is_ib = m

            if is_ib:
                n_ib += 1
                ib_authors.add(author)
                mt = mention.get(tid)
                if mt and mt in brand_lc:
                    brands_mentioned.add(brand_lc[mt])
            else:
                if author in brands:
                    brands_responding.add(author)
                    ob_per_brand[author] += 1

            if tid in linked:
                n_link += 1

        all_conv_brands = brands_responding | brands_mentioned
        if not all_conv_brands:
            continue

        n_ob = sum(ob_per_brand.values())
        conv_len = n_ib + n_ob
        has_both = n_ib > 0 and n_ob > 0
        is_multi = conv_len >= 3 and has_both

        for brand in all_conv_brands:
            s = S[brand]
            brand_ob = ob_per_brand.get(brand, 0)
            s["ib"] += n_ib
            s["ob"] += brand_ob
            s["total"] += n_ib + brand_ob
            s["customers"].update(ib_authors)
            s["support"].add(brand)
            s["links"] += n_link
            s["directed"] += 1
            s["lengths"].append(conv_len)

            if has_both and brand in brands_responding:
                s["complete"] += 1
                s["responded"] += 1
            if is_multi and brand in brands_responding:
                s["multi"] += 1

    del convos, linked, mention  # free memory

    # -- Build results list -------------------------------------------------
    results: list[dict] = []
    for brand, s in S.items():
        directed = s["directed"] or 1
        lens = s["lengths"]
        avg_len = sum(lens) / len(lens) if lens else 0.0
        results.append(dict(
            brand=brand,
            total_tweets=s["total"],
            inbound_tweets=s["ib"],
            outbound_tweets=s["ob"],
            unique_customers=len(s["customers"]),
            unique_support_accounts=len(s["support"]),
            conversation_links=s["links"],
            conversation_count=directed,
            complete_conversations=s["complete"],
            multi_turn_conversations=s["multi"],
            avg_conversation_length=round(avg_len, 2),
            response_rate=round(s["responded"] / directed, 4),
        ))

    # -- Composite quality score (0-1) --------------------------------------
    # Weights chosen to prioritise *usable* support data over raw volume.
    max_complete = max((r["complete_conversations"] for r in results), default=1) or 1
    max_multi    = max((r["multi_turn_conversations"] for r in results), default=1) or 1
    max_cust     = max((r["unique_customers"] for r in results), default=1) or 1

    for r in results:
        r["quality_score"] = round(
            0.35 * (r["complete_conversations"] / max_complete)
          + 0.25 * (r["multi_turn_conversations"] / max_multi)
          + 0.20 * r["response_rate"]
          + 0.10 * (r["unique_customers"] / max_cust)
          + 0.10 * min(r["avg_conversation_length"] / 10.0, 1.0),
        4)

    results.sort(key=lambda r: r["quality_score"], reverse=True)
    top20 = results[:20]

    # -- Console summary ----------------------------------------------------
    print("\n" + "=" * 100)
    print(f"{'RANK':>4}  {'BRAND':<25} {'COMPLETE':>9} {'MULTI':>7} "
          f"{'RESP%':>6} {'CUSTOMERS':>10} {'AVG_LEN':>8} {'SCORE':>7}")
    print("=" * 100)
    for i, r in enumerate(top20, 1):
        print(f"{i:4d}  {r['brand']:<25} {r['complete_conversations']:>9,} "
              f"{r['multi_turn_conversations']:>7,} "
              f"{r['response_rate'] * 100:>5.1f}% "
              f"{r['unique_customers']:>10,} "
              f"{r['avg_conversation_length']:>8.2f} "
              f"{r['quality_score']:>7.4f}")
    print("=" * 100)

    # -- Export CSV ---------------------------------------------------------
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "brand", "total_tweets", "inbound_tweets", "outbound_tweets",
        "unique_customers", "unique_support_accounts", "conversation_links",
        "conversation_count", "complete_conversations", "multi_turn_conversations",
        "avg_conversation_length", "response_rate", "quality_score",
    ]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)
    print(f"\nCSV  -> {OUT_CSV}")

    # -- Generate report ----------------------------------------------------
    report = _build_report(top20, results, n_tweets, len(brands))
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(f"Report -> {REPORT}")


# -- Report generator ------------------------------------------------------
def _build_report(
    top20: list[dict],
    all_results: list[dict],
    total_tweets: int,
    total_brands: int,
) -> str:
    L: list[str] = []

    L.append("# Brand Analysis Report\n")
    L.append(f"**Dataset:** {total_tweets:,} tweets across {total_brands:,} brand accounts\n")

    # ── Ranking criteria ───────────────────────────────────────────────────
    L.append("## Ranking Criteria\n")
    L.append("Brands are ranked by a **composite quality score** (0–1) designed to")
    L.append("identify brands with the strongest *usable* customer-support data,")
    L.append("not simply the highest tweet volume.\n")
    L.append("| Weight | Metric | Rationale |")
    L.append("|--------|--------|-----------|")
    L.append("| 35% | Complete conversations | Conversations with both customer and brand messages — the core data unit |")
    L.append("| 25% | Multi-turn conversations | Conversations ≥ 3 messages with both sides — deeper interaction data |")
    L.append("| 20% | Response rate | Fraction of attributed conversations where the brand actually responded |")
    L.append("| 10% | Unique customers | Diversity of customer issues and intents |")
    L.append("| 10% | Avg conversation length | Depth of engagement (capped at 10 for normalisation) |\n")
    L.append("### Why not rank by tweet count?\n")
    L.append("Raw tweet volume conflates noisy, one-sided, or bot-generated traffic with")
    L.append("genuine support interactions. A brand with 100 k tweets but mostly")
    L.append("unanswered customer complaints is *less* useful than a brand with 30 k")
    L.append("tweets that are predominantly multi-turn resolved conversations.\n")

    # ── Top 20 table ───────────────────────────────────────────────────────
    L.append("## Top 20 Brands by Quality Score\n")
    L.append("| Rank | Brand | Total | Complete | Multi-turn | Resp % | Customers | Avg Len | Score |")
    L.append("|------|-------|-------|----------|------------|--------|-----------|---------|-------|")
    for i, r in enumerate(top20, 1):
        L.append(
            f"| {i} | `{r['brand']}` "
            f"| {r['total_tweets']:,} "
            f"| {r['complete_conversations']:,} "
            f"| {r['multi_turn_conversations']:,} "
            f"| {r['response_rate'] * 100:.1f}% "
            f"| {r['unique_customers']:,} "
            f"| {r['avg_conversation_length']:.2f} "
            f"| {r['quality_score']:.4f} |"
        )
    L.append("")

    # ── Data quality limitations ───────────────────────────────────────────
    L.append("## Data Quality Limitations\n")
    L.append("1. **Brand ≡ account handle.** Some companies operate multiple support handles")
    L.append("   (e.g. `@AmazonHelp` vs `@AmazonCS`). These appear as separate brands and")
    L.append("   are **not merged** automatically. Manual review may reveal opportunities")
    L.append("   to combine related accounts.")
    L.append("2. **Response-rate denominator.** Conversations are attributed to a brand via")
    L.append("   outbound tweets **or** `@mention` parsing of inbound tweets. Customers who")
    L.append("   tag a brand using non-standard spelling or omit the `@` prefix will be")
    L.append("   missed, potentially *overstating* the response rate.")
    L.append("3. **Conversation boundaries.** Threads are reconstructed using")
    L.append("   `in_response_to_tweet_id` and `response_tweet_id` via Union-Find. Some")
    L.append("   threads may be fragmented when linking IDs reference tweets absent from")
    L.append("   the dataset.")
    L.append("4. **Inbound attribution.** In the rare case of multi-brand conversations,")
    L.append("   inbound tweets are attributed to *all* involved brands, slightly")
    L.append("   inflating inbound counts.")
    L.append("5. **Temporal snapshot.** The dataset captures activity at a fixed point in")
    L.append("   time; brand behaviour may have changed.\n")

    # ── Suitability analysis ───────────────────────────────────────────────
    L.append("## Suitability Analysis of Top Candidates\n")
    L.append("For the SupportProof project we need a brand whose data supports:\n")
    L.append("- **Intent taxonomy:** diverse customer issues (→ many unique customers)")
    L.append("- **Historical-resolution retrieval:** resolved multi-turn exchanges")
    L.append("- **Golden evaluation set (150–250 examples):** enough quality conversations")
    L.append("- **Escalation decisions:** conversations showing both resolution and escalation patterns\n")

    for i, r in enumerate(top20, 1):
        multi = r["multi_turn_conversations"]
        cust = r["unique_customers"]
        rr = r["response_rate"]
        avg = r["avg_conversation_length"]

        suitable = True
        notes: list[str] = []

        if multi >= 5000:
            notes.append(f"✅ Excellent multi-turn volume ({multi:,})")
        elif multi >= 1000:
            notes.append(f"✅ Adequate multi-turn volume ({multi:,})")
        else:
            notes.append(f"⚠️ Low multi-turn volume ({multi:,})")
            suitable = False

        if cust >= 5000:
            notes.append(f"✅ Large customer base ({cust:,}) — diverse intents")
        elif cust >= 1000:
            notes.append(f"✅ Moderate customer base ({cust:,})")
        else:
            notes.append(f"⚠️ Small customer base ({cust:,})")

        if rr >= 0.8:
            notes.append(f"✅ High response rate ({rr * 100:.1f}%)")
        elif rr >= 0.5:
            notes.append(f"✅ Moderate response rate ({rr * 100:.1f}%)")
        else:
            notes.append(f"⚠️ Low response rate ({rr * 100:.1f}%)")

        if avg >= 4:
            notes.append(f"✅ Good conversation depth (avg {avg:.1f})")
        elif avg >= 2.5:
            notes.append(f"✅ Adequate conversation depth (avg {avg:.1f})")
        else:
            notes.append(f"⚠️ Shallow conversations (avg {avg:.1f})")

        verdict = "**Suitable**" if suitable else "**Marginal**"
        L.append(f"### {i}. `{r['brand']}` — {verdict}\n")
        for n in notes:
            L.append(f"- {n}")
        L.append("")

    # ── Top 3 recommendation ──────────────────────────────────────────────
    L.append("---\n")
    L.append("## Recommended Brands for SupportProof\n")
    L.append("Based on the analysis above, the top 3 brands are:\n")

    for i, r in enumerate(top20[:3], 1):
        L.append(f"### Recommendation {i}: `{r['brand']}`\n")
        L.append(f"| Metric | Value |")
        L.append(f"|--------|-------|")
        L.append(f"| Total tweets | {r['total_tweets']:,} |")
        L.append(f"| Inbound (customer) tweets | {r['inbound_tweets']:,} |")
        L.append(f"| Outbound (brand) tweets | {r['outbound_tweets']:,} |")
        L.append(f"| Unique customers | {r['unique_customers']:,} |")
        L.append(f"| Complete conversations | {r['complete_conversations']:,} |")
        L.append(f"| Multi-turn conversations | {r['multi_turn_conversations']:,} |")
        L.append(f"| Average conversation length | {r['avg_conversation_length']:.2f} |")
        L.append(f"| Response rate | {r['response_rate'] * 100:.1f}% |")
        L.append(f"| Quality score | {r['quality_score']:.4f} |\n")

        multi = r["multi_turn_conversations"]
        cust = r["unique_customers"]
        rr = r["response_rate"]
        avg = r["avg_conversation_length"]

        L.append("**Why this brand:**\n")
        reasons = []
        if multi >= 1000:
            reasons.append(f"- {multi:,} multi-turn conversations comfortably exceed the 150–250 "
                           f"golden-set requirement, leaving room for stratified sampling.")
        if cust >= 1000:
            reasons.append(f"- {cust:,} unique customers provide a broad distribution of intents "
                           f"for taxonomy discovery.")
        if rr >= 0.5:
            reasons.append(f"- {rr * 100:.1f}% response rate means the majority of customer queries "
                           f"have brand responses available for resolution retrieval.")
        if avg >= 3:
            reasons.append(f"- Average conversation length of {avg:.1f} messages indicates "
                           f"substantive back-and-forth, useful for escalation analysis.")
        for reason in reasons:
            L.append(reason)
        L.append("")

    return "\n".join(L)


if __name__ == "__main__":
    main()
