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
# Hugging Face Client (FREE MODEL)
# =========================================================
client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=HF_TOKEN,
)

# =========================================================
# MCQ Generator Function
# =========================================================
def generate_evaluate_chain(inputs: dict):
    """
    Generate MCQs using Hugging Face (FREE).
    """

    prompt = f"""
    You are an expert MCQ generator.

    Create {inputs['number']} multiple choice questions for
    {inputs['subject']} students in {inputs['tone']} difficulty.

    Text:
    {inputs['text']}

    Return response in JSON format like:
    {inputs['response_json']}
    """

    try:
        response = client.text_generation(
            prompt,
            max_new_tokens=800,
            temperature=0.7
        )

        # Try to parse JSON
        try:
            return json.loads(response)
        except:
            return {"quiz": response}

    except Exception as e:
        return {"quiz": f"Error generating MCQs: {str(e)}"}