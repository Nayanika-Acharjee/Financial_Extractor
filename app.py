from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
import pdfplumber
import pandas as pd
from extractor import extract_financial_data

app = FastAPI()

UPLOAD_PATH = "uploaded.pdf"
OUTPUT_CSV = "output.csv"

# ---------------- HOME PAGE ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>Financial Extractor</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f6f9;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .card {
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 6px 20px rgba(0,0,0,0.1);
                text-align: center;
                width: 400px;
            }
            h2 {
                margin-bottom: 20px;
                color: #333;
            }
            input[type="file"] {
                margin: 15px 0;
            }
            button {
                background: #4f46e5;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background: #4338ca;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>📊 Financial Statement Extractor</h2>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" required><br>
                <button type="submit">Upload & Extract</button>
            </form>
        </div>
    </body>
    </html>
    """

# ---------------- UPLOAD & EXTRACT ----------------
@app.post("/upload", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    # Save uploaded file
    with open(UPLOAD_PATH, "wb") as f:
        f.write(await file.read())

    # Extract text from PDF
    text = ""
    with pdfplumber.open(UPLOAD_PATH) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"

    # Extract financial data
    data = extract_financial_data(text)

    # Save CSV
    df = pd.DataFrame([data])
    df.to_csv(OUTPUT_CSV, index=False)

    # Convert table to HTML
    table_html = df.to_html(index=False)

    # Success page with table preview
    return f"""
    <html>
    <head>
        <title>Extraction Complete</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f9;
                padding: 40px;
                text-align: center;
            }}
            .container {{
                max-width: 800px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            }}
            h3 {{
                color: #16a34a;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
            }}
            th {{
                background: #4f46e5;
                color: white;
            }}
            a.button {{
                display: inline-block;
                margin-top: 20px;
                background: #4f46e5;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                text-decoration: none;
            }}
            a.button:hover {{
                background: #4338ca;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h3>✅ Extraction Complete</h3>
            <p>Your financial data has been extracted successfully.</p>

            <h4>📊 Extracted Data Preview</h4>
            {table_html}

            <a class="button" href="/download">⬇ Download CSV</a>
            <br><br>
            <a href="/">Upload another file</a>
        </div>
    </body>
    </html>
    """

# ---------------- DOWNLOAD CSV ----------------
@app.get("/download")
def download():
    return FileResponse(
        path=OUTPUT_CSV,
        filename="income_statement.csv",
        media_type="text/csv"
    )
