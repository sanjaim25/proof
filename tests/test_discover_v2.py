"""
Tests for src.intent.discover_v2.
"""

import unittest
from src.intent.discover_v2 import (
    is_support_message,
    embed_message,
    cosine_similarity,
    propose_intent_from_centroid
)

class TestIntentDiscoveryV2(unittest.TestCase):

    def test_noise_filtering(self):
        # Empty
        self.assertFalse(is_support_message(""))
        
        # Too short (< 15 chars or < 4 words)
        self.assertFalse(is_support_message("Hi"))
        self.assertFalse(is_support_message("Where is it"))
        
        # Praise/Greeting filtering
        self.assertFalse(is_support_message("Thank you so much Amazon! Best customer service ever!"))
        self.assertFalse(is_support_message("@AmazonHelp great job with my delivery today, thanks!"))
        
        # Valid support message with praise words but a problem
        self.assertTrue(is_support_message("Thanks for the help earlier, but my new package is missing."))
        
        # Normal support requests
        self.assertTrue(is_support_message("Where is my package? It was supposed to be here yesterday."))
        self.assertTrue(is_support_message("@AmazonHelp tracking says delivered but I don't have it."))

    def test_embed_message(self):
        # Missing delivery
        vec1 = embed_message("My package was stolen from my porch!")
        self.assertIn("missing", vec1)
        self.assertGreater(vec1["missing"], 0)
        
        # Delivery delay + refund
        vec2 = embed_message("My order is late, I want a refund now.")
        self.assertIn("delay", vec2)
        self.assertIn("refund", vec2)
        self.assertGreater(vec2["delay"], 0)
        self.assertGreater(vec2["refund"], 0)
        
        # Empty/no concepts
        vec3 = embed_message("Random words without semantic concepts.")
        self.assertEqual(len(vec3), 0)

    def test_cosine_similarity(self):
        v1 = {"missing": 1.0}
        v2 = {"missing": 0.5, "delay": 0.5}
        v3 = {"refund": 1.0}
        
        self.assertGreater(cosine_similarity(v1, v2), 0.0)
        self.assertEqual(cosine_similarity(v1, v3), 0.0)

    def test_propose_intent_from_centroid(self):
        # Empty or weak centroid
        self.assertEqual(propose_intent_from_centroid({}), "other_or_unclear")
        self.assertEqual(propose_intent_from_centroid({"missing": 0.1}), "other_or_unclear")
        
        # Strong centroids
        self.assertEqual(propose_intent_from_centroid({"missing": 0.8, "delay": 0.2}), "missing_delivery")
        self.assertEqual(propose_intent_from_centroid({"delay": 0.9}), "delivery_delay")
        self.assertEqual(propose_intent_from_centroid({"refund": 0.7, "return": 0.3}), "refunds_and_charges")

if __name__ == "__main__":
    unittest.main()
