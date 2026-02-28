import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(
    model="google/flan-t5-large",
    token=HF_TOKEN,
)

def generate_evaluate_chain(inputs: dict):
    prompt = f"""
You are an expert MCQ generator.

Create EXACTLY {inputs['number']} multiple choice questions.

Return STRICT JSON in this format:

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

    response = client.text_generation(
        prompt,
        max_new_tokens=800,
        temperature=0.3
    )

    # 🔹 Try to extract JSON safely
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        cleaned = response[start:end]
        return {"quiz": json.loads(cleaned)}
    except Exception:
        # fallback: return raw text
        return {"quiz": response}