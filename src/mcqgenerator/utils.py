import PyPDF2
import json
import traceback


# =========================================================
# Read uploaded file (PDF or TXT)
# =========================================================
def read_file(uploaded_file):
    """
    Reads text from uploaded PDF or TXT file.
    Compatible with Streamlit uploader and PyPDF2 v3+.
    """

    # ✅ PDF handling
    if uploaded_file.name.lower().endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

            if not text.strip():
                raise Exception("No readable text found in PDF.")

            return text

        except Exception as e:
            traceback.print_exc()
            raise Exception("Error reading the PDF file")

    # ✅ TXT handling
    elif uploaded_file.name.lower().endswith(".txt"):
        try:
            return uploaded_file.read().decode("utf-8")
        except Exception:
            raise Exception("Error reading TXT file")

    # ❌ Unsupported file
    else:
        raise Exception("Unsupported file format. Only PDF and TXT are supported.")


# =========================================================
# Convert LLM response to table format
# =========================================================
def get_table_data(quiz_data):
    """
    Converts quiz JSON into table format for Streamlit display.
    Handles both dict and string responses.
    """

    try:
        # If LLM returned string → parse JSON
        if isinstance(quiz_data, str):
            quiz_data = json.loads(quiz_data)

        table = []

        # Expected format:
        # { "1": { "mcq": "...", "options": {...}, "correct": "A" } }

        for key, value in quiz_data.items():
            question = value.get("mcq", "")
            options_dict = value.get("options", {})
            correct = value.get("correct", "")

            options = " || ".join(
                f"{opt}: {text}" for opt, text in options_dict.items()
            )

            table.append({
                "Question": question,
                "Options": options,
                "Correct Answer": correct
            })

        return table

    except Exception as e:
        traceback.print_exc()
        return False