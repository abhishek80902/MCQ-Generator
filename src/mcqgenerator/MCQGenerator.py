import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# =========================================================
# Load Environment
# =========================================================
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# =========================================================
# Hugging Face Client (FREE CHAT MODEL)
# =========================================================
client = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta",  # free & supported
    token=HF_TOKEN,
)

# =========================================================
# MCQ Generator Function
# =========================================================
def generate_evaluate_chain(inputs: dict):
    prompt = f"""
You are an expert MCQ generator.

Create EXACTLY {inputs['number']} multiple choice questions from the text below.

Text:
{inputs['text']}

Return STRICT JSON in this format:
{inputs['response_json']}
"""

    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.3,
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