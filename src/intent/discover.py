"""
Discover customer-support intents from AmazonHelp conversations.
Pure Python implementation of TF-IDF and K-Means clustering.
"""

import json
import math
import random
import re
import string
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# ── Paths ──────────────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).resolve().parents[2]
IN_JSONL  = WORKSPACE / "data" / "processed" / "amazonhelp_conversations.jsonl"
OUT_JSON  = WORKSPACE / "data" / "processed" / "intent_candidates.json"
REPORT    = WORKSPACE / "reports" / "intent_discovery.md"

# ── Constants ──────────────────────────────────────────────────────────────
SAMPLE_SIZE = 3000
K_CLUSTERS = 25
SEED = 42

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him",
    "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't",
    "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor",
    "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to",
    "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves",
    # Specific noise words
    "amazonhelp", "amazon", "help", "hi", "hello", "please", "just", "like", "will", "can", "now", "get"
}

# ── Extraction & Filtering ─────────────────────────────────────────────────

def is_valid_message(text: str) -> bool:
    """Filter out noise, too short, or URL-only messages."""
    text = text.strip()
    if not text:
        return False
    
    # Remove @mentions and URLs for length checking
    clean_text = re.sub(r'@\w+', '', text)
    clean_text = re.sub(r'http\S+', '', clean_text)
    clean_text = clean_text.strip()
    
    if len(clean_text) < 15:
        return False
    
    words = clean_text.split()
    if len(words) < 3:
        return False
        
    return True

def extract_customer_messages(conversations: List[dict]) -> List[str]:
    """Extract and deduplicate valid customer messages."""
    messages = []
    seen = set()
    for conv in conversations:
        for turn in conv.get("turns", []):
            if turn.get("speaker") == "customer":
                text = turn.get("text", "")
                if is_valid_message(text):
                    # Deduplicate based on a normalized version
                    norm = re.sub(r'\s+', ' ', text.lower().strip())
                    if norm not in seen:
                        seen.add(norm)
                        messages.append(text)
    return messages

# ── NLP & Clustering (Pure Python) ─────────────────────────────────────────

def tokenize(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    words = text.split()
    return [w for w in words if w not in STOP_WORDS and not w.isdigit()]

def build_tfidf(docs: List[List[str]]) -> Tuple[List[Dict[str, float]], set]:
    """Compute TF-IDF vectors for documents."""
    df = Counter()
    for doc in docs:
        for word in set(doc):
            df[word] += 1
            
    N = len(docs)
    # Scikit-learn style smoothing: log((1+N)/(1+count)) + 1
    idf = {w: math.log((1 + N) / (1 + count)) + 1.0 for w, count in df.items()}
    
    tfidf_docs = []
    vocab = set()
    for doc in docs:
        tf = Counter(doc)
        doc_len = len(doc)
        vec = {}
        norm_sq = 0.0
        if doc_len > 0:
            for w, count in tf.items():
                val = (count / doc_len) * idf[w]
                vec[w] = val
                norm_sq += val * val
                vocab.add(w)
            
            # Normalize vector
            if norm_sq > 0:
                norm = math.sqrt(norm_sq)
                vec = {w: v / norm for w, v in vec.items()}
        tfidf_docs.append(vec)
        
    return tfidf_docs, vocab

def cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    score = 0.0
    # Iterate over the smaller dict
    if len(vec1) > len(vec2):
        vec1, vec2 = vec2, vec1
    for k, v in vec1.items():
        if k in vec2:
            score += v * vec2[k]
    return score

def kmeans_clustering(tfidf_docs: List[Dict[str, float]], k: int, seed: int = SEED, max_iters: int = 30) -> List[int]:
    """K-Means clustering using cosine similarity."""
    rng = random.Random(seed)
    
    # Init centroids by picking k random documents
    valid_indices = [i for i, doc in enumerate(tfidf_docs) if len(doc) > 0]
    if len(valid_indices) < k:
        k = len(valid_indices)
    
    centroids = [tfidf_docs[i].copy() for i in rng.sample(valid_indices, k)]
    assignments = [-1] * len(tfidf_docs)
    
    for iteration in range(max_iters):
        changed = False
        clusters = [[] for _ in range(k)]
        
        # Assignment step
        for i, doc in enumerate(tfidf_docs):
            if not doc:
                continue
            best_c = -1
            best_sim = -1.0
            for c_idx, centroid in enumerate(centroids):
                sim = cosine_similarity(doc, centroid)
                if sim > best_sim:
                    best_sim = sim
                    best_c = c_idx
                    
            if assignments[i] != best_c:
                changed = True
                assignments[i] = best_c
            clusters[best_c].append(doc)
            
        if not changed:
            break
            
        # Update step
        for c_idx in range(k):
            new_centroid = defaultdict(float)
            if clusters[c_idx]:
                for doc in clusters[c_idx]:
                    for w, v in doc.items():
                        new_centroid[w] += v
                        
                # Normalize
                norm_sq = sum(v * v for v in new_centroid.values())
                if norm_sq > 0:
                    norm = math.sqrt(norm_sq)
                    centroids[c_idx] = {w: v / norm for w, v in new_centroid.items()}
            else:
                # Reinitialize empty cluster
                centroids[c_idx] = tfidf_docs[rng.choice(valid_indices)].copy()
                
    return assignments

# ── Taxonomy Generation ────────────────────────────────────────────────────

def get_cluster_keywords(cluster_docs: List[Dict[str, float]], top_n: int = 5) -> List[str]:
    word_scores = defaultdict(float)
    for doc in cluster_docs:
        for w, v in doc.items():
            word_scores[w] += v
    sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:top_n]]

def propose_intent_name(keywords: List[str]) -> str:
    # Heuristics based on common e-commerce support keywords
    kw_str = " ".join(keywords)
    if "prime" in kw_str and ("cancel" in kw_str or "membership" in kw_str or "charge" in kw_str):
        return "prime_cancellation_or_charge"
    if "delivery" in kw_str or "late" in kw_str or "arrive" in kw_str or "arrived" in kw_str:
        if "missing" in kw_str or "didn't" in kw_str or "never" in kw_str:
            return "missing_delivery"
        return "delivery_delay"
    if "return" in kw_str or "refund" in kw_str or "replacement" in kw_str:
        return "returns_and_refunds"
    if "order" in kw_str and "cancel" in kw_str:
        return "cancel_order"
    if "tracking" in kw_str or "status" in kw_str or "where" in kw_str:
        return "order_tracking"
    if "account" in kw_str or "login" in kw_str or "password" in kw_str:
        return "account_issue"
    if "app" in kw_str or "website" in kw_str or "error" in kw_str:
        return "technical_issue"
    if "damaged" in kw_str or "broken" in kw_str:
        return "damaged_item"
    if "wrong" in kw_str or "item" in kw_str or "missing" in kw_str:
        return "wrong_or_missing_item"
    if "gift" in kw_str or "card" in kw_str:
        return "gift_card_issue"
    
    return f"unknown_{keywords[0] if keywords else 'topic'}"

# ── Output Formatting ──────────────────────────────────────────────────────

def generate_proposed_taxonomy(clusters: List[dict]) -> List[dict]:
    # Group similar clusters based on proposed intent name
    intent_groups = defaultdict(list)
    for c in clusters:
        name = c["likely_intent_name"]
        if name.startswith("unknown_"):
            name = "other"
        intent_groups[name].append(c)
        
    taxonomy = []
    for name, group in intent_groups.items():
        total_examples = sum(c["num_examples"] for c in group)
        
        examples = []
        keywords = set()
        for c in group:
            examples.extend(c["representative_examples"])
            keywords.update(c["keywords"])
            
        # Shuffle examples deterministically and take top 5
        rng = random.Random(SEED)
        rng.shuffle(examples)
        
        confusable = []
        if name == "delivery_delay":
            confusable = ["missing_delivery", "order_tracking"]
        elif name == "missing_delivery":
            confusable = ["delivery_delay", "wrong_or_missing_item"]
        elif name == "returns_and_refunds":
            confusable = ["cancel_order"]
        elif name == "cancel_order":
            confusable = ["returns_and_refunds"]
            
        desc = "Customer inquiry related to: " + ", ".join(list(keywords)[:5])
        
        taxonomy.append({
            "intent_id": name,
            "intent_name": name.replace("_", " ").title(),
            "description": desc,
            "in_scope": "Messages containing: " + ", ".join(list(keywords)[:5]),
            "out_of_scope": "Other distinct issues",
            "representative_examples": examples[:5],
            "estimated_percentage": 0.0, # Will be filled later
            "count": total_examples,
            "common_keywords": list(keywords)[:10],
            "confusable_intents": confusable
        })
        
    # Calculate percentages
    total = sum(t["count"] for t in taxonomy)
    for t in taxonomy:
        t["estimated_percentage"] = round((t["count"] / total) * 100, 1)
        
    # Sort by percentage
    taxonomy.sort(key=lambda x: x["estimated_percentage"], reverse=True)
    return taxonomy

def write_markdown_report(clusters: List[dict], taxonomy: List[dict], outliers_count: int, total_sampled: int):
    outliers_pct = (outliers_count / total_sampled) * 100 if total_sampled else 0
    
    md = [
        "# Intent Discovery Report",
        "\n**PROPOSED TAXONOMY — REQUIRES HUMAN REVIEW**\n",
        "## Methodology",
        "- **Sampling Strategy**: Filtered for valid lengths, removed duplicates, and deterministically sampled 3,000 customer messages.",
        "- **Clustering**: Applied TF-IDF with stop-word removal followed by K-Means clustering (K=25) using cosine similarity (pure Python).",
        "- **Taxonomy Generation**: Grouped clusters heuristically based on keywords to produce final proposed intents.",
        f"\n**Total Sampled:** {total_sampled:,}",
        f"**Outliers (Noise/Unclustered):** {outliers_count:,} ({outliers_pct:.1f}%)\n",
        "## Proposed Final Taxonomy (8-15 Intents)\n"
    ]
    
    for t in taxonomy:
        md.append(f"### {t['intent_name']} (`{t['intent_id']}`)")
        md.append(f"- **Estimated Prevalence**: {t['estimated_percentage']}%")
        md.append(f"- **Description**: {t['description']}")
        md.append(f"- **In Scope**: {t['in_scope']}")
        md.append(f"- **Out of Scope**: {t['out_of_scope']}")
        md.append(f"- **Common Keywords**: {', '.join(t['common_keywords'])}")
        md.append(f"- **Confusable Intents**: {', '.join(t['confusable_intents']) if t['confusable_intents'] else 'None'}")
        md.append("\n**Examples:**")
        for ex in t['representative_examples']:
            clean_ex = ex.replace('\n', ' ').strip()
            md.append(f"- \"{clean_ex}\"")
        md.append("\n")
        
    md.append("## Raw Candidate Clusters\n")
    for c in clusters:
        md.append(f"### Cluster {c['cluster_id']} (n={c['num_examples']}, {c['percentage']:.1f}%)")
        md.append(f"- **Proposed Intent**: `{c['likely_intent_name']}`")
        md.append(f"- **Keywords**: {', '.join(c['keywords'])}")
        md.append(f"- **Confidence**: {c['confidence']}")
        md.append("\n**Examples:**")
        for ex in c['representative_examples']:
            clean_ex = ex.replace('\n', ' ').strip()
            md.append(f"- \"{clean_ex}\"")
        md.append("\n")
        
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(md), encoding="utf-8")
    
# ── Main ───────────────────────────────────────────────────────────────────

def main():
    import io
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        
    if not IN_JSONL.exists():
        print(f"ERROR: {IN_JSONL} not found"); sys.exit(1)
        
    print(f"Reading conversations from {IN_JSONL}...")
    conversations = []
    with open(IN_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                conversations.append(json.loads(line))
                
    print("Extracting and filtering customer messages...")
    messages = extract_customer_messages(conversations)
    print(f"Found {len(messages):,} valid unique customer messages.")
    
    rng = random.Random(SEED)
    if len(messages) > SAMPLE_SIZE:
        sampled_messages = rng.sample(messages, SAMPLE_SIZE)
    else:
        sampled_messages = messages
        
    print(f"Sampled {len(sampled_messages):,} messages for clustering.")
    
    print("Tokenizing and computing TF-IDF...")
    docs = [tokenize(msg) for msg in sampled_messages]
    tfidf_docs, vocab = build_tfidf(docs)
    
    print(f"Clustering into {K_CLUSTERS} clusters...")
    assignments = kmeans_clustering(tfidf_docs, k=K_CLUSTERS, seed=SEED)
    
    print("Analyzing clusters...")
    clusters = []
    outliers = 0
    cluster_docs = defaultdict(list)
    cluster_texts = defaultdict(list)
    
    for i, c_idx in enumerate(assignments):
        if c_idx == -1:
            outliers += 1
            continue
        cluster_docs[c_idx].append(tfidf_docs[i])
        cluster_texts[c_idx].append(sampled_messages[i])
        
    for c_idx, docs in cluster_docs.items():
        texts = cluster_texts[c_idx]
        keywords = get_cluster_keywords(docs, top_n=5)
        intent_name = propose_intent_name(keywords)
        
        rng_cluster = random.Random(SEED)
        rep_examples = rng_cluster.sample(texts, min(5, len(texts)))
        
        clusters.append({
            "cluster_id": c_idx,
            "num_examples": len(texts),
            "percentage": (len(texts) / len(sampled_messages)) * 100,
            "representative_examples": rep_examples,
            "keywords": keywords,
            "likely_intent_name": intent_name,
            "confidence": "High" if len(texts) > (len(sampled_messages)/K_CLUSTERS)*0.5 else "Low"
        })
        
    # Sort clusters by size
    clusters.sort(key=lambda x: x["num_examples"], reverse=True)
    
    # Save raw clusters
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(clusters, f, indent=2, ensure_ascii=False)
        
    # Generate final taxonomy and report
    taxonomy = generate_proposed_taxonomy(clusters)
    write_markdown_report(clusters, taxonomy, outliers, len(sampled_messages))
    
    # Console output
    print("\n=======================================================")
    print("INTENT DISCOVERY SUMMARY (PROPOSED TAXONOMY)")
    print("=======================================================\n")
    print(f"Outliers / Unclustered: {outliers} / {len(sampled_messages)}\n")
    
    for t in taxonomy:
        print(f"Intent: {t['intent_name']} ({t['intent_id']}) - {t['estimated_percentage']}%")
        for i, ex in enumerate(t['representative_examples'][:3], 1):
            ex_clean = ex.replace('\n', ' ').strip()
            if len(ex_clean) > 100: ex_clean = ex_clean[:97] + "..."
            print(f"  {i}. {ex_clean}")
        print()
        
    print(f"\nConfusable pairs analyzed in report.")
    print(f"Full report saved to {REPORT}")
    print(f"Candidate clusters saved to {OUT_JSON}")

if __name__ == "__main__":
    main()
