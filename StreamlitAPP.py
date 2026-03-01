import os
import json
import traceback
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain

# =========================================================
# Environment Setup
# =========================================================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found.")
    st.info("👉 Add GROQ_API_KEY in Streamlit → App Settings → Secrets")
    st.stop()

# =========================================================
# Page Config
# =========================================================
st.set_page_config(
    page_title="MCQ Generator",
    page_icon="📘",
    layout="wide"
)

# =========================================================
# Load Response Schema
# =========================================================
try:
    with open("Response.json", "r") as file:
        RESPONSE_JSON = json.load(file)
except Exception:
    st.error("❌ Failed to load Response.json")
    st.stop()

# =========================================================
# UI Header
# =========================================================
st.title("📘 AI MCQ Generator")
st.markdown(
    "Generate high-quality Multiple Choice Questions (MCQs) "
    "from **PDF or TXT files** using FREE AI 🚀"
)

# =========================================================
# Sidebar Configuration
# =========================================================
with st.sidebar:
    st.header("⚙️ Configuration")

    mcq_count = st.number_input("Number of MCQs", 3, 50, 5)

    subject = st.text_input(
        "Subject",
        max_chars=30,
        placeholder="e.g. Machine Learning"
    )

    tone = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])

# =========================================================
# File Upload
# =========================================================
st.subheader("📂 Upload Study Material")

uploaded_file = st.file_uploader(
    "Upload a PDF or TXT file",
    type=["pdf", "txt"]
)

generate_btn = st.button("🚀 Generate MCQs")

# =========================================================
# Validation
# =========================================================
def validate_inputs(file, subject):
    if file is None:
        st.warning("⚠️ Please upload a file.")
        return False
    if not subject.strip():
        st.warning("⚠️ Please enter a subject.")
        return False
    return True

# =========================================================
# MCQ Generation
# =========================================================
if generate_btn:
    if not validate_inputs(uploaded_file, subject):
        st.stop()

    with st.spinner("⏳ Generating MCQs..."):
        try:
            # Read file
            text = read_file(uploaded_file)

            # Generate MCQs
            response = generate_evaluate_chain({
                "text": text,
                "number": mcq_count,
                "subject": subject,
                "tone": tone,
                "response_json": json.dumps(RESPONSE_JSON),
            })

            st.success("✅ MCQs Generated Successfully!")

            # =================================================
            # Display Results
            # =================================================
            if isinstance(response, dict) and response.get("quiz"):
                table_data = get_table_data(response["quiz"])

                if table_data:
                    df = pd.DataFrame(table_data)

                    st.subheader("📋 Generated MCQs")

                    # ✅ Display MCQs as clean cards
                    for i, row in df.iterrows():
                        st.markdown(f"### Q{i+1}. {row['Question']}")
                        options_html = row["Options"].replace("\n", "<br>")
                        st.markdown(options_html, unsafe_allow_html=True)
                        st.markdown(f"**✅ Answer:** {row['Correct Answer']}")
                        st.divider()

                    # ✅ Download CSV
                    csv_data = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Download MCQs as CSV",
                        csv_data,
                        "mcqs.csv",
                        "text/csv"
                    )
                else:
                    st.error("❌ Failed to extract MCQ data.")
            else:
                st.error("❌ Invalid response format.")
                st.write(response)

        except Exception:
            st.error("❌ Error generating MCQs.")
            st.code(traceback.format_exc())