import PyPDF2
import json
import traceback

def read_file(file):
    # ✅ PDF handling (modern PyPDF2)
    if file.name.endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(file)
            text = ""

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted

            return text

        except Exception as e:
            traceback.print_exc()
            raise Exception("Error reading the PDF file")

    # ✅ TXT handling
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    else:
        raise Exception("Unsupported file format. Only PDF and TXT are supported.")