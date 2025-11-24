import logging
import tempfile
import numpy as np

logger = logging.getLogger(__name__)

def run_model(model, image, input_size=None, task_type="detection"):
    """Run ML model on image with optional resizing"""
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
            logger.error(f"Model prediction error: {str(e)}")
            return {"error": str(e)}

def crop_center_patch(image, patch_size):
    """Crop center patch from image for classification models"""
    w, h = image.size
    left = max(0, (w - patch_size) // 2)
    upper = max(0, (h - patch_size) // 2)
    right = left + patch_size
    lower = upper + patch_size
    return image.crop((left, upper, right, lower))

def compute_redness(patch):
    """Compute redness metric for a patch"""
    arr = np.array(patch)
    red_channel = arr[:, :, 0].astype(float)
    green_channel = arr[:, :, 1].astype(float)
    blue_channel = arr[:, :, 2].astype(float)
    redness = red_channel - (green_channel + blue_channel) / 2
    return max(0, np.mean(redness)) / 255

def compute_global_redness(image):
    """Compute global redness metric for entire image"""
    arr = np.array(image)
    red_channel = arr[:, :, 0].astype(float)
    green_channel = arr[:, :, 1].astype(float)
    blue_channel = arr[:, :, 2].astype(float)
    redness = red_channel - (green_channel + blue_channel) / 2
    return max(0, np.mean(redness)) / 255
