import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def generate_evaluate_chain(inputs: dict):
    prompt = f"""
You are an expert MCQ generator.

Create EXACTLY {inputs['number']} multiple choice questions.

Return ONLY valid JSON in this format:

{{
  "1": {{
    "mcq": "Question text",
    "options": {{
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D"
    }},
    "correct": "A"
  }}
}}

Text:
{inputs['text']}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    # 🔹 Extract JSON safely
    try:
        start = content.find("{")
        end = content.rfind("}") + 1
        cleaned = content[start:end]
        return {"quiz": json.loads(cleaned)}
    except:
        return {"quiz": content}