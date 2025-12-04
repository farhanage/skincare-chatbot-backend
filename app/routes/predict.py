# app/routes/predict.py
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import requests
import base64
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

router = APIRouter()

load_dotenv()

# Disease detection API endpoint
DISEASE_DETECTION_API = os.getenv("DISEASE_DETECTION_API")


class PredictionResponse(BaseModel):
    success: bool
    prediction: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/predict", response_model=PredictionResponse)
async def predict_disease(
    file: UploadFile = File(...)
):
    """
    Predict skincare disease from uploaded image
    
    Args:
        file: Image file (JPEG, PNG, etc.)
    
    Returns:
        Prediction results from disease detection model
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        # Read file content
        logger.info(f"Uploading image: {file.filename}")
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )
        
        logger.info(f"Processing image: {file.filename} ({len(file_content)} bytes)")
        
        # Send binary image data directly
        # The API expects multipart/form-data with the file
        files = {
            'file': (file.filename, file_content, file.content_type)
        }
        
        # Call disease detection API
        logger.info(f"Calling disease detection API: {DISEASE_DETECTION_API}")
        response = requests.post(
            DISEASE_DETECTION_API,
            files=files,
            timeout=30
        )
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        logger.info(f"Disease detection result: {result}")
        
        return {
            "success": True,
            "prediction": result,
            "error": None
        }
        
    except requests.exceptions.Timeout:
        logger.error("Disease detection API timeout")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Disease detection service timeout. Please try again."
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Disease detection API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to connect to disease detection service: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process image: {str(e)}"
        )
