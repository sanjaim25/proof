"""
Tests for src.data.extract_brand — conversation reconstruction, speaker
identification, turn ordering, missing-ID handling, and no-invented-link
guarantees.

Run:
    python -m pytest tests/test_extract_brand.py -v
"""

import unittest
from datetime import datetime, timezone

from src.data.extract_brand import (
    UnionFind,
    build_conversation,
    identify_speaker,
    parse_twitter_date,
    sort_turns,
    validate_conversation,
)


# ── Helpers ────────────────────────────────────────────────────────────────
def _make_tweet(tid, author, inbound, created_at, text="hello",
                response_tweet_id="", in_response_to_tweet_id=""):
    """Shortcut to build a tweet dict matching extract_brand's expected format."""
    return {
        "author_id": author,
        "inbound": inbound,
        "created_at": created_at,
        "text": text,
        "response_tweet_id": response_tweet_id,
        "in_response_to_tweet_id": in_response_to_tweet_id,
    }


BRAND_SET = {"amazonhelp"}


# ── Conversation reconstruction ───────────────────────────────────────────
class TestConversationReconstruction(unittest.TestCase):
    """Tweets linked by in_response_to / response_tweet_id form one thread."""

    def test_two_tweet_conversation(self):
        """Two tweets linked via in_response_to form a single conversation."""
        uf = UnionFind()
        uf.union(1, 2)
        self.assertEqual(uf.find(1), uf.find(2))

    def test_multi_turn_chain(self):
        """Chain 1<-2<-3<-4 should all share one root."""
        uf = UnionFind()
        uf.union(2, 1)
        uf.union(3, 2)
        uf.union(4, 3)
        root = uf.find(1)
        for tid in (2, 3, 4):
            self.assertEqual(uf.find(tid), root)

    def test_branching_replies(self):
        """Two replies to the same parent belong to the same conversation."""
        uf = UnionFind()
        uf.union(2, 1)  # tweet 2 replies to 1
        uf.union(3, 1)  # tweet 3 also replies to 1
        self.assertEqual(uf.find(2), uf.find(3))

    def test_build_conversation_basic(self):
        """build_conversation produces correct metadata for a 3-turn thread."""
        data = {
            10: _make_tweet(10, "user1", True,
                            "Mon Oct 30 10:00:00 +0000 2017",
                            "@AmazonHelp my order is late"),
            11: _make_tweet(11, "AmazonHelp", False,
                            "Mon Oct 30 10:05:00 +0000 2017",
                            "@user1 Sorry to hear that! Please DM us.",
                            in_response_to_tweet_id="10"),
            12: _make_tweet(12, "user1", True,
                            "Mon Oct 30 10:10:00 +0000 2017",
                            "@AmazonHelp ok done",
                            in_response_to_tweet_id="11"),
        }
        conv = build_conversation(data, [10, 11, 12], "conv_10", BRAND_SET)

        self.assertEqual(conv["num_turns"], 3)
        self.assertTrue(conv["brand_responded"])
        self.assertTrue(conv["is_multi_turn"])
        self.assertEqual(conv["customer_author"], "user1")
        self.assertEqual(conv["brand_author"], "AmazonHelp")
        self.assertEqual(conv["turns"][0]["speaker"], "customer")
        self.assertEqual(conv["turns"][1]["speaker"], "brand")

    def test_build_conversation_single_turn(self):
        """A single tweet is correctly marked as single-turn."""
        data = {
            99: _make_tweet(99, "user5", True,
                            "Mon Oct 30 10:00:00 +0000 2017",
                            "@AmazonHelp help me"),
        }
        conv = build_conversation(data, [99], "conv_99", BRAND_SET)
        self.assertEqual(conv["num_turns"], 1)
        self.assertFalse(conv["is_multi_turn"])
        self.assertFalse(conv["brand_responded"])


# ── Speaker identification ────────────────────────────────────────────────
class TestSpeakerIdentification(unittest.TestCase):

    def test_brand_speaker(self):
        self.assertEqual(identify_speaker("AmazonHelp", BRAND_SET), "brand")

    def test_customer_speaker(self):
        self.assertEqual(identify_speaker("user123", BRAND_SET), "customer")

    def test_case_insensitive(self):
        self.assertEqual(identify_speaker("amazonhelp", BRAND_SET), "brand")
        self.assertEqual(identify_speaker("AMAZONHELP", BRAND_SET), "brand")

    def test_different_brand(self):
        """Non-AmazonHelp brand accounts are labelled 'customer'."""
        self.assertEqual(identify_speaker("AppleSupport", BRAND_SET), "customer")


# ── Turn ordering ─────────────────────────────────────────────────────────
class TestTurnOrdering(unittest.TestCase):

    def test_chronological_order(self):
        turns = [
            {"_dt": datetime(2017, 10, 31, 22, 0, tzinfo=timezone.utc), "tweet_id": 2},
            {"_dt": datetime(2017, 10, 31, 21, 0, tzinfo=timezone.utc), "tweet_id": 1},
        ]
        ordered = sort_turns(turns)
        self.assertEqual(ordered[0]["tweet_id"], 1)
        self.assertEqual(ordered[1]["tweet_id"], 2)

    def test_tie_broken_by_tweet_id(self):
        same_dt = datetime(2017, 10, 31, 22, 0, tzinfo=timezone.utc)
        turns = [
            {"_dt": same_dt, "tweet_id": 50},
            {"_dt": same_dt, "tweet_id": 30},
        ]
        ordered = sort_turns(turns)
        self.assertEqual(ordered[0]["tweet_id"], 30)

    def test_unparseable_date_sorted_last(self):
        good_dt = datetime(2017, 10, 31, 21, 0, tzinfo=timezone.utc)
        turns = [
            {"_dt": None, "tweet_id": 99},
            {"_dt": good_dt, "tweet_id": 1},
        ]
        ordered = sort_turns(turns)
        self.assertEqual(ordered[0]["tweet_id"], 1)
        self.assertEqual(ordered[1]["tweet_id"], 99)

    def test_parse_twitter_date_valid(self):
        dt = parse_twitter_date("Tue Oct 31 22:10:47 +0000 2017")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2017)
        self.assertEqual(dt.month, 10)
        self.assertEqual(dt.day, 31)

    def test_parse_twitter_date_invalid(self):
        self.assertIsNone(parse_twitter_date(""))
        self.assertIsNone(parse_twitter_date("not-a-date"))
        self.assertIsNone(parse_twitter_date(None))


# ── Missing parent / response IDs ────────────────────────────────────────
class TestMissingIDs(unittest.TestCase):

    def test_missing_parent_flagged(self):
        """Reference to a tweet NOT in the conversation should produce a flag."""
        turns = [
            {"in_response_to_tweet_id": "999", "_dt": None, "tweet_id": 1},
        ]
        conv_tids = {1}  # 999 is not in the conversation
        flags = validate_conversation(turns, conv_tids)
        self.assertTrue(any("outside conversation" in f for f in flags))

    def test_present_parent_not_flagged(self):
        """Reference to a tweet IN the conversation should NOT produce a flag."""
        turns = [
            {"in_response_to_tweet_id": "10", "_dt": None, "tweet_id": 11},
        ]
        conv_tids = {10, 11}
        flags = validate_conversation(turns, conv_tids)
        ref_flags = [f for f in flags if "outside" in f]
        self.assertEqual(len(ref_flags), 0)

    def test_empty_parent_not_flagged(self):
        """Empty in_response_to_tweet_id is normal, not a flag."""
        turns = [
            {"in_response_to_tweet_id": "", "_dt": None, "tweet_id": 1},
        ]
        flags = validate_conversation(turns, {1})
        ref_flags = [f for f in flags if "outside" in f]
        self.assertEqual(len(ref_flags), 0)

    def test_conversation_with_missing_data_still_builds(self):
        """build_conversation handles tweets referencing absent parents."""
        data = {
            20: _make_tweet(20, "user2", True,
                            "Mon Oct 30 10:00:00 +0000 2017",
                            "@AmazonHelp where is my order?",
                            in_response_to_tweet_id="999"),  # 999 not in data
            21: _make_tweet(21, "AmazonHelp", False,
                            "Mon Oct 30 10:05:00 +0000 2017",
                            "@user2 Let me check.",
                            in_response_to_tweet_id="20"),
        }
        conv = build_conversation(data, [20, 21], "conv_20", BRAND_SET)
        self.assertIsNotNone(conv)
        self.assertTrue(conv["is_flagged"])
        self.assertIn("outside conversation", conv["flag_reason"])


# ── No invented conversation links ───────────────────────────────────────
class TestNoInventedLinks(unittest.TestCase):

    def test_unlinked_tweets_stay_separate(self):
        """Two tweets with NO edges must remain in different components."""
        uf = UnionFind()
        uf.find(100)
        uf.find(200)
        self.assertNotEqual(uf.find(100), uf.find(200))

    def test_only_explicit_edges_connect(self):
        """Only the explicit union calls create connections."""
        uf = UnionFind()
        uf.find(1)
        uf.find(2)
        uf.find(3)
        uf.union(1, 2)
        self.assertEqual(uf.find(1), uf.find(2))
        self.assertNotEqual(uf.find(1), uf.find(3))

    def test_transitive_connection(self):
        """1-2 and 2-3 implies 1-3 (transitive, via real edges)."""
        uf = UnionFind()
        uf.union(1, 2)
        uf.union(2, 3)
        self.assertEqual(uf.find(1), uf.find(3))

    def test_no_spurious_merge(self):
        """Two independent 2-tweet conversations stay independent."""
        uf = UnionFind()
        uf.union(10, 11)  # conversation A
        uf.union(20, 21)  # conversation B
        self.assertEqual(uf.find(10), uf.find(11))
        self.assertEqual(uf.find(20), uf.find(21))
        self.assertNotEqual(uf.find(10), uf.find(20))


if __name__ == "__main__":
    unittest.main()
