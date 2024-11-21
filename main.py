import os
import pdfplumber
from openai import OpenAI
import json

# Set your OpenAI API key
client = OpenAI(api_key='key')
def extract_text_from_pdf(file_path):
    """
    Extracts all text from the PDF file.
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def generate_json_from_description(description):
    """
    Uses OpenAI API to create structured JSON data from the description.
    """
    prompt = f"""
    You are a JSON generator. Extract the following fields from the property description:
    - Title
    - Location
    - Features (list of features as bullet points)
    - Seller Description
    - Acreage
    - Bathrooms
    - Bedrooms
    - City
    - Code
    - County
    - Street
    - Property Type
    - Guiding Price

    Format the response strictly as JSON without any additional text, explanations, or comments.
    Do not use backticks or markdown format.
    Description:
    {description}
    """
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant that only responds in JSON format."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4o",
            temperature=0.0
        )
        response_dict = response.model_dump()  # Convert to dictionary
        raw_response = response_dict["choices"][0]["message"]["content"].strip()
        print("Raw JSON Response:", raw_response)  # Debugging
        return raw_response
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return None

def save_json_to_file(data, index):
    """
    Saves JSON data to a file.
    """
    file_name = f"output_{index}.json"
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Saved iteration {index} to {file_name}")

# Extract text from PDF
pdf_file_path = "my.pdf"  # Replace with your actual file path
pdf_text = extract_text_from_pdf(pdf_file_path)

# Process descriptions
descriptions = pdf_text.split("\n\n")  # Adjust splitting logic if needed
for index, description in enumerate(descriptions, start=1):
    structured_data = generate_json_from_description(description)
    if structured_data:
        try:
            json_data = json.loads(structured_data)  # Convert to JSON object
            save_json_to_file(json_data, index)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for iteration {index}: {e}")
            print(f"Raw Data: {structured_data}")

