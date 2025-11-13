from fastapi import FastAPI, File, UploadFile
from roboflow import Roboflow
from PIL import Image, ImageDraw
import tempfile, io, os
from dotenv import load_dotenv
import pandas as pd
import numpy as np

load_dotenv()
ROBOFLOW_API_KEY = os.getenv("API_KEY")


app = FastAPI(title="Skin Analysis")
rf = Roboflow(api_key=ROBOFLOW_API_KEY)


# Model
acne_model = rf.workspace().project("acnedet-v1").version(2).model
skin_disease_model = rf.workspace("kelixo").project("skin_disease_ak").version(1).model
skin_class_model = rf.workspace("skn-f1vaw").project("skn-1").version(1).model


#CSV
CSV_FILE = "uploaded_skin_features.csv"
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=[
        "ID", "filename",
        "acne_count", "avg_acne_width", "avg_acne_height", "avg_acne_area",
        "papules_count", "pustules_count", "comedone_count", "nodules_count",
        "avg_redness", "global_redness",
        "skin_disease_label", "skin_disease_confidence",
        "skin_classification_labels", "acne_detected","result"
    ])
    df_init.to_csv(CSV_FILE, index=False)

# 5. Helper functions
def run_model(model, image, input_size=None, task_type="detection"):
    #Resizing the image to what the model requires
    if input_size:
        image = image.resize((input_size, input_size))
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp_file:
        image.save(tmp_file, format="JPEG", quality=95)
        tmp_file.flush()
        try:
            if task_type == "detection":
                result = model.predict(tmp_file.name, confidence=0.3, overlap=0.5)
            else:
                result = model.predict(tmp_file.name)
            return result.json()
        except Exception as e:
            return {"error": str(e)}
# Somre images are too big for the model so it makes some sense to take the center.
# Since sometimes the center is where the target is at
def crop_center_patch(image, patch_size):
    w, h = image.size
    left = max(0, (w - patch_size) // 2)
    upper = max(0, (h - patch_size) // 2)
    right = left + patch_size
    lower = upper + patch_size
    return image.crop((left, upper, right, lower))

#Take the patches and compute the red channels
def compute_redness(patch):
    arr = np.array(patch)
    red_channel = arr[:,:,0].astype(float)
    green_channel = arr[:,:,1].astype(float)
    blue_channel = arr[:,:,2].astype(float)
    redness = red_channel - (green_channel + blue_channel)/2
    return max(0, np.mean(redness))/255
#Do it for the entire image
def compute_global_redness(image):
    arr = np.array(image)
    red_channel = arr[:,:,0].astype(float)
    green_channel = arr[:,:,1].astype(float)
    blue_channel = arr[:,:,2].astype(float)
    redness = red_channel - (green_channel + blue_channel)/2
    return max(0, np.mean(redness))/255

#FastAPI
@app.post("/skinprocessing")
async def analyze_skin(file: UploadFile = File(...)):
    #Load image
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Acne detection model
    acne_results = run_model(acne_model, image, task_type="detection")
    preds = acne_results.get("predictions", []) or []
    acne_count = len(preds)
    total_width = total_height = total_area = total_redness = 0
    papules = pustules = comedones = nodules = 0
    for pred in preds:
        x, y, w, h = float(pred["x"]), float(pred["y"]), float(pred["width"]), float(pred["height"])
        left, upper, right, lower = int(x - w/2), int(y - h/2), int(x + w/2), int(y + h/2)
        patch = image.crop((left, upper, right, lower))
        total_redness += compute_redness(patch)
        total_width += w
        total_height += h
        total_area += w*h
        lesion_type = str(pred.get("class","")).lower()
        if "papule" in lesion_type:
            papules += 1
        elif "pustule" in lesion_type:
            pustules += 1
        elif "comedone" in lesion_type:
            comedones += 1
        elif "nodule" in lesion_type:
            nodules += 1
    unknown_count = acne_count - (papules + pustules + comedones + nodules)
    if unknown_count > 0:
        comedones += unknown_count
    acne_features = {
        "acne_count": acne_count,
        "avg_acne_width": total_width / acne_count if acne_count else 0,
        "avg_acne_height": total_height / acne_count if acne_count else 0,
        "avg_acne_area": total_area / acne_count if acne_count else 0,
        "avg_redness": total_redness / acne_count if acne_count else 0,
        "papules_count": papules,
        "pustules_count": pustules,
        "comedone_count": comedones,
        "nodules_count": nodules
    }

    # Skin disease classification model
    skin_patch = crop_center_patch(image, 300)
    skin_disease_results = run_model(skin_disease_model, skin_patch, input_size=300, task_type="classification")
    skin_preds = skin_disease_results.get("predictions", [])
    if skin_preds and skin_preds[0].get("predictions"):
        top_disease = skin_preds[0]["predictions"][0]
        disease_label = top_disease.get("class", "NULL")
        disease_confidence = top_disease.get("confidence", "NULL")
    else:
        disease_label, disease_confidence = "NULL", "NULL"

    # Skin general classification model pretty shitty
    skin_class_patch = crop_center_patch(image, 640)
    skin_class_results = run_model(skin_class_model, skin_class_patch, input_size=640, task_type="classification")
    class_labels = [p.get("class","NULL") for p in skin_class_results.get("predictions", [])] or ["NULL"]

    # Global redness
    global_red = compute_global_redness(image)

    # Save
    existing_df = pd.read_csv(CSV_FILE)
    next_id = int(existing_df["ID"].max() + 1) if not existing_df.empty else 1
    row = {
        "ID": next_id,
        "filename": file.filename,
        **acne_features,
        "global_redness": global_red,
        "skin_disease_label": disease_label,
        "skin_disease_confidence": disease_confidence,
        "skin_classification_labels": ",".join(class_labels),
        "acne_detected": 1 if acne_count > 0 else 0,
        "result": "NaN"
    }
    pd.DataFrame([row]).to_csv(CSV_FILE, mode="a", index=False, header=False)

    return {"filename": file.filename, "ID": next_id, **row}
