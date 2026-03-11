import os
import time
import json
import google.generativeai as genai
from typing import List, Dict, Any, Optional

try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None

class ContextWindowBudget:
    """Tracks LLM spending and enforces token/batch limits."""
    def __init__(self, max_cost: float = 1.0, max_tokens_per_module: int = 2000, max_batch_size: int = 10):
        self.max_cost = max_cost
        self.max_tokens_per_module = max_tokens_per_module
        self.max_batch_size = max_batch_size
        self.cumulative_cost = 0.0
        self.total_tokens_used = 0
        self.modules_eligible = 0
        self.modules_processed = 0

    def can_afford_batch(self, estimated_tokens: int) -> bool:
        # Rough cost estimate for Flash or GPT-4o-mini ($0.15 per 1M tokens)
        estimated_cost = (estimated_tokens / 1_000_000) * 0.15
        return (self.cumulative_cost + estimated_cost) <= self.max_cost

    def record_usage(self, tokens: int, cost: float):
        self.total_tokens_used += tokens
        self.cumulative_cost += cost

class LLMClient:
    """
    Wrapper for LLM interactions ensuring determinism, retry logic, and budget compliance.
    Supports Google Gemini and OpenAI.
    """
    def __init__(self, api_key: Optional[str] = None, budget: Optional[ContextWindowBudget] = None):
        self.google_api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        self.provider = None
        if self.openai_api_key and openai:
            self.client = OpenAI(api_key=self.openai_api_key)
            self.provider = "openai"
        elif self.google_api_key:
            genai.configure(api_key=self.google_api_key)
            self.provider = "google"
        
        self.budget = budget or ContextWindowBudget()
        self.max_retries = 2
        
        # Deterministic generation config
        self.generation_config = {
            "temperature": 0.0,
            "top_p": 0.1,
        }

    def _call_with_retry(self, model_name: str, prompt: str, is_json: bool = False) -> Optional[str]:
        """Handles transient API retries for both providers."""
        if not self.provider:
            print("[DEBUG] LLMClient: _call_with_retry failed - No provider.")
            return None

        for attempt in range(self.max_retries + 1):
            try:
                if self.provider == "google":
                    model = genai.GenerativeModel(model_name)
                    config = {**self.generation_config}
                    if is_json:
                        config["response_mime_type"] = "application/json"
                    
                    response = model.generate_content(
                        prompt,
                        generation_config=config,
                        request_options={"timeout": 30}
                    )
                    if response and response.text:
                        tokens = getattr(response, 'usage_metadata', None)
                        if tokens:
                            cost = (tokens.total_token_count / 1_000_000) * 0.10
                            self.budget.record_usage(tokens.total_token_count, cost)
                        return response.text
                
                elif self.provider == "openai":
                    # Map to specific OpenAI models if needed
                    actual_model = "gpt-4o-mini" if "flash" in model_name.lower() or "mini" in model_name.lower() else model_name
                    
                    kwargs = {
                        "model": actual_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": self.generation_config["temperature"],
                        "top_p": self.generation_config["top_p"],
                        "timeout": 30
                    }
                    if is_json:
                        kwargs["response_format"] = {"type": "json_object"}
                    
                    response = self.client.chat.completions.create(**kwargs)
                    if response.choices[0].message.content:
                        usage = response.usage
                        cost = (usage.total_tokens / 1_000_000) * 0.15 # GPT-4o-mini price approx
                        self.budget.record_usage(usage.total_tokens, cost)
                        return response.choices[0].message.content

            except Exception as e:
                error_str = str(e).lower()
                is_transient = any(msg in error_str for msg in ["429", "rate limit", "503", "service unavailable", "deadline exceeded", "timeout"])
                
                if is_transient and attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return None
        return None

    def embed_texts(self, texts: List[str], task_type: str = "clustering") -> List[List[float]]:
        """
        Generates embeddings for a list of strings using the active provider.
        """
        if not self.provider or not texts:
            return [[0.0] * 768] * len(texts)

        try:
            if self.provider == "google":
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=texts,
                    task_type=task_type
                )
                total_chars = sum(len(t) for t in texts)
                self.budget.record_usage(total_chars // 4, 0.0)
                return result['embedding']
            
            elif self.provider == "openai":
                response = self.client.embeddings.create(
                    input=texts,
                    model="text-embedding-3-small"
                )
                # Cost is negligible for small batches
                self.budget.record_usage(response.usage.total_tokens, 0.0)
                return [data.embedding for data in response.data]
                
        except Exception:
            # Fallback to zero vectors on failure
            return [[0.0] * 768] * len(texts)

    def get_purpose_statements(self, batched_summaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes a batch of module summaries to get business-level purpose statements.
        Returns validated results or default fallbacks.
        """
        if not batched_summaries:
            return []

        total_input_chars = sum(len(str(s)) for s in batched_summaries)
        estimated_input_tokens = total_input_chars // 4
        
        if not self.budget.can_afford_batch(estimated_input_tokens):
            return []

        prompt = f"""
        You are analyzing software modules.
        Your task is to explain the BUSINESS PURPOSE of each module, not implementation details.

        Focus on:
        • what business capability the module provides
        • what data it operates on
        • how it fits into the system

        Avoid:
        • variable names
        • programming language details
        • algorithm explanations

        Return 2-3 sentences per module.
        
        Modules to analyze:
        {json.dumps(batched_summaries, indent=2)}
        
        Output format must be a JSON list under the key "results":
        {{
          "results": [
            {{
              "module_path": "...",
              "purpose_statement": "...",
              "purpose_confidence": 0.0-1.0
            }}
          ]
        }}
        """

        model_name = "gemini-1.5-flash" if self.provider == "google" else "gpt-4o-mini"
        response_text = self._call_with_retry(model_name, prompt, is_json=True)
        
        results = []
        if response_text:
            try:
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                
                data = json.loads(response_text)
                raw_results = data.get("results", []) if isinstance(data, dict) else data
                
                if not isinstance(raw_results, list):
                    raw_results = []

                for i, summary in enumerate(batched_summaries):
                    mpath = summary.get("module_path")
                    found = next((r for r in raw_results if r.get("module_path") == mpath), None)
                    
                    if found and "purpose_statement" in found and "purpose_confidence" in found:
                        results.append(found)
                    else:
                        results.append({
                            "module_path": mpath,
                            "purpose_statement": "Unknown purpose",
                            "purpose_confidence": 0.0
                        })
            except (json.JSONDecodeError, KeyError):
                for summary in batched_summaries:
                    results.append({
                        "module_path": summary.get("module_path"),
                        "purpose_statement": "Unknown purpose",
                        "purpose_confidence": 0.0
                    })
        else:
            for summary in batched_summaries:
                results.append({
                    "module_path": summary.get("module_path"),
                    "purpose_statement": "Unknown purpose",
                    "purpose_confidence": 0.0
                })

        self.budget.modules_processed += len(results)
        return results
