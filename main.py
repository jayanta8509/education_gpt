from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
from process import process_document
from openai_report import translate_to_slovenian
import uvicorn
import aiohttp
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
import os
from typing import Optional
import asyncio

app = FastAPI()

# Email Config
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_MAIL = "iksen.testmail@gmail.com"
SENDER_PASS = "vrovvtukfbaxbubd"
RECEIVER_MAIL = "research@almamater.at"

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates") 
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def render_template(template_name, report_content):
    template = env.get_template(template_name)
    return template.render(report_content=report_content)

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = SENDER_MAIL
    msg["To"] = RECEIVER_MAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls() 
        server.login(SENDER_MAIL, SENDER_PASS)
        server.sendmail(SENDER_MAIL, RECEIVER_MAIL, msg.as_string())
        server.quit()
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

async def process_from_url(url: str, **kwargs) -> Dict[str, Any]:
    """
    Process document from URL
    """
    try:
        # Download the file from URL using aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return {
                        "status": "error",
                        "status_code": response.status,
                        "message": f"Failed to download file from URL: HTTP {response.status}"
                    }
                
                # Read the content
                content = await response.read()
                
                # Create a file-like object from the content
                file_content = io.BytesIO(content)
                
                # Process the document
                result = await process_document(
                    pdf_input=file_content,
                    **kwargs
                )
                
                return result
    except Exception as e:
        return {
            "status": "error",
            "status_code": 500,
            "message": f"Error processing URL: {str(e)}"
        }

@app.post("/upload")
async def upload_file(
    file_url: Optional[str] = Form(None),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    mobile_phone: str = Form(...),
    country: str = Form(...),
    years_of_experience: int = Form(...),
    area_of_expertise: str = Form(...),
    study_programs: str = Form(...),
    is_currently_teaching: bool = Form(...),
    current_university: Optional[str] = Form(None)
):
    """
    Handle file upload and form data submission.
    Returns both English and Slovenian reports.
    Sends emails if reports contain data.
    """
    try:
        common_params = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "mobile_phone": mobile_phone,
            "country": country,
            "years_of_experience": years_of_experience,
            "area_of_expertise": area_of_expertise,
            "study_programs": study_programs,
            "is_currently_teaching": is_currently_teaching,
            "current_university": current_university
        }

        if not file_url:
            return {"status": "error", "status_code": 400, "message": "File URL must be provided"}

        # Process English report
        english_result = await process_from_url(file_url, **common_params)
        if english_result["status"] != "success":
            return english_result

        english_report = english_result["report"]

        # Process Slovenian report
        slovenian_result = await translate_to_slovenian(english_report)
        if slovenian_result["status"] != "success":
            return slovenian_result

        slovenian_report = slovenian_result["report"]

        email_tasks = []
        if english_report:
            english_body = render_template("english_report.html", english_report)
            email_tasks.append(asyncio.to_thread(send_email, "English Report Generated", english_body))

        if slovenian_report:
            slovenian_body = render_template("slovenian_report.html", slovenian_report)
            email_tasks.append(asyncio.to_thread(send_email, "Slovenian Report Generated", slovenian_body))

        if email_tasks:
            await asyncio.gather(*email_tasks)

        return {
            "status": "success",
            "status_code": 200,
            "english_report": english_report,
            "slovenian_report": slovenian_report
        }

    except Exception as e:
        return {
            "status": "error",
            "status_code": 500,
            "message": str(e)
        }

@app.post("/translate")
async def translate_report(
    report_data: dict
):
    """
    Translate the evaluation report to Slovenian.
    """
    try:
        result = await translate_to_slovenian(report_data)
        return result
    except Exception as e:
        return {
            "status": "error",
            "status_code": 500,
            "message": str(e)
        }

@app.get("/")
async def root():
    return {"message": "Welcome to the Evaluation Report Generator API"} 


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)