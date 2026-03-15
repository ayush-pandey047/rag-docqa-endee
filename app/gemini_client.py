
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_answer(question, context_passages):
    context = "\n\n".join(context_passages)

    prompt = f"""You are a helpful assistant. Answer the question based only on the context provided below.
If the answer is not found in the context, say "I could not find relevant information in the uploaded documents."

Context:
{context}

Question:
{question}

Answer:"""

    response = model.generate_content(prompt)
    return response.text.strip()