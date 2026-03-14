import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

load_dotenv()

from utils.llm_client import LLMClient

client = LLMClient()
print(f"Provider: {client.provider}")

prompt = "Hello, are you there? Reply with 'YES'."
response = client._call_with_retry("gpt-4o-mini", prompt)
print(f"Response: {response}")
