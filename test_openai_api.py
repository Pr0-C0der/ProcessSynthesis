import os
from dotenv import load_dotenv
from openai import OpenAI

# Load the .env file
load_dotenv()

# Read API key from environment
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[
        {"role": "user", "content": "Hello, what can you do?"}
    ]
)

print(response.choices[0].message.content)
