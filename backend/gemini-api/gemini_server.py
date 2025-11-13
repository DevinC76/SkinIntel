from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import tempfile
import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=api_key)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def analyze_image(imagepath: str, mime_type: str):
    with open(imagepath, 'rb') as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),
            """
            Analyze the image and return a single JSON object describing acne details.

            Instructions:
            1. Detect and count only acne-related lesions (papules, blackheads, whiteheads, nodules, pustules, cysts).
            2. If no face or multiple faces are detected, return exactly:
               { "Invalid": 0 }
            3. Include an overall acne intensity classification:
               one of ["Mild Acne", "Moderate Acne", "Moderately Severe Acne", "Severe Acne"].
            4. Return only valid JSON (no extra commentary or text).

            Output format example:
            {
                "papules_count": 10,
                "blackheads_count": 10,
                "whiteheads_count": 10,
                "nodules_count": 10,
                "pustules_count": 10,
                "cysts_count": 10,
                "acne": true,
                "rosea": false,
                "intensity": "Severe Acne"
            }
            """
        ]
    )

    return response


def generate_healing_video(image_path: str):
    """
    Generates a video showing acne healing progression.
    """
    prompt = (
        "A realistic short time-lapse video showing the same person's face healing from acne. "
        "Acne gradually fades, redness and inflammation reduce, and the skin becomes clearer over time. "
        "Keep facial structure, lighting, and background consistent. Duration 10 seconds."
    )

    # Load acne image
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # Generate healing video
    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=prompt,
        image={"mime_type": "image/jpeg", "data": image_bytes},
    )

    # Poll for completion
    while not operation.done:
        print("Waiting for video generation to complete...")
        time.sleep(10)
        operation = client.operations.get(operation)

    # Download and save
    video = operation.response.generated_videos[0]
    filename = "healing_progression.mp4"
    client.files.download(file=video.video)
    video.video.save(filename)
    print(f"✅ Video saved as {filename}")
    return filename


@app.post("/vision")
async def vision(image_file: UploadFile = File(...)):
    mime_type = image_file.content_type

    if not mime_type.startswith("image/"):
        return JSONResponse({"error": "Invalid file type. Please upload an image."}, status_code=400)

    extension = mime_type.split("/")[-1]
    if extension == "jpeg":
        extension = "jpg"

    with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as tmp:
        tmp.write(await image_file.read())
        temp_path = tmp.name

    try:
        result = analyze_image(temp_path, mime_type)
        return JSONResponse({"result": result.text})
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/recommend")
async def recommend(request: Request):
    try:
        data = await request.json()
        if not data:
            return JSONResponse({"error": "No JSON data provided."}, status_code=400)

        acne_data = json.dumps(data, indent=2)

        prompt = f"""
        You are a dermatologist assistant.
        Based on this acne analysis result:
        {acne_data}

        Recommend an appropriate skincare routine and product ingredients.

        Your response should include:
        1. A short explanation of the acne type and intensity.
        2. Recommended skincare steps (cleanser, treatment, moisturizer, sunscreen).
        3. Key ingredients to look for (e.g. salicylic acid, benzoyl peroxide, niacinamide).
        4. Gentle over-the-counter product suggestions.
        5. When to see a dermatologist if acne is severe or cystic.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
        )

        return JSONResponse({"recommendation": response.text})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/healing-video")
async def healing_video(image_file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(await image_file.read())
        temp_path = tmp.name

    try:
        video_path = generate_healing_video(temp_path)
        return FileResponse(video_path, media_type="video/mp4", filename="healing_progression.mp4")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# Run with: uvicorn app:app --reload
