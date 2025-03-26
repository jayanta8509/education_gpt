# Teacher Application API

This is a FastAPI-based REST API for handling teacher applications.

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## Endpoints

### POST /api/teacher-application

Submit a teacher application with the following form data:
- `first_name`: First name of the applicant
- `last_name`: Last name of the applicant
- `email`: Email address
- `mobile_phone`: Mobile phone number
- `country`: Country of residence
- `years_of_experience`: Number of years of teaching experience
- `area_of_expertise`: Area of expertise
- `study_programs`: Comma-separated list of study programs
- `is_currently_teaching`: Boolean indicating if currently teaching
- `current_university`: Name of current university (if applicable)
- `resume`: PDF file containing the application

## Example Usage

You can test the API using curl or any API client like Postman:

```bash
curl -X POST "http://localhost:8000/api/teacher-application" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "first_name=John" \
  -F "last_name=Doe" \
  -F "email=john.doe@example.com" \
  -F "mobile_phone=+1234567890" \
  -F "country=United States" \
  -F "years_of_experience=5" \
  -F "area_of_expertise=Computer Science" \
  -F "study_programs=BS Computer Science,MS Data Science" \
  -F "is_currently_teaching=true" \
  -F "current_university=Example University" \
  -F "resume=@path/to/your/resume.pdf"
``` 