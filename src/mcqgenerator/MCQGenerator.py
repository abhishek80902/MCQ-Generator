import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# =========================================================
# Environment Setup
# =========================================================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# =========================================================
# LLM Setup
# =========================================================
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=OPENAI_API_KEY
)

# =========================================================
# Main Function (No deprecated chains)
# =========================================================
def generate_evaluate_chain(inputs: dict):
    """
    Generate MCQs using OpenAI.
    """

    prompt = f"""
    Text:
    {inputs['text']}

    You are an expert MCQ maker. Create {inputs['number']} {inputs['tone']} level
    multiple choice questions for {inputs['subject']} students.

    Return JSON in this format:
    {inputs['response_json']}
    """

    response = llm.invoke(prompt)

    try:
        return json.loads(response.content)
    except:
        return {"quiz": response.content}