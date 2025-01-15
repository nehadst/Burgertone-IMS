import os
from dotenv import load_dotenv
import openai

load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')
print(f"Key found: {'Yes' if openai_key else 'No'}")
print(f"Key starts with sk-: {'Yes' if openai_key.startswith('sk-') else 'No'}")
print(f"Key length: {len(openai_key)}")

client = openai.OpenAI()
try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("OpenAI API test successful!")
except Exception as e:
    print(f"Error: {str(e)}") 