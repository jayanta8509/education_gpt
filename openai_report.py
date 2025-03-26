import os
from typing import Dict, Any
from datetime import datetime
import openai
from dotenv import load_dotenv
from pydantic import BaseModel
import json

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

class EvaluationReport(BaseModel):
    title: str = "EVALUATION REPORT"
    purpose: str
    education_and_accomplishments: str
    ability_to_lecture: str
    suitability: str
    conclusion: str
    date: str
    evaluator: str = "Evaluator"

class SlovenianReport(BaseModel):
    title: str = "POROČILO O OCENI"
    purpose: str
    education_and_accomplishments: str
    ability_to_lecture: str
    suitability: str
    conclusion: str
    date: str
    evaluator: str = "Ocenjevalec"

async def translate_to_slovenian(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate the evaluation report to Slovenian using OpenAI's API.
    
    Args:
        report_data (Dict[str, Any]): The original English report data
        
    Returns:
        Dict[str, Any]: Dictionary containing the status and translated report
    """
    try:
        # Prepare the prompt for translation
        prompt = f"""Translate the following evaluation report to Slovenian. Maintain the same structure and format.
        Keep the date in English format. Here's the report to translate:

        Title: {report_data['title']}
        Purpose: {report_data['purpose']}
        Education and Accomplishments: {report_data['education_and_accomplishments']}
        Ability to Lecture: {report_data['ability_to_lecture']}
        Suitability: {report_data['suitability']}
        Conclusion: {report_data['conclusion']}
        Date: {report_data['date']}
        Evaluator: {report_data['evaluator']}

        Please format the response as a JSON object with the following structure:
        {{
            "title": "POROČILO O OCENI",
            "purpose": "translated text here",
            "education_and_accomplishments": "translated text here",
            "ability_to_lecture": "translated text here",
            "suitability": "translated text here",
            "conclusion": "translated text here",
            "date": "keep original date",
            "evaluator": "Ocenjevalec"
        }}"""

        # Call OpenAI API for translation
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional translator specializing in academic and professional document translation. Translate the evaluation report to Slovenian while maintaining the formal tone and structure."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={ "type": "json_object" }
        )

        # Extract and parse the JSON response
        translated_data = json.loads(response.choices[0].message.content)
        
        # Create the Slovenian report using Pydantic
        slovenian_report = SlovenianReport(**translated_data)

        # Convert to dictionary for response
        report_dict = slovenian_report.model_dump()

        return {
            "status": "success",
            "status_code": 200,
            "report": report_dict
        }

    except Exception as e:
        return {
            "status": "error",
            "status_code": 500,
            "message": str(e)
        }

async def generate_report_with_openai(
    extracted_text: str,
    first_name: str,
    last_name: str,
    email: str,
    mobile_phone: str,
    country: str,
    years_of_experience: int,
    area_of_expertise: str,
    study_programs: str,
    is_currently_teaching: bool,
    current_university: str
) -> Dict[str, Any]:
    """
    Generate an evaluation report using OpenAI's API.
    
    Args:
        extracted_text (str): The text extracted from the uploaded documents
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
        
    Returns:
        Dict[str, Any]: Dictionary containing the status and report
    """
    # print(extracted_text)
    try:
        # Get today's date
        today = datetime.now().strftime("%B %d, %Y")
        
        # Prepare the candidate information
        candidate_info = f"""
Candidate Information:
Name: {first_name} {last_name}
Email: {email}
Phone: {mobile_phone}
Country: {country}
Years of Experience: {years_of_experience}
Area of Expertise: {area_of_expertise}
Study Programs: {study_programs}
Currently Teaching: {'Yes' if is_currently_teaching else 'No'}
Current University: {current_university if is_currently_teaching else 'N/A'}
"""
        
        # Prepare the prompt for OpenAI
        prompt = f"""Based on the following candidate information and document text, write in English a two-page Evaluation Report 
for this person to become a lecturer at Alma Mater Europaea University. The Evaluation Report should first 
overview the person's education and accomplishments, then assess the person's ability to lecture, and then 
conclude that the person meets the criteria, and is suitable. Add today's date ({today}). At the end, instead 
of the name of the evaluator just write: Evaluator


1. Purpose: Brief introduction and purpose of the evaluation
2. Education and Accomplishments: Overview of the candidate's educational background and professional achievements
3. Ability to Lecture: Assessment of teaching capabilities and experience
4. Suitability: Analysis of how well the candidate fits the position
5. Conclusion: Final assessment and recommendation

Please format the response as a JSON object with the following structure:
{{
    "purpose": "text here",
    "education_and_accomplishments": "text here",
    "ability_to_lecture": "text here",
    "suitability": "text here",
    "conclusion": "text here"
}}

Candidate Information:
{candidate_info}

Document Text to Analyze:
{extracted_text}"""

        # Call OpenAI API using the new format
        response = openai.chat.completions.create(
            model="gpt-4o",  # or "gpt-3.5-turbo" depending on your needs
            messages=[
                {"role": "system", "content": "You are a professional academic evaluator writing a formal evaluation report. Use the provided candidate information to create a comprehensive and personalized evaluation. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={ "type": "json_object" }
        )

        # Extract and parse the JSON response
        report_data = json.loads(response.choices[0].message.content)
        
        # Create the evaluation report using Pydantic
        evaluation_report = EvaluationReport(
            purpose=report_data["purpose"],
            education_and_accomplishments=report_data["education_and_accomplishments"],
            ability_to_lecture=report_data["ability_to_lecture"],
            suitability=report_data["suitability"],
            conclusion=report_data["conclusion"],
            date=today
        )

        # Convert to dictionary for response
        report_dict = evaluation_report.model_dump()

        return {
            "status": "success",
            "status_code": 200,
            "report": report_dict
        }

    except Exception as e:
        return {
            "status": "error",
            "status_code": 500,
            "message": str(e)
        } 