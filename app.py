from multiprocessing import context

import flask
from flask_cors import CORS
import PyPDF2
import docx
import requests

app = flask.Flask(__name__)
CORS(app)

HF_API_TOKEN = "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"

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}


API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"

headers = {
    "Authorization":  "Bearer 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",
    "Content-Type": "application/json"
}




DOCUMENT_TEXT = ""

@app.route('/')
def index():
    return flask.render_template('index.html')

# ----------- FILE TEXT EXTRACTION -----------

def extract_text(file):
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        return " ".join([page.extract_text() or "" for page in reader.pages])

    elif filename.endswith(".docx"):
        doc = docx.Document(file)
        return " ".join([para.text for para in doc.paragraphs])

    elif filename.endswith(".txt"):
        return file.read().decode("utf-8")

    return ""

# ----------- SUMMARIZATION -----------

def summarize_text(text):
    API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": text[:800]},
            timeout=30
        )

        print("STATUS:", response.status_code)
        print("RAW:", response.text)

        # ❌ If empty response
        if not response.text.strip():
            return "❌ Empty response from API"

        # ❌ If not JSON
        try:
            data = response.json()
        except:
            return "❌ API did not return JSON"

        # 🔥 Handle API cases
        if isinstance(data, dict):
            return data.get("error", "❌ API error")

        if isinstance(data, list):
            return data[0].get("summary_text", "No summary found")

        return "❌ Unexpected API response"

    except requests.exceptions.Timeout:
        return "⏳ Request timed out"

    except Exception as e:
        return f"❌ Error: {str(e)}"
# ----------- QUESTION ANSWERING -----------

from openai import OpenAI

def answer_question(question, context):

    client = OpenAI(
        api_key="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",
        base_url="https://api.groq.com/openai/v1"
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions from documents."
                },
                {
                    "role": "user",
                    "content": f"""
                    Answer the question based on the context below in 4-5 lines.Answer ONLY from the provided context.
                    If the answer is not present in the context, say:
                    "I don't know based on the given document."
                    Do NOT make up answers.

                    Context:
                    {context[:1500]}

                    Question:
                    {question}
                    """
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"
# ----------- ROUTES -----------

@app.route('/upload', methods=['POST'])
def upload():
    global DOCUMENT_TEXT

    file = flask.request.files['file']
    DOCUMENT_TEXT = extract_text(file)

    if not DOCUMENT_TEXT:
        return flask.jsonify({"error": "Could not extract text"}), 400

    summary = summarize_text(DOCUMENT_TEXT)
    print("Extracted Text:", DOCUMENT_TEXT[:500])

    return flask.jsonify({"summary": summary})
   


@app.route('/ask', methods=['POST'])
def ask():
    data = flask.request.json
    question = data.get("question")

    answer = answer_question(question, DOCUMENT_TEXT)

    return flask.jsonify({"answer": answer})


if __name__ == '__main__':
    app.run(debug=True)