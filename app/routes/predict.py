# app/routes/predict.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.prediction import predict_disease
import logging
import traceback

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Predict skin disease from uploaded image
    Available at:
    - POST /predict (legacy)
    - POST /api/v1/predict (versioned)
    """
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    
    try:
        # Read file contents
        contents = await file.read()
        
        if len(contents) == 0:
            raise HTTPException(400, "Uploaded file is empty")
        
        logger.info(f" Processing image: {file.filename} ({len(contents)} bytes)")
        
        # Run prediction
        result = await predict_disease(contents)
        
        # Check if prediction has error
        if result.get("success") is False:
            error_msg = result.get("error", "Unknown prediction error")
            logger.error(f"Prediction failed: {error_msg}")
            raise HTTPException(500, f"Prediction failed: {error_msg}")
        
        logger.info(f" Prediction successful: {result['predictions']['best']['label']} ({result['predictions']['best']['score']:.2%})")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Log full error details
        logger.error(f"Unexpected error in predict route: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return consistent error response
        return {
            "success": False,
            "error": str(e),
            "predictions": {
                "topk": [],
                "best": {"index": -1, "label": "Error", "score": 0.0}
            },
            "message": "Internal server error during prediction"
        }

# Test endpoints untuk kedua path
@router.get("/test")
async def test_endpoint_v1():
    """Test endpoint untuk API v1"""
    return {
        "message": "Predict route is working! (API v1)",
        "endpoint": "GET /api/v1/predict/test",
        "status": "active"
    }

@router.get("/predict/test")
async def test_endpoint_legacy():
    """Test endpoint untuk legacy path"""
    return {
        "message": "Predict route is working! (Legacy)",
        "endpoint": "GET /predict/test", 
        "status": "active"
    }