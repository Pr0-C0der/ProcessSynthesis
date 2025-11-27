import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model="gpt-4.1-nano",
    messages=[
        {"role": "user", "content": "Hello, Nano!"}
    ]
)

print(response.choices[0].message.content)
