import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain

# =========================================================
# Environment Setup
# =========================================================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# =========================================================
# LLM Configuration (Modern LangChain)
# =========================================================
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=OPENAI_API_KEY
)

# =========================================================
# Prompt 1 — Quiz Generation
# =========================================================
quiz_template = """
Text: {text}

You are an expert MCQ maker. Given the above text, create a quiz of {number}
multiple choice questions for {subject} students in {tone} tone.

Rules:
- Do not repeat questions
- Ensure questions match the text
- Generate exactly {number} MCQs

### RESPONSE_JSON
{response_json}
"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=quiz_template
)

quiz_chain = LLMChain(
    llm=llm,
    prompt=quiz_generation_prompt,
    output_key="quiz",
    verbose=False
)

# =========================================================
# Prompt 2 — Quiz Evaluation
# =========================================================
evaluation_template = """
You are an expert English grammarian and educator.

Given the following quiz for {subject} students:
{quiz}

Tasks:
1. Evaluate question complexity (max 50 words)
2. Improve tone if needed
3. Fix unclear questions

Return improved quiz if changes are required.
"""

quiz_evaluation_prompt = PromptTemplate(
    input_variables=["subject", "quiz"],
    template=evaluation_template
)

review_chain = LLMChain(
    llm=llm,
    prompt=quiz_evaluation_prompt,
    output_key="review",
    verbose=False
)

# =========================================================
# Sequential Chain
# =========================================================
generate_evaluate_chain = SequentialChain(
    chains=[quiz_chain, review_chain],
    input_variables=["text", "number", "subject", "tone", "response_json"],
    output_variables=["quiz", "review"],
    verbose=False
)
