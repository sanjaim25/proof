"""
Tests for src.intent.discover.
"""

import unittest
from src.intent.discover import (
    is_valid_message,
    extract_customer_messages,
    tokenize,
    build_tfidf,
    cosine_similarity,
    kmeans_clustering,
    propose_intent_name
)

class TestIntentDiscovery(unittest.TestCase):

    def test_noise_filtering(self):
        # Empty
        self.assertFalse(is_valid_message(""))
        self.assertFalse(is_valid_message("   "))
        
        # Too short (< 15 chars or < 3 words)
        self.assertFalse(is_valid_message("Hi"))
        self.assertFalse(is_valid_message("Thanks Amazon!"))
        
        # URL only
        self.assertFalse(is_valid_message("http://amazon.com/help"))
        self.assertFalse(is_valid_message("@AmazonHelp http://link.com/foo"))
        
        # Valid messages
        self.assertTrue(is_valid_message("Where is my package? It was supposed to be here yesterday."))
        self.assertTrue(is_valid_message("@AmazonHelp tracking says delivered but I don't have it."))

    def test_customer_message_extraction(self):
        convs = [
            {
                "turns": [
                    {"speaker": "customer", "text": "Where is my package?"},
                    {"speaker": "brand", "text": "I can help with that."},
                    {"speaker": "customer", "text": "Thanks, it arrived!"}
                ]
            }
        ]
        
        msgs = extract_customer_messages(convs)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0], "Where is my package?")
        self.assertEqual(msgs[1], "Thanks, it arrived!")

    def test_tokenize(self):
        tokens = tokenize("Hello @AmazonHelp! My package (123) is late. http://link.com")
        self.assertNotIn("amazonhelp", tokens)
        self.assertNotIn("hello", tokens)
        self.assertNotIn("is", tokens)
        self.assertNotIn("123", tokens)
        self.assertNotIn("http://link.com", tokens)
        self.assertIn("package", tokens)
        self.assertIn("late", tokens)

    def test_tfidf_and_cosine(self):
        docs = [
            ["package", "late"],
            ["package", "missing"],
            ["account", "password"]
        ]
        tfidf_docs, vocab = build_tfidf(docs)
        self.assertEqual(len(tfidf_docs), 3)
        
        # 0 and 1 both share 'package', should have some similarity
        sim_0_1 = cosine_similarity(tfidf_docs[0], tfidf_docs[1])
        self.assertGreater(sim_0_1, 0.0)
        
        # 0 and 2 share nothing
        sim_0_2 = cosine_similarity(tfidf_docs[0], tfidf_docs[2])
        self.assertEqual(sim_0_2, 0.0)

    def test_deterministic_clustering(self):
        docs = [
            ["package", "late"],
            ["package", "missing"],
            ["package", "late", "missing"],
            ["account", "password", "login"],
            ["account", "locked", "login"]
        ]
        tfidf_docs, vocab = build_tfidf(docs)
        
        # k=2 should group the first 3 together and the last 2 together
        assignments1 = kmeans_clustering(tfidf_docs, k=2, seed=42)
        assignments2 = kmeans_clustering(tfidf_docs, k=2, seed=42)
        
        # Should be deterministic
        self.assertEqual(assignments1, assignments2)
        
        # Groupings should make sense
        self.assertEqual(assignments1[0], assignments1[1])
        self.assertEqual(assignments1[1], assignments1[2])
        self.assertEqual(assignments1[3], assignments1[4])
        self.assertNotEqual(assignments1[0], assignments1[3])

    def test_taxonomy_proposals(self):
        self.assertEqual(propose_intent_name(["package", "late", "delivery"]), "delivery_delay")
        self.assertEqual(propose_intent_name(["package", "missing", "delivery"]), "missing_delivery")
        self.assertEqual(propose_intent_name(["cancel", "prime", "membership"]), "prime_cancellation_or_charge")
        self.assertEqual(propose_intent_name(["return", "item", "refund"]), "returns_and_refunds")
        self.assertEqual(propose_intent_name(["account", "password", "login"]), "account_issue")
        self.assertEqual(propose_intent_name(["random", "stuff"]), "unknown_random")

if __name__ == "__main__":
    unittest.main()
