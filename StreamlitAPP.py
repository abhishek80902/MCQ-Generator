import os
import json
import traceback
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from langchain.callbacks import get_openai_callback

from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

# ----------------------------------------
# Basic setup
# ----------------------------------------
load_dotenv()
st.set_page_config(
    page_title="MCQ Generator",
    page_icon="📘",
    layout="wide"
)

# ----------------------------------------
# Load response schema
# ----------------------------------------
try:
    with open("Response.json", "r") as file:
        RESPONSE_JSON = json.load(file)
except Exception as e:
    st.error("❌ Failed to load Response.json")
    st.stop()

# ----------------------------------------
# UI Header
# ----------------------------------------
st.title("📘 Your personal MCQs Creator")
st.markdown("Generate high-quality MCQs from PDF or TXT files using LLMs 🚀")

# ----------------------------------------
# Sidebar Inputs
# ----------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    mcq_count = st.number_input(
        "Number of MCQs",
        min_value=3,
        max_value=50,
        value=5
    )

    subject = st.text_input(
        "Subject",
        max_chars=30,
        placeholder="e.g. Machine Learning"
    )

    tone = st.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard"]
    )

# ----------------------------------------
# Main Input Form
# ----------------------------------------
uploaded_file = st.file_uploader(
    "📂 Upload a PDF or TXT file",
    type=["pdf", "txt"]
)

generate_btn = st.button("🚀 Generate MCQs")

# ----------------------------------------
# MCQ Generation Logic
# ----------------------------------------
if generate_btn:
    if uploaded_file is None:
        st.warning("⚠️ Please upload a file first.")
        st.stop()

    if not subject:
        st.warning("⚠️ Please enter a subject.")
        st.stop()

    with st.spinner("⏳ Generating MCQs... Please wait"):
        try:
            # Read file
            text = read_file(uploaded_file)

            # OpenAI callback
            with get_openai_callback() as cb:
                response = generate_evaluate_chain(
                    {
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    }
                )

            st.success("✅ MCQs Generated Successfully!")

            # ----------------------------------------
            # Token Usage
            # ----------------------------------------
            with st.expander("📊 Token Usage"):
                st.write(f"**Total Tokens:** {cb.total_tokens}")
                st.write(f"**Prompt Tokens:** {cb.prompt_tokens}")
                st.write(f"**Completion Tokens:** {cb.completion_tokens}")
                st.write(f"**Estimated Cost:** ${cb.total_cost:.6f}")

            # ----------------------------------------
            # Display MCQs
            # ----------------------------------------
            if isinstance(response, dict):
                quiz = response.get("quiz")

                if quiz:
                    table_data = get_table_data(quiz)

                    if table_data:
                        df = pd.DataFrame(table_data)
                        df.index = df.index + 1

                        st.subheader("📋 Generated MCQs")
                        st.dataframe(df, use_container_width=True)

                        # Download button
                        csv = df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "⬇️ Download MCQs as CSV",
                            csv,
                            "mcqs.csv",
                            "text/csv"
                        )
                    else:
                        st.error("❌ Failed to extract MCQ table data.")
                else:
                    st.error("❌ No quiz data found in response.")
                    st.write(response)
            else:
                st.error("❌ Unexpected response format.")
                st.write(response)

        except Exception as e:
            st.error("❌ Something went wrong while generating MCQs.")
            st.code(traceback.format_exc())
