import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def generate_evaluate_chain(inputs: dict):
    prompt = f"""
Create {inputs['number']} multiple choice questions from the text below.

Text:
{inputs['text']}

Return JSON format like:
{inputs['response_json']}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    content = response.choices[0].message.content

    try:
        start = content.find("{")
        end = content.rfind("}") + 1
        cleaned = content[start:end]
        return {"quiz": json.loads(cleaned)}
    except:
        return {"quiz": content}