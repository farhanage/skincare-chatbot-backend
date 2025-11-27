# app/services/prediction.py
import anyio
from app.models.ai_model import skin_model
import logging
import traceback

logger = logging.getLogger(__name__)

async def predict_disease(image_bytes: bytes):
    """
    Predict skin disease from image bytes
    Returns consistent response format for frontend
    """
    def _infer(img_bytes: bytes) -> dict:
        try:
            # Get prediction from model
            raw_result = skin_model.predict_bytes(img_bytes)
            
            # Debug log
            logger.info(f"Raw prediction result: {raw_result}")
            
            # Ensure we have the expected keys with safe defaults
            topk = raw_result.get("topk", [])
            best = raw_result.get("best", {})
            
            # Validate best prediction structure
            if not isinstance(best, dict):
                best = {"index": -1, "label": "Unknown", "score": 0.0}
            
            # Ensure best has required fields
            safe_best = {
                "index": best.get("index", -1),
                "label": best.get("label", "Unknown"),
                "score": best.get("score", 0.0)
            }
            
            # Build consistent response
            response = {
                "success": True,
                "predictions": {
                    "topk": topk,
                    "best": safe_best
                },
                "model_info": {
                    "status": raw_result.get("model_status", "enhanced_fallback"),
                    "type": "skin_disease_detector"
                },
                "message": "Analysis completed successfully"
            }
            
            # Add note if present
            if "note" in raw_result:
                response["note"] = raw_result["note"]
                
            logger.info(f"Formatted response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Prediction service error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "predictions": {
                    "topk": [],
                    "best": {"index": -1, "label": "Error", "score": 0.0}
                },
                "message": "Prediction service error"
            }
    
    # Run in thread pool
    return await anyio.to_thread.run_sync(_infer, image_bytes)