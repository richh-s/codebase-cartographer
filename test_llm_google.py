import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

load_dotenv()

from utils.llm_client import LLMClient

# Manually clear OpenAI key to force Google fallback
os.environ["OPENAI_API_KEY"] = ""

client = LLMClient()
print(f"Provider: {client.provider}")

prompt = "Hello, are you there? Reply with 'YES'."
response = client._call_with_retry("gemini-1.5-flash", prompt)
print(f"Response: {response}")
