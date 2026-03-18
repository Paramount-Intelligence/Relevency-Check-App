import anthropic
import os
from dotenv import load_dotenv

# Load env from current directory
load_dotenv()

key = os.getenv("ANTHROPIC_API_KEY")
print(f"Key starts with: {key[:10]}...")

client = anthropic.Anthropic(api_key=key)

try:
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("Success!")
    print(message.content[0].text)
except Exception as e:
    print(f"Error: {e}")
