import logging
import io
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Request
from PIL import Image
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import supabase
from app.models import AnalysisResponse
from app.auth.dependencies import get_current_user
from app.services.ml_models import model_manager
from app.services.image_processing import (
    run_model,
    crop_center_patch,
    compute_redness,
    compute_global_redness
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Analysis"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/skinprocessing", response_model=AnalysisResponse)
@limiter.limit("30/minute")
async def analyze_skin(
    request: Request,
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    """
    Analyze skin image for acne detection and skin disease classification.
    Requires authentication via Bearer token.
    """
    logger.info(f"Processing skin analysis for user: {user.email}, file: {file.filename}")

    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Load image
        image_bytes = await file.read()
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Acne detection model
        acne_results = run_model(model_manager.acne_model, image, task_type="detection")

        if "error" in acne_results:
            logger.error(f"Acne model error: {acne_results['error']}")
            raise HTTPException(status_code=500, detail="Acne detection model failed")

        preds = acne_results.get("predictions", []) or []
        acne_count = len(preds)
        total_width = total_height = total_area = total_redness = 0
        papules = pustules = comedones = nodules = 0

        for pred in preds:
            x, y, w, h = float(pred["x"]), float(pred["y"]), float(pred["width"]), float(pred["height"])
            left, upper, right, lower = int(x - w/2), int(y - h/2), int(x + w/2), int(y + h/2)

            # Ensure bounds are within image
            left = max(0, left)
            upper = max(0, upper)
            right = min(image.width, right)
            lower = min(image.height, lower)

            patch = image.crop((left, upper, right, lower))
            total_redness += compute_redness(patch)
            total_width += w
            total_height += h
            total_area += w * h

            lesion_type = str(pred.get("class", "")).lower()
            if "papule" in lesion_type:
                papules += 1
            elif "pustule" in lesion_type:
                pustules += 1
            elif "comedone" in lesion_type:
                comedones += 1
            elif "nodule" in lesion_type:
                nodules += 1

        # Classify unknown lesions as comedones
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
        skin_disease_results = run_model(
            model_manager.skin_disease_model,
            skin_patch,
            input_size=300,
            task_type="classification"
        )

        skin_preds = skin_disease_results.get("predictions", [])
        if skin_preds and skin_preds[0].get("predictions"):
            top_disease = skin_preds[0]["predictions"][0]
            disease_label = top_disease.get("class")
            disease_confidence = top_disease.get("confidence")
        else:
            disease_label = None
            disease_confidence = None

        # Skin general classification model
        skin_class_patch = crop_center_patch(image, 640)
        skin_class_results = run_model(
            model_manager.skin_class_model,
            skin_class_patch,
            input_size=640,
            task_type="classification"
        )
        class_labels = [p.get("class", "Unknown") for p in skin_class_results.get("predictions", [])] or ["Unknown"]

        # Global redness
        global_red = compute_global_redness(image)

        # Save to Supabase database
        analysis_data = {
            "user_id": user.id,
            "filename": file.filename,
            **acne_features,
            "global_redness": global_red,
            "skin_disease_label": disease_label,
            "skin_disease_confidence": disease_confidence,
            "skin_classification_labels": ",".join(class_labels),
            "acne_detected": acne_count > 0,
            "result": None
        }

        result = supabase.table("skin_analyses").insert(analysis_data).execute()

        if not result.data:
            logger.error("Failed to save analysis to database")
            raise HTTPException(status_code=500, detail="Failed to save analysis")

        saved_analysis = result.data[0]
        logger.info(f"Analysis saved successfully with ID: {saved_analysis['id']}")

        return AnalysisResponse(
            id=saved_analysis["id"],
            filename=file.filename,
            acne_count=acne_features["acne_count"],
            avg_acne_width=acne_features["avg_acne_width"],
            avg_acne_height=acne_features["avg_acne_height"],
            avg_acne_area=acne_features["avg_acne_area"],
            papules_count=acne_features["papules_count"],
            pustules_count=acne_features["pustules_count"],
            comedone_count=acne_features["comedone_count"],
            nodules_count=acne_features["nodules_count"],
            avg_redness=acne_features["avg_redness"],
            global_redness=global_red,
            skin_disease_label=disease_label,
            skin_disease_confidence=disease_confidence,
            skin_classification_labels=",".join(class_labels),
            acne_detected=acne_count > 0
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during analysis")

@router.get("/analyses")
@limiter.limit("60/minute")
async def get_user_analyses(
    request: Request,
    user=Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """Get current user's analysis history"""
    try:
        result = supabase.table("skin_analyses") \
            .select("*") \
            .eq("user_id", user.id) \
            .order("created_at", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()

        return {
            "analyses": result.data,
            "count": len(result.data)
        }
    except Exception as e:
        logger.error(f"Error fetching analyses: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch analyses")

@router.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: str, user=Depends(get_current_user)):
    """Get a specific analysis by ID"""
    try:
        result = supabase.table("skin_analyses") \
            .select("*") \
            .eq("id", analysis_id) \
            .eq("user_id", user.id) \
            .single() \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return result.data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch analysis")

@router.delete("/analyses/{analysis_id}")
async def delete_analysis(analysis_id: str, user=Depends(get_current_user)):
    """Delete a specific analysis"""
    try:
        result = supabase.table("skin_analyses") \
            .delete() \
            .eq("id", analysis_id) \
            .eq("user_id", user.id) \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Analysis not found")

        logger.info(f"Analysis {analysis_id} deleted by user {user.email}")
        return {"message": "Analysis deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete analysis")
