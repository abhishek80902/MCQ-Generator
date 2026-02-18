import os
import json
import traceback
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain

# =========================================================
# 1️⃣ Environment Setup
# =========================================================
load_dotenv()  # Loads .env for local development

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("❌ OPENAI_API_KEY not found.")
    st.info("👉 Add it in Streamlit Cloud → App Settings → Secrets")
    st.stop()

# =========================================================
# 2️⃣ Streamlit Page Configuration
# =========================================================
st.set_page_config(
    page_title="MCQ Generator",
    page_icon="📘",
    layout="wide"
)

# =========================================================
# 3️⃣ Load Response Schema
# =========================================================
def load_response_schema():
    try:
        with open("Response.json", "r") as file:
            return json.load(file)
    except Exception:
        st.error("❌ Failed to load Response.json")
        st.stop()

RESPONSE_JSON = load_response_schema()

# =========================================================
# 4️⃣ UI Header
# =========================================================
st.title("📘 Your Personal MCQ Creator")
st.markdown(
    "Generate high-quality Multiple Choice Questions (MCQs) "
    "from **PDF or TXT** files using AI 🚀"
)

# =========================================================
# 5️⃣ Sidebar Configuration
# =========================================================
with st.sidebar:
    st.header("⚙️ Configuration")

    mcq_count = st.number_input(
        "Number of MCQs",
        min_value=3,
        max_value=50,
        value=5,
        step=1,
        help="Select how many MCQs to generate"
    )

    subject = st.text_input(
        "Subject",
        max_chars=30,
        placeholder="e.g. Machine Learning"
    )

    tone = st.selectbox(
        "Difficulty Level",
        options=["Easy", "Medium", "Hard"],
        help="Choose the difficulty level"
    )

# =========================================================
# 6️⃣ File Upload Section
# =========================================================
st.subheader("📂 Upload Study Material")

uploaded_file = st.file_uploader(
    "Upload a PDF or TXT file",
    type=["pdf", "txt"],
    help="Upload study material to generate MCQs"
)

generate_btn = st.button("🚀 Generate MCQs")

# =========================================================
# 7️⃣ Input Validation
# =========================================================
def validate_inputs(uploaded_file, subject):
    if uploaded_file is None:
        st.warning("⚠️ Please upload a file first.")
        return False

    if not subject.strip():
        st.warning("⚠️ Please enter a subject.")
        return False

    return True

# =========================================================
# 8️⃣ MCQ Generation Logic
# =========================================================
if generate_btn:
    if not validate_inputs(uploaded_file, subject):
        st.stop()

    with st.spinner("⏳ Generating MCQs... Please wait"):
        try:
            # Step 1: Read file
            text = read_file(uploaded_file)

            # Step 2: Generate MCQs using LangChain
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

            # =================================================
            # 9️⃣ Display Results
            # =================================================
            if isinstance(response, dict) and response.get("quiz"):
                table_data = get_table_data(response["quiz"])

                if table_data:
                    df = pd.DataFrame(table_data)
                    df.index += 1

                    st.subheader("📋 Generated MCQs")
                    st.dataframe(df, use_container_width=True)

                    # Download Button
                    csv_data = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="⬇️ Download MCQs as CSV",
                        data=csv_data,
                        file_name="mcqs.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("❌ Failed to extract MCQ table data.")
            else:
                st.error("❌ Invalid response format received.")
                st.write(response)

        except Exception:
            st.error("❌ Something went wrong while generating MCQs.")
            st.code(traceback.format_exc())
