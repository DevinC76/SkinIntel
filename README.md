# Skintel

## Description

Struggling to understand your skin? **Skintel** is your intelligent skincare companion — powered by AI, it analyzes your skin condition from a single photo and recommends personalized treatments and skincare routines.

With **Skintel**, you can:

- Upload a clear photo of your face to detect acne type, severity, and other skin concerns.  
- Receive personalized skincare recommendations tailored to your skin condition.  
- Generate a visual video showing your **potential healing process** for encouragement and progress tracking.  
- Learn about active ingredients, when to see a dermatologist, and how to care for your skin properly.  

Your skin tells a story — let **Skintel** help you understand it.

---

## Key Features

- **Upload Facial Image**: Submit a photo and get AI-driven acne detection, including counts of papules, blackheads, whiteheads, nodules, pustules, and cysts.  
- **Acne Intensity Classification**: Automatically classifies acne into one of four grades: *Mild*, *Moderate*, *Moderately Severe*, or *Severe*.  
- **Personalized Recommendations**: Suggests treatment steps, key ingredients, and OTC products tailored to your skin type.  
- **Healing Simulation Video**: Generates a short, realistic video showing how your skin could heal over time.  

---

## Technologies Used

- **Backend**: Python + FastAPI, Google Gemini API (Gemini 2.5 & Veo 3.1)  
---

The diagram above illustrates the **Skintel system workflow** for skin image analysis and healing simulation.

1. The client uploads a face image to the FastAPI server.  
2. The server sends the image to **Gemini Vision** for acne detection and severity grading.  
3. The client receives structured acne data and can view skincare recommendations.  
4. Optionally, the user can generate a **healing simulation video** using the Veo video generation model.

---

## Installation

### 1.Clone the repository

```bash
https://github.com/DevinC76/SkinIntel.git
cd backend
```
### 2. Create and activate a virtual environment
#### Mac/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```
#### Windows (Command Prompt)
```bash
py -3 -m venv .venv
.venv\Scripts\activate
```

### Backend
```bash
cd backend
pip install -r requirements.txt
```

### Set up environment variables
Create a .env file in your backend directory:
```bash
GOOGLE_API_KEY=your_api_key_here
ROBOFLOW_API_KEY=your_api_key_here
```

| **Endpoint**     | **Method** | **Description**                                                                                           | **Request Body**                                                                                          | **Response Example**                                                                                                                                                                                                                                                                |
| ---------------- | ---------- | --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/vision`        | `POST`     | Uploads a facial image and analyzes acne severity using **Gemini Vision**. Returns counts and acne grade. | **form-data**:<br>• `image_file` — *(required)* Image file (`.jpg`, `.jpeg`, `.png`).                     | **Success (200):**<br>`json { "papules_count": 5, "blackheads_count": 2, "whiteheads_count": 3, "nodules_count": 1, "pustules_count": 2, "cysts_count": 0, "acne": true, "rosea": false, "intensity": "Moderate Acne" }`<br><br>**No Face Detected (200):** `json { "Invalid": 0 }` |
| `/recommend`     | `POST`     | Generates skincare recommendations and treatment steps based on the acne analysis.                        | **application/json**:<br>`json { "intensity": "Moderate Acne", "papules_count": 5, "pustules_count": 2 }` | **Success (200):**<br>`json { "recommendation": "You have moderate acne. Use a gentle salicylic acid cleanser, benzoyl peroxide spot treatment, and non-comedogenic moisturizer." }`                                                                                                |
| `/healing-video` | `POST`     | Generates a realistic short video showing gradual acne healing.                                           | **form-data**:<br>• `image_file` — *(required)* Facial image file (`.jpg`, `.jpeg`, `.png`).              | **Response:** Downloads `healing_progression.mp4`.                                                                                                                                                                                                                                  |
