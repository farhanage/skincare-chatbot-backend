import os
import logging
from typing import List, Dict, Optional
import requests

logger = logging.getLogger(__name__)

# Configure LLM Inference API
LLM_INFERENCE_API = os.getenv("LLM_INFERENCE_API")


class ChatbotService:
    """Service for AI chatbot interactions using external LLM Inference API"""
    
    def __init__(self):
        self.api_url = LLM_INFERENCE_API + "/api/chat" 
        if not self.api_url:
            logger.warning("LLM_INFERENCE_API not configured")
    
    async def get_response(
        self,
        user_message: str,
        chat_history: List[Dict] = None,
        disease_context: Optional[Dict] = None,
        available_products: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Get AI response for user message
        
        Args:
            user_message: The user's message
            chat_history: Previous conversation history (not used with external API)
            disease_context: Optional disease detection context
            available_products: Optional list of available products (not used with external API)
            
        Returns:
            Dict with 'text' and optional 'products' list
        """
        try:
            if not self.api_url:
                raise ValueError("LLM_INFERENCE_API not configured")
            
            # Prepare disease_info for API request
            disease_info = {}
            if disease_context and disease_context.get("disease"):
                disease_info = {
                    "disease": disease_context.get("disease", ""),
                    "confidence": disease_context.get("confidence", 0.0)
                }
            
            # Make request to LLM inference API
            payload = {
                "message": user_message,
                "disease_info": disease_info
            }
            
            logger.info(f"Calling LLM API: {self.api_url}")
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            if not result.get("success"):
                raise ValueError(f"API error: {result.get('message', 'Unknown error')}")
            
            return {
                "text": result.get("response", ""),
                "products": result.get("products", [])
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API request error: {e}")
            return {
                "text": "Maaf, saya mengalami kendala dalam menghubungi layanan AI. Silakan coba lagi nanti.",
                "products": []
            }
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            return {
                "text": "Maaf, saya mengalami kendala. Silakan coba lagi atau hubungi customer service kami.",
                "products": []
            }
    
    async def generate_chat_title(self, first_message: str) -> str:
        """Generate a short title for the chat based on first message"""
        # Simple title generation from first few words
        words = first_message.split()[:5]
        title = " ".join(words)
        return title[:50] if title else "New Chat"


# Singleton instance
chatbot_service = ChatbotService()
