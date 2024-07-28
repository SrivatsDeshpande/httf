import os
import pdfplumber  # For PDF parsing
from fastapi import FastAPI, Body, Request, Form
from fastapi.templating import Jinja2Templates
from google.generativeai import GenerativeModel
import google.generativeai as genai

# Replace with your actual API key
API_KEY = "YOUR_API_KEY"

app = FastAPI()
templates = Jinja2Templates(directory="templates")  # Assuming a templates directory

# Load the Gemini model (choose 'gemini-pro' or another suitable model)
model = GenerativeModel("gemini-pro")
genai.configure(api_key=API_KEY)  # Configure Gemini API using the provided key

def process_pdf(pdf_path):
    """
    Extracts text from the provided PDF path.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """

    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

@app.get("/")
async def root(request: Request):
    """
    Renders the initial HTML form for user input.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: Request, user_input: str = Form(...)):
    """
    Processes user input, retrieves relevant context from the PDF, and
    generates a response using the Gemini model.

    Args:
        request (Request): FastAPI request object.
        user_input (str): User's question or statement.

    Returns:
        JSON: Response object containing the generated response.
    """

    # Handle potential errors during PDF processing
    try:
        pdf_text = process_pdf("policy.pdf")  # Replace with actual PDF path
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return {"message": "An error occurred while processing the PDF."}

    # Combine user input and PDF context for better understanding
    context = f"{user_input} {pdf_text}"

    # Generate response using Gemini, considering the context
    response = model.generate(
        prompt=context,
        max_tokens=1024,  # Adjust as needed
        temperature=0.7,  # Adjust for creative vs. factual responses
    )

    return {"message": response.text[0]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
