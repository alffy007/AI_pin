from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from openai import OpenAI
import json
import base64


app = FastAPI()

IMAGEDIR = "images/"

api_key = ""

client = OpenAI(api_key=api_key)


# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


# Cached interests
cached_data = {
    "interests": ["football", "drawing", "reading"],
    "activities": [],
    "note_title": "ASIC Design Flow",
    "note_description":"Explaining about ASIC design flow in the note "
}

# Define the system and user prompts
system_prompt = """
You are an AI assistant responsible for generating structured JSON outputs. 
Your job is to detect children's activities, update their interests based on observations, and return a valid JSON object.
"""

user_message = f"""
You are an AI that observes children's activities and maintains a JSON-based cache of their interests. 

1. Infer the activity from the provided image if it related to studying like reading books or watching academic youtube video then show the activity like that.
2. Update the `interests` list in the cache:
   - Add the predicted intrests curated from the overall impression to the list if it represents a new interest.
   - Retain all previously observed interests in the list.
   - do not delete any thing from the cached data list   
3. Update the `activities` list in the cache:
   - Add the detected activity to the list.
   - Retain all previously observed activities in the list.
   - do not delete any thing from the cached data list   
4. Update the `note_title` and `note_description` in the cache only if image has some kind of learning material:
    - The `note_title` should be the name of the activity.
    - The `note_description` should be a brief description of the activity.
    - you can update fully if detected note is different from the cached note       
3. Always respond in the following JSON format:
{{
    "interests": [<list_of_interests>],
    "activities": [<list_of_detected_activity>],
    "note_title": "<note_title>",
    "note_description": "<note_description>"
}}
for example:
{{
    "interests": ["football", "drawing", "reading"],
    "activities": ["football", "reading"]
    "note_title": "ASIC Design Flow",
    "note_description":"Explaining about ASIC design flow in the note "
}}
4
Use the cached data below for the initial impression of the character:
{json.dumps(cached_data)}

dont forget to return the JSON object as the output and also dont forget to close the bracket
IF THE IMAGE IS NOT CLEAR OR THE ACTIVITY IS NOT RECOGNIZABLE, NO DIFFRENCE BETWEEN CACHED DATA THEN YOU SHOULD RETURN SAME EXACT CACHED JSON DATA AS OUTPUT(VERY IMPORTANT) 

Now, process the image and generate the updated JSON response.
"""


@app.get("/")
async def root():
    return {"message": "Hello World"}


def find_min(a, b):
    if a < b:
        return a
    else:
        return b


@app.post("/upload/")
async def getimages(image: UploadFile = File(...)):
    image.filename = "dummy.jpg"
    contents = await image.read()
    with open(f"{IMAGEDIR}{image.filename}", "wb") as f:
        f.write(contents)
        # Getting the base64 string  
    base64_image = encode_image(f"{IMAGEDIR}{image.filename}")
        
    response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": user_message,
                        },
                        {
                        "type": "image_url",
                        "image_url": {
                            "url":  f"data:image/jpeg;base64,{base64_image}"
                        },
                        },
                    ],
                    },
                    {
                    "role": "system",
                    "content": system_prompt,
                    }
                ],
                max_tokens=100,
                temperature=0,
    )
    
    # Extract and print the result
    result = response.choices[0].message.content.strip()
    # print(response.choices)
    cached_data = result
    print(cached_data)
    # Validate the JSON
    try:
        json_output = json.loads(result)
        print(json_output)
    except json.JSONDecodeError:
        print("Invalid JSON:", result)
        
    return {"status": "ok"}





