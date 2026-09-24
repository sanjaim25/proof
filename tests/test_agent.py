"""
Tests for SupportProof Agent Architecture.
"""

import os
import unittest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from src.agent.agent import SupportProofAgent, AgentRequest, AgentResponse
from src.agent.schemas import Turn
from src.agent.providers import GeminiProvider, OpenAIProvider, LLMProvider

class TestAgent(unittest.TestCase):
    
    @patch("dotenv.load_dotenv")
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_gemini_key_fails(self, _mock_dotenv):
        with self.assertRaises(SystemExit):
            GeminiProvider()
            
    def test_schema_validation(self):
        # Missing intent
        with self.assertRaises(ValidationError):
            AgentResponse.model_validate_json('{"reply": "hi", "escalate": false}')
            
        # Invalid intent string not checked by Pydantic directly unless we use Literal/Enum, 
        # but our custom _validate_grounding catches it.
        
    @patch('src.agent.providers.OpenAIProvider.generate')
    @patch('src.agent.retriever.Retriever.retrieve')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test", "LLM_PROVIDER": "openai"})
    def test_weak_retrieval_does_not_force_escalation(self, mock_retrieve, mock_generate):
        # Mock retrieval returning WEAK confidence (no evidence)
        mock_retrieve.return_value = {
            "cases": [],
            "confidence": "weak",
            "top_sim": 0.0,
            "mean_sim": 0.0
        }
        
        # Mock LLM deciding NOT to escalate
        mock_generate.return_value = AgentResponse(
            intent="other_or_unclear",
            intent_confidence=0.9,
            reply="I can help with that.",
            escalate=False,
            escalation_reason=None,
            evidence=[]
        )
        
        agent = SupportProofAgent()
        res = agent.process(AgentRequest(customer_message="help"))
        
        # Should remain False since deterministic override is removed
        self.assertFalse(res["escalate"])
        self.assertIsNone(res["escalation_reason"])
        self.assertIsNone(res.get("api_error"))
        
    @patch('src.agent.providers.OpenAIProvider.generate')
    @patch('src.agent.retriever.Retriever.retrieve')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test", "LLM_PROVIDER": "openai"})
    def test_grounding_validation(self, mock_retrieve, mock_generate):
        # Mock retrieval with no $50 in evidence
        mock_retrieve.return_value = {
            "cases": [{"case_id": "1", "brand_response": "We will refund you.", "similarity": 0.9, "customer_message": ""}],
            "confidence": "strong",
            "top_sim": 0.9,
            "mean_sim": 0.9
        }
        
        # Mock LLM returning unsupported $50
        mock_generate.return_value = AgentResponse(
            intent="refund_request",
            intent_confidence=0.9,
            reply="I will refund you $50.00 immediately.",
            escalate=False,
            escalation_reason=None,
            evidence=[]
        )
        
        agent = SupportProofAgent()
        res = agent.process(AgentRequest(customer_message="refund plz"))
        
        # Should be caught by smart validation
        self.assertTrue(res["escalate"])
        self.assertIn("Unsupported monetary amount generated: $50.00", res["validation_failures"])
        self.assertIn("wait while I connect you to a human", res["reply"])
        self.assertIsNone(res.get("api_error"))

    def test_evaluation_config_k(self):
        """Verify that the evaluation script is configured for K=2 to save tokens."""
        with open("src/evaluation/run_agent.py", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("SupportProofAgent(k=2", content)
        self.assertNotIn("SupportProofAgent(k=5", content)
        self.assertNotIn("SupportProofAgent(k=3", content)


class TestProviders(unittest.TestCase):
    """Tests for provider implementations — no real API calls."""

    # ── 1. OpenAI provider returns a valid AgentResponse ──────────────────

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "gpt-5.6-luna"})
    @patch("openai.OpenAI")
    def test_openai_provider_returns_valid_response(self, MockOpenAI):
        """OpenAIProvider.generate() returns a schema-validated Pydantic object."""
        expected = AgentResponse(
            intent="refund_request",
            intent_confidence=0.85,
            reply="I can help with your refund.",
            escalate=False,
            escalation_reason=None,
            evidence=[],
        )

        # Mock the SDK's parse() return structure
        mock_message = MagicMock()
        mock_message.refusal = None
        mock_message.parsed = expected

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.beta.chat.completions.parse.return_value = mock_response
        MockOpenAI.return_value = mock_client

        provider = OpenAIProvider()
        result = provider.generate("test prompt", AgentResponse)

        self.assertIsInstance(result, AgentResponse)
        self.assertEqual(result.intent, "refund_request")
        self.assertEqual(result.reply, "I can help with your refund.")

    # ── 2. Invalid structured output / refusal is rejected safely ─────────

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("openai.OpenAI")
    def test_openai_provider_raises_on_refusal(self, MockOpenAI):
        """Model refusal raises ValueError so the agent fallback can handle it."""
        mock_message = MagicMock()
        mock_message.refusal = "I cannot process this request."
        mock_message.parsed = None

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.beta.chat.completions.parse.return_value = mock_response
        MockOpenAI.return_value = mock_client

        provider = OpenAIProvider()
        with self.assertRaises(ValueError) as ctx:
            provider.generate("test prompt", AgentResponse)
        self.assertIn("Model refused", str(ctx.exception))

    # ── 3. API/provider errors trigger the agent's deterministic fallback ─

    @patch('src.agent.providers.OpenAIProvider.generate')
    @patch('src.agent.retriever.Retriever.retrieve')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test", "LLM_PROVIDER": "openai"})
    def test_provider_error_triggers_fallback(self, mock_retrieve, mock_generate):
        """When the provider raises, the agent returns the safe fallback."""
        mock_retrieve.return_value = {
            "cases": [],
            "confidence": "weak",
            "top_sim": 0.0,
            "mean_sim": 0.0,
        }
        mock_generate.side_effect = Exception("API connection failed")

        agent = SupportProofAgent()
        res = agent.process(AgentRequest(customer_message="help me"))

        self.assertTrue(res["escalate"])
        self.assertEqual(res["intent"], "other_or_unclear")
        self.assertIn("technical difficulties", res["reply"])
        self.assertIn("API connection failed", res["escalation_reason"])
        self.assertEqual(res.get("api_error"), "API connection failed")

    # ── 4. Gemini provider remains importable ─────────────────────────────

    def test_gemini_provider_importable(self):
        """GeminiProvider class is still importable and is a proper LLMProvider."""
        self.assertTrue(issubclass(GeminiProvider, LLMProvider))
        self.assertTrue(hasattr(GeminiProvider, 'generate'))

    def test_openai_provider_is_llm_provider(self):
        """OpenAIProvider class is a proper LLMProvider subclass."""
        self.assertTrue(issubclass(OpenAIProvider, LLMProvider))
        self.assertTrue(hasattr(OpenAIProvider, 'generate'))

    # ── 5. Provider selection works through LLM_PROVIDER ──────────────────

    @patch('src.agent.providers.OpenAIProvider.generate')
    @patch('src.agent.retriever.Retriever.retrieve')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test", "LLM_PROVIDER": "openai"})
    def test_provider_selection_openai(self, mock_retrieve, mock_generate):
        """LLM_PROVIDER=openai selects OpenAIProvider."""
        agent = SupportProofAgent()
        self.assertIsInstance(agent.provider, OpenAIProvider)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test", "LLM_PROVIDER": "gemini"})
    def test_provider_selection_gemini(self):
        """LLM_PROVIDER=gemini selects GeminiProvider."""
        agent = SupportProofAgent()
        self.assertIsInstance(agent.provider, GeminiProvider)

    @patch.dict(os.environ, {"LLM_PROVIDER": "unsupported_llm"}, clear=False)
    def test_provider_selection_invalid(self):
        """Unknown LLM_PROVIDER raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            SupportProofAgent()
        self.assertIn("unsupported_llm", str(ctx.exception))

    @patch("dotenv.load_dotenv")
    @patch.dict(os.environ, {}, clear=True)
    def test_openai_missing_key_fails(self, _mock_dotenv):
        """OpenAIProvider exits if OPENAI_API_KEY is missing."""
        with self.assertRaises(SystemExit):
            OpenAIProvider()

    # ── 6. Groq Provider tests ────────────────────────────────────────────

    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key", "GROQ_MODEL": "openai/gpt-oss-20b"})
    @patch("groq.Groq")
    def test_groq_provider_returns_valid_response(self, MockGroq):
        """GroqProvider.generate() returns a schema-validated Pydantic object."""
        mock_json_content = '''{
            "intent": "refund_request",
            "intent_confidence": 0.85,
            "reply": "I can help with your refund.",
            "escalate": false,
            "escalation_reason": null,
            "evidence": []
        }'''

        mock_message = MagicMock()
        mock_message.content = mock_json_content

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        MockGroq.return_value = mock_client

        from src.agent.providers import GroqProvider
        provider = GroqProvider()
        result = provider.generate("test prompt", AgentResponse)

        self.assertIsInstance(result, AgentResponse)
        self.assertEqual(result.intent, "refund_request")
        self.assertEqual(result.reply, "I can help with your refund.")

        # Verify that response_format uses strict json_schema (not json_object)
        call_kwargs = mock_client.chat.completions.create.call_args
        rf = call_kwargs.kwargs.get("response_format") or call_kwargs[1].get("response_format")
        self.assertEqual(rf["type"], "json_schema")
        self.assertTrue(rf["json_schema"]["strict"])

    def test_groq_strict_schema_builder(self):
        """_build_strict_schema produces Groq strict-compatible JSON schema."""
        from src.agent.providers import _build_strict_schema
        schema = _build_strict_schema(AgentResponse)

        # Root object must have additionalProperties: false
        self.assertFalse(schema["additionalProperties"])
        # All 6 fields must be required
        self.assertIn("evidence", schema["required"])
        self.assertEqual(len(schema["required"]), 6)
        # EvidenceItem must be inlined (no $ref)
        evidence_items = schema["properties"]["evidence"]["items"]
        self.assertNotIn("$ref", evidence_items)
        self.assertFalse(evidence_items["additionalProperties"])
        # Metadata must be stripped
        self.assertNotIn("title", schema)
        self.assertNotIn("description", schema["properties"]["intent"])

    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key"})
    @patch("groq.Groq")
    def test_groq_provider_raises_on_invalid_json(self, MockGroq):
        """GroqProvider raises an error if the JSON is invalid or schema validation fails."""
        mock_message = MagicMock()
        mock_message.content = '{"invalid_json": true'  # Missing closing brace

        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        MockGroq.return_value = mock_client

        from src.agent.providers import GroqProvider
        provider = GroqProvider()
        with self.assertRaises(Exception):
            provider.generate("test prompt", AgentResponse)

    @patch('src.agent.providers.GroqProvider.generate')
    @patch('src.agent.retriever.Retriever.retrieve')
    @patch.dict(os.environ, {"GROQ_API_KEY": "test", "LLM_PROVIDER": "groq"})
    def test_provider_selection_groq(self, mock_retrieve, mock_generate):
        """LLM_PROVIDER=groq selects GroqProvider."""
        from src.agent.providers import GroqProvider
        agent = SupportProofAgent()
        self.assertIsInstance(agent.provider, GroqProvider)

    @patch("dotenv.load_dotenv")
    @patch.dict(os.environ, {}, clear=True)
    def test_groq_missing_key_fails(self, _mock_dotenv):
        """GroqProvider exits if GROQ_API_KEY is missing."""
        from src.agent.providers import GroqProvider
        with self.assertRaises(SystemExit):
            GroqProvider()

class TestAgentV1Prompts(unittest.TestCase):
    """Verify that the Agent v1 prompt includes all targeted policy fixes."""
    
    def setUp(self):
        from src.agent.prompts import SYSTEM_PROMPT
        self.prompt = SYSTEM_PROMPT.lower()

    def test_other_or_unclear_conservative_instructions(self):
        self.assertIn("lacks enough information to reliably distinguish", self.prompt)
        self.assertIn("use other_or_unclear rather than guessing", self.prompt)
        self.assertIn("do not force a specific intent", self.prompt)

    def test_multi_intent_precedence_instructions(self):
        self.assertIn("prefer issue_with_received_item over return_request", self.prompt)
        self.assertIn("prefer return_request", self.prompt)
        self.assertIn("prefer refund_request", self.prompt)
        self.assertIn("prefer delivery_delay", self.prompt)
        self.assertIn("prefer order_tracking", self.prompt)
        self.assertIn("prefer missing_delivery", self.prompt)

    def test_explicit_escalation_request(self):
        self.assertIn("explicitly asks for a human/agent/escalation", self.prompt)

    def test_account_specific_action_requiring_escalation(self):
        self.assertIn("needs an account-specific action", self.prompt)

    def test_missing_delivery_escalation(self):
        self.assertIn("missing delivery / marked-delivered-but-not-received", self.prompt)

    def test_received_item_problem_escalation(self):
        self.assertIn("received item is damaged/defective", self.prompt)

    def test_angry_language_does_not_imply_escalation(self):
        self.assertIn("merely because the customer is angry, frustrated, or uses strong language", self.prompt)

    def test_urls_are_prohibited(self):
        self.assertIn("never reproduce urls", self.prompt)
        self.assertIn("never invent or provide urls", self.prompt)
        self.assertIn("never include t.co links", self.prompt)

    def test_no_invented_completed_actions(self):
        self.assertIn("do not invent account access", self.prompt)
        self.assertIn("or completed actions", self.prompt)


class TestRetrieverMath(unittest.TestCase):
    def test_cosine_similarity_bounded(self):
        from src.agent.retriever import Retriever
        
        # Create a mock retriever with a simple vocabulary
        r = Retriever(k=1, threshold=0.0)
        r.vocab = {"test", "word", "matching"}
        r.vectors = [{"test": 0.70710678118, "word": 0.70710678118}]
        r.corpus = [{"case_id": "1", "customer_message": "test word", "brand_response": "response"}]
        
        # Same exact words -> query normalized will be {test: ~0.707, word: ~0.707}
        res = r.retrieve("test word")
        
        self.assertGreater(len(res["cases"]), 0)
        sim = res["cases"][0]["similarity"]
        
        # Because we added L2 normalization to q_vec, it should be bounded at exactly 1.0 (with slight float imprecision)
        self.assertLessEqual(sim, 1.000001)
        self.assertGreaterEqual(sim, 0.999999)
        
    def test_unrelated_vectors(self):
        from src.agent.retriever import Retriever
        r = Retriever(k=1, threshold=0.55) # Use real threshold to drop 0 similarity
        r.vocab = {"test", "word", "other"}
        r.vectors = [{"other": 1.0}]
        r.corpus = [{"case_id": "1", "customer_message": "other", "brand_response": "response"}]
    
        res = r.retrieve("test word")
        self.assertEqual(len(res["cases"]), 0)
            
    def test_retrieval_confidence_thresholds(self):
        from src.agent.retriever import Retriever
        r = Retriever(k=1, threshold=0.0)
        r.vocab = {"validword", "anotherword"}
        r.vectors = [{"validword": 1.0}]
        r.corpus = [{"case_id": "1", "customer_message": "validword", "brand_response": "response"}]
    
        # Match perfectly -> 1.0 -> strong
        res_strong = r.retrieve("validword")
        self.assertEqual(res_strong["confidence"], "strong")
        
        # No match -> 0.0 -> weak
        res_weak = r.retrieve("anotherword")
        self.assertEqual(res_weak["confidence"], "weak")

if __name__ == "__main__":
    unittest.main()
