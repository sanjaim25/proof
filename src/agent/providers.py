import os
import sys
from typing import Type
from pydantic import BaseModel

class LLMProvider:
    def generate(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        raise NotImplementedError("Subclasses must implement generate()")

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = None):
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("ERROR: GEMINI_API_KEY environment variable is missing.", file=sys.stderr)
            print("Please configure it in a .env file or export it directly.", file=sys.stderr)
            sys.exit(1)
            
        self.model_name = model_name or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Initialize Google GenAI client
        from google import genai
        from google.genai import types
        self.client = genai.Client(api_key=api_key)
        self.types = types

    def generate(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.0,
            ),
        )
        return schema.model_validate_json(response.text)

class OpenAIProvider(LLMProvider):
    def __init__(self, model_name: str = None):
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("ERROR: OPENAI_API_KEY environment variable is missing.", file=sys.stderr)
            print("Please configure it in a .env file or export it directly.", file=sys.stderr)
            sys.exit(1)

        self.model_name = model_name or os.environ.get("OPENAI_MODEL", "gpt-5.6-luna")

        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format=schema,
        )
        result = response.choices[0].message
        if getattr(result, 'refusal', None):
            raise ValueError(f"Model refused: {result.refusal}")
        return result.parsed

class GroqProvider(LLMProvider):
    def __init__(self, model_name: str = None):
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("ERROR: GROQ_API_KEY environment variable is missing.", file=sys.stderr)
            print("Please configure it in a .env file or export it directly.", file=sys.stderr)
            sys.exit(1)

        self.model_name = model_name or os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")

        from groq import Groq
        self.client = Groq(api_key=api_key)

    def generate(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        strict_schema = _build_strict_schema(schema)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "agent_response",
                    "strict": True,
                    "schema": strict_schema,
                },
            },
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Model returned empty content.")
        return schema.model_validate_json(content)


def _build_strict_schema(schema_cls: Type[BaseModel]) -> dict:
    """Convert a Pydantic model JSON schema to Groq strict-compatible format.

    Strict JSON Schema requires:
    - additionalProperties: false on every object
    - all properties listed in required
    - no $ref — definitions must be inlined
    - no unsupported keys (title, description, default)
    """
    raw = schema_cls.model_json_schema()
    defs = raw.pop("$defs", {})

    def _resolve(obj):
        if isinstance(obj, dict):
            # Resolve $ref by inlining the referenced definition
            if "$ref" in obj:
                ref_name = obj["$ref"].split("/")[-1]
                return _resolve(defs[ref_name])
            result = {}
            for k, v in obj.items():
                # Strip metadata keys unsupported by strict mode
                if k in ("title", "description", "default"):
                    continue
                result[k] = _resolve(v)
            # Enforce strict object constraints
            if result.get("type") == "object" and "properties" in result:
                result["additionalProperties"] = False
                result["required"] = list(result["properties"].keys())
            return result
        if isinstance(obj, list):
            return [_resolve(item) for item in obj]
        return obj

    return _resolve(raw)

