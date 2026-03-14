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

try:
    import ollama
except ImportError:
    ollama = None

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
    def __init__(self, api_key: Optional[str] = None, budget: Optional[ContextWindowBudget] = None, logger: Optional[Any] = None):
        self.google_api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.logger = logger
        
        self.provider = "heuristics"
        
        # 1. Check Ollama (Primary)
        if ollama:
            try:
                ollama.list()
                self.provider = "ollama"
            except Exception:
                pass
        
        # 2. Check Gemini (Fallback 1)
        if self.provider == "heuristics" and self.google_api_key:
            genai.configure(api_key=self.google_api_key)
            self.provider = "google"
            
        # 3. Check OpenAI (Fallback 2)
        if self.provider == "heuristics" and self.openai_api_key and openai:
            self.client = OpenAI(api_key=self.openai_api_key)
            self.provider = "openai"
        
        self.budget = budget or ContextWindowBudget()
        self.max_retries = 2
        
        # Deterministic generation config
        self.generation_config = {
            "temperature": 0.0,
            "top_p": 0.1,
        }

    def _call_with_retry(self, model_tier: str, prompt: str, is_json: bool = False) -> Optional[str]:
        """
        Handles transient API retries and provider fallback.
        model_tier: 'bulk' (cheap, fast) or 'synthesis' (expensive, deep)
        """
        providers_to_try = []
        if ollama: providers_to_try.append("ollama")
        if self.google_api_key: providers_to_try.append("google")
        if self.openai_api_key and openai: providers_to_try.append("openai")

        if not providers_to_try:
            return None

        for current_provider in providers_to_try:
            for attempt in range(self.max_retries + 1):
                try:
                    if current_provider == "ollama":
                        # Detect available model
                        try:
                            models_data = ollama.list()
                            # Ollama returns a list of Model objects with 'model' attribute (containing 'name')
                            models = getattr(models_data, 'models', [])
                            names = [getattr(m, 'model', '') for m in models]
                            
                            # Clean potential tags if strictly qwen2.5:3b is missing
                            local_model = "qwen2.5:3b" if "qwen2.5:3b" in names else (names[0] if names else None)
                            
                            if not local_model:
                                print(f"[DEBUG] LLMClient: Ollama - No local models found in {names}.")
                                break # Skip to next provider

                            response = ollama.generate(
                                model=local_model,
                                prompt=prompt,
                                format='json' if is_json else '',
                                options={
                                    "temperature": self.generation_config["temperature"],
                                    "top_p": self.generation_config["top_p"]
                                }
                            )
                            if response and response.get('response'):
                                self.budget.record_usage(len(response['response']) // 4, 0.0)
                                if self.logger:
                                    self.logger.log_event("LLMClient", "SEMANTIC_ENRICHMENT", "N/A", "llm_inference", 1.0, metadata={"provider": "ollama", "model": local_model, "tier": model_tier})
                                return response['response']
                            else:
                                print(f"[DEBUG] LLMClient: Ollama generation returned empty response. Response: {response}")
                                break
                        except Exception as oe:
                            print(f"[DEBUG] LLMClient: Ollama generation failed with error: {oe}")
                            break # Skip to next provider
                    
                    elif current_provider == "google":
                        # model_tier: bulk (flash) vs synthesis (pro)
                        actual_model = "gemini-1.5-flash" if model_tier == "bulk" else "gemini-1.5-pro"
                        model = genai.GenerativeModel(actual_model)
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
                            if self.logger:
                                self.logger.log_event("LLMClient", "SEMANTIC_ENRICHMENT", "N/A", "llm_inference", 1.0, metadata={"provider": "google", "model": actual_model, "tier": model_tier})
                            return response.text
                    
                    elif current_provider == "openai":
                        if not hasattr(self, 'client'):
                            self.client = OpenAI(api_key=self.openai_api_key)
                        
                        actual_model = "gpt-4o-mini" if model_tier == "bulk" else "gpt-4o"
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
                            cost = (usage.total_tokens / 1_000_000) * 0.15
                            self.budget.record_usage(usage.total_tokens, cost)
                            if self.logger:
                                self.logger.log_event("LLMClient", "SEMANTIC_ENRICHMENT", "N/A", "llm_inference", 1.0, metadata={"provider": "openai", "model": actual_model, "tier": model_tier})
                            return response.choices[0].message.content

                except Exception as e:
                    print(f"[DEBUG] LLMClient Provider {current_provider} Error: {e}")
                    error_str = str(e).lower()
                    is_transient = any(msg in error_str for msg in ["429", "rate limit", "503", "service unavailable", "deadline exceeded", "timeout"])
                    
                    if is_transient and attempt < self.max_retries:
                        time.sleep(2 ** attempt)
                        continue
                    else:
                        break # Break out of attempts for this provider, try next provider
        return None

    def embed_texts(self, texts: List[str], task_type: str = "clustering") -> List[List[float]]:
        """
        Generates embeddings for a list of strings using the best available provider.
        Prioritizes Ollama (if local) -> Gemini -> OpenAI.
        """
        if not texts:
            return []

        # Define providers to try for embeddings
        providers_to_try = []
        if ollama: providers_to_try.append("ollama")
        if self.google_api_key: providers_to_try.append("google")
        if self.openai_api_key and openai: providers_to_try.append("openai")

        for current_provider in providers_to_try:
            try:
                if current_provider == "ollama":
                    # Detect model
                    models_data = ollama.list()
                    models = getattr(models_data, 'models', [])
                    names = [getattr(m, 'model', '') for m in models]
                    local_model = "qwen2.5:3b" if "qwen2.5:3b" in names else (names[0] if names else None)
                    
                    if not local_model:
                        continue
                    
                    # Newer Ollama library uses .embed(model=..., input=...)
                    response = ollama.embed(model=local_model, input=texts)
                    if response and response.get('embeddings'):
                        total_chars = sum(len(t) for t in texts)
                        self.budget.record_usage(total_chars // 4, 0.0)
                        return response['embeddings']
                    continue

                elif current_provider == "google":
                    result = genai.embed_content(
                        model="models/embedding-001",
                        content=texts,
                        task_type=task_type
                    )
                    total_chars = sum(len(t) for t in texts)
                    self.budget.record_usage(total_chars // 4, 0.0)
                    return result['embedding']
                
                elif current_provider == "openai":
                    response = self.client.embeddings.create(
                        input=texts,
                        model="text-embedding-3-small"
                    )
                    self.budget.record_usage(response.usage.total_tokens, 0.0)
                    return [data.embedding for data in response.data]
                    
            except Exception as e:
                print(f"[DEBUG] LLMClient Embedding Error ({current_provider}): {e}")
                continue

        # Final fallback to zero vectors
        return [[0.0] * 768] * len(texts)

    def _call_heuristic_fallback(self, batched_summaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Non-LLM fallback that extracts purpose from docstrings and metadata.
        Ensures the pipeline continues even if all LLM services are down.
        """
        results = []
        for summary in batched_summaries:
            mpath = summary.get("module_path", "unknown")
            doc = summary.get("docstring")
            imports = summary.get("imports", [])
            funcs = summary.get("functions", [])
            
            if doc:
                purpose = f"Estimated purpose: {doc}"
                confidence = 0.4
            elif funcs or imports:
                purpose = f"Inferred purpose: This module manages {len(funcs)} functions and imports {len(imports)} dependencies. Key features likely include {', '.join(funcs[:2]) if funcs else 'system coordination'}."
                confidence = 0.2
            else:
                # Better heuristics for boilerplate or config files
                base = mpath.lower()
                if base.endswith("__init__.py"):
                    purpose = "Package initialization: Defines the module structure and exposes public interfaces for this directory."
                elif base.endswith(".toml") or base.endswith(".yml") or base.endswith(".yaml"):
                    purpose = "Configuration file: Defines project settings, dependencies, or environment-specific parameters."
                elif base.endswith(".md"):
                    purpose = "Documentation: Provides high-level project information, instructions, or architectural context."
                elif ".env" in base:
                    purpose = "Environment variables: Manages secrets and environment-specific configurations."
                elif base.endswith(".json") or base.endswith(".txt"):
                    purpose = "Data/Static resource: Stores structured data or plain text used by the system."
                else:
                    purpose = "Unknown purpose (Fallback enabled)"
                confidence = 0.1
                
            results.append({
                "module_path": mpath,
                "purpose_statement": purpose,
                "purpose_confidence": confidence
            })
        return results

    def get_purpose_statements(self, batched_summaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes a batch of module summaries to get business-level purpose statements.
        Cascades through: Cloud (OpenAI/Google) -> Local (Ollama) -> Heuristic.
        Uses 'bulk' model tier for cost efficiency.
        """
        if not batched_summaries:
            return []

        total_input_chars = sum(len(str(s)) for s in batched_summaries)
        estimated_input_tokens = total_input_chars // 4
        
        # Budget Check
        if not self.budget.can_afford_batch(estimated_input_tokens):
             return self._call_heuristic_fallback(batched_summaries)

        prompt = f"""
        You are analyzing software modules.
        Explain the BUSINESS PURPOSE of each module, not implementation details.
        Return 2-3 sentences per module.
        
        CRITICAL: Derive the purpose from the code implementation ONLY (functions, imports, logic). 
        Explicitly IGNORE any existing docstrings or comments that might describe the purpose, 
        as they may be outdated or misleading.
        
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

        response_text = self._call_with_retry("bulk", prompt, is_json=True)
        
        if response_text:
            try:
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                
                data = json.loads(response_text)
                raw_results = data.get("results", []) if isinstance(data, dict) else data
                
                if not isinstance(raw_results, list):
                    raw_results = []

                results = []
                for summary in batched_summaries:
                    mpath = summary.get("module_path")
                    found = next((r for r in raw_results if r.get("module_path") == mpath), None)
                    
                    if found and found.get("purpose_statement") and found.get("purpose_confidence") is not None:
                        results.append(found)
                    else:
                        # Fallback for individual module failure in block
                        results.extend(self._call_heuristic_fallback([summary]))
                
                self.budget.modules_processed += len(results)
                return results

            except (json.JSONDecodeError, KeyError):
                pass
        
        # Final cascading fallback to heuristic
        return self._call_heuristic_fallback(batched_summaries)
