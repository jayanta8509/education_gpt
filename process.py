from PyPDF2 import PdfReader
from fastapi import UploadFile
import io
from typing import Dict, Any, List
import os
import re
import PyPDF2
import os
from openai_report import generate_report_with_openai

async def extract_pdf_text(pdf_input, start_page=0, end_page=None):
    # Handle both file paths and uploaded files
    if isinstance(pdf_input, str):
        # If input is a file path
        if not os.path.exists(pdf_input):
            raise FileNotFoundError(f"PDF file not found: {pdf_input}")
        file = open(pdf_input, 'rb')
    elif isinstance(pdf_input, UploadFile):
        # If input is an uploaded file (SpooledTemporaryFile)
        # Read the file content into a BytesIO object
        file_content = await pdf_input.read()
        file = io.BytesIO(file_content)
    else:
        # If input is already a BytesIO object
        file = pdf_input
    
    try:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)
        
        # Validate page numbers
        total_pages = len(pdf_reader.pages)
        
        if start_page < 0 or start_page >= total_pages:
            raise ValueError(f"Invalid start page. Must be between 0 and {total_pages-1}")
        
        # Set end page to last page if not specified
        if end_page is None:
            end_page = total_pages - 1
        
        if end_page < start_page or end_page >= total_pages:
            raise ValueError(f"Invalid end page. Must be between {start_page} and {total_pages-1}")
        
        # Extract text from specified pages
        extracted_text = []
        for page_num in range(start_page, end_page + 1):
            page = pdf_reader.pages[page_num]
            extracted_text.append(page.extract_text())
        
        # Combine extracted text
        return '\n'.join(extracted_text)
    finally:
        # Close the file if it was opened from a path
        if isinstance(pdf_input, str):
            file.close()

async def process_document(
    pdf_input,
    first_name: str,
    last_name: str,
    email: str,
    mobile_phone: str,
    country: str,
    years_of_experience: int,
    area_of_expertise: str,
    study_programs: str,
    is_currently_teaching: bool,
    current_university: str,
    start_page: int = 0,
    end_page: int = None
) -> Dict[str, Any]:
    """
    Process the uploaded document and generate an evaluation report.
    
    Args:
        pdf_input: Either a file path (str) or an uploaded file
        first_name (str): Candidate's first name
        last_name (str): Candidate's last name
        email (str): Candidate's email address
        mobile_phone (str): Candidate's mobile phone number
        country (str): Candidate's country of residence
        years_of_experience (int): Years of teaching experience
        area_of_expertise (str): Candidate's area of expertise
        study_programs (str): Study programs they can teach
        is_currently_teaching (bool): Whether they are currently teaching
        current_university (str): Current university if teaching
        start_page (int): Starting page number for text extraction
        end_page (int): Ending page number for text extraction
        
    Returns:
        Dict[str, Any]: Dictionary containing the status and report
    """
    try:
        # Extract text from the PDF
        extracted_text = await extract_pdf_text(pdf_input, start_page, end_page)
        # print(extracted_text)
        
        # Generate report using OpenAI
        result = await generate_report_with_openai(
            extracted_text=extracted_text,
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile_phone=mobile_phone,
            country=country,
            years_of_experience=years_of_experience,
            area_of_expertise=area_of_expertise,
            study_programs=study_programs,
            is_currently_teaching=is_currently_teaching,
            current_university=current_university
        )
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "status_code": 500,
            "status_description": "Internal Server Error",
            "message": str(e)
        }