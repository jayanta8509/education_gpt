from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
from process import process_document
from openai_report import translate_to_slovenian
import uvicorn
import aiohttp
import io

app = FastAPI()

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
    # file: Optional[UploadFile] = File(None),
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
    Accepts either file upload or file URL.
    Returns both English and Slovenian reports.
    """
    try:
        # Prepare common parameters
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

        # Process based on input type
        if file_url:
            # Process from URL
            english_result = await process_from_url(file_url, **common_params)
        # elif file:
        #     # Process from file upload
        #     english_result = await process_document(
        #         pdf_input=file,
        #         **common_params
        #     )
        else:
            return {
                "status": "error",
                "status_code": 400,
                "message": "Either file or file_url must be provided"
            }
        
        # Check if English report generation was successful
        if english_result["status"] != "success":
            return english_result
        
        # Get the English report data
        english_report = english_result["report"]
        
        # Generate Slovenian translation
        slovenian_result = await translate_to_slovenian(english_report)
        
        # Check if translation was successful
        if slovenian_result["status"] != "success":
            return slovenian_result
        
        # Get the Slovenian report data
        slovenian_report = slovenian_result["report"]
        
        # Return both reports
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