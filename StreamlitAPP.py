import os
import json
import traceback
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain

# ----------------------------------------
# Environment setup
# ----------------------------------------
load_dotenv()  # For local development

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("❌ OPENAI_API_KEY not found.")
    st.info("👉 Add it in Streamlit Cloud → App Settings → Secrets")
    st.stop()

# ----------------------------------------
# Streamlit page config
# ----------------------------------------
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
except Exception:
    st.error("❌ Failed to load Response.json")
    st.stop()

# ----------------------------------------
# UI
# ----------------------------------------
st.title("📘 Your Personal MCQ Creator")
st.markdown("Generate high-quality MCQs from PDF or TXT files using AI 🚀")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    mcq_count = st.number_input("Number of MCQs", 3, 50, 5)
    subject = st.text_input("Subject", max_chars=30, placeholder="e.g. Machine Learning")
    tone = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])

# Main input
uploaded_file = st.file_uploader("📂 Upload a PDF or TXT file", type=["pdf", "txt"])
generate_btn = st.button("🚀 Generate MCQs")

# ----------------------------------------
# Logic
# ----------------------------------------
if generate_btn:
    if uploaded_file is None:
        st.warning("⚠️ Please upload a file first.")
        st.stop()

    if not subject:
        st.warning("⚠️ Please enter a subject.")
        st.stop()

    with st.spinner("⏳ Generating MCQs..."):
        try:
            text = read_file(uploaded_file)

            response = generate_evaluate_chain(
                {
                    "text": text,
                    "number": mcq_count,
                    "subject": subject,
                    "tone": tone,
                    "response_json": json.dumps(RESPONSE_JSON),
                }
            )

            st.success("✅ MCQs Generated Successfully!")

            if isinstance(response, dict) and response.get("quiz"):
                table_data = get_table_data(response["quiz"])

                if table_data:
                    df = pd.DataFrame(table_data)
                    df.index += 1

                    st.subheader("📋 Generated MCQs")
                    st.dataframe(df, use_container_width=True)

                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇️ Download CSV", csv, "mcqs.csv", "text/csv")
                else:
                    st.error("❌ Failed to extract MCQ data.")
            else:
                st.error("❌ Invalid response format.")
                st.write(response)

        except Exception:
            st.error("❌ Something went wrong.")
            st.code(traceback.format_exc())
