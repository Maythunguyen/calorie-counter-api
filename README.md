This is an API service for a Calories Counter application, built with FastAPI and OpenAI. It reads the content from images and provides calorie information based on data sourced from Kaggle.com.



## Features
- Analyze and label food items from images

- Identify specific foods based on labels and provide accurate labeling

- Calculate total calories based on the detected foods in the image

## Tech Stack
Framework: FastAPI

Language: Python

AI Integration: OpenAI API (GPT-4)

Data Validation: Pydantic

Pandas: Reading data

Pathlib (Path): for managing file paths

uuid4: for generating unique file identifiers

shutil: for file operations like saving uploaded files

base64: for encoding and decoding file content

# Installation
Clone the repository:
```bash
git clone https://github.com/Maythunguyen/calorie-counter-api.git
#Navigate into the directory:

cd calorie-counter-api

#Create a virtual environment and activate it:

python -m venv .venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate

#Install dependencies:

pip install -r requirements.txt

#Environment Setup

#Create an .env file at the project root with your OpenAI API key:

OPENAI_API_KEY=your_openai_api_key_here


#Running the Application

#Start the FastAPI server:

uvicorn app.main:app --reload

```
The API will be available at http://localhost:8000.

## API Endpoints
Root Endpoint (GET /):

Simple health check.

Image analysis (POST /api/image_analysis):


## API Documentation

FastAPI provides automatic interactive documentation accessible via:

Swagger UI: http://localhost:8000/docs

ReDoc UI: http://localhost:8000/redoc

# Deployment
he recommended platform for deploying this backend service is Render - https://render.com/

## License
This project is licensed under the MIT License. See the LICENSE file for details

