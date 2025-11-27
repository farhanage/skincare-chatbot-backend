# app/routes/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import requests
import json

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    disease_info: Optional[dict] = None  # FIXED: Ubah ke Optional

class ChatResponse(BaseModel):
    success: bool
    response: str
    message: str = ""
    products: list = []  # Recommended products with full details

# Konfigurasi Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"  # Model lebih cepat dari llama3

# Cache sederhana untuk response cepat
QUICK_RESPONSES = {
    "produk": "Untuk {disease}, saya sarankan:\n\n**Produk Perawatan:**\n- Sunscreen SPF 50+ (Skin Aqua, Biore)\n- Gentle cleanser (Cetaphil, Simple)\n- Pelembap non-comedogenic (Hada Labo, Wardah)\n- Spot treatment (tea tree oil)\n\n**Brand Lokal Terjangkau:** Somethinc, Avoskin, Whitelab\n\nKonsultasi dokter kulit untuk rekomendasi spesifik!",
    
    "obat": "Pengobatan {disease} tergantung tingkat keparahan:\n\n**Opsi Umum:**\n- Krim topikal (benzoyl peroxide, retinoid)\n- Antibiotik oral (jika perlu)\n- Terapi laser/light (prosedur dokter)\n\n**PENTING:** Jangan self-medicate! Konsultasi dermatologist untuk treatment plan yang tepat.",
    
    "apa itu": "**{disease}** adalah kondisi kulit yang terdeteksi dengan akurasi {confidence}%.\n\nDeteksi AI bersifat screening awal, bukan diagnosis medis.\n\nUntuk diagnosis pasti dan treatment plan, silakan konsultasi dengan dokter spesialis kulit (Sp.KK).",
    
    "penyebab": "Penyebab {disease} bisa beragam:\n\n- Faktor genetik\n- Lingkungan (polusi, cuaca)\n- Diet dan lifestyle\n- Ketidakseimbangan hormon\n\nDokter kulit dapat identifikasi penyebab spesifik melalui pemeriksaan menyeluruh.",
    
    "cegah": "Tips pencegahan {disease}:\n\n**Perlindungan:**\n- Gunakan sunscreen setiap hari\n- Hindari iritan dan alergen\n- Jaga kebersihan kulit\n\n**Gaya Hidup:**\n- Diet seimbang\n- Cukup tidur & kelola stress\n- Rutin periksa kulit\n\nDeteksi dini sangat penting!",
}

def get_quick_response(user_message: str, disease_info: dict) -> str:
    """Cari response cepat dari cache"""
    user_lower = user_message.lower()
    disease_name = disease_info.get('disease', 'kondisi kulit') if disease_info else 'kondisi kulit'
    confidence = f"{(disease_info.get('confidence', 0) * 100):.1f}%" if disease_info else "0%"
    
    for key, template in QUICK_RESPONSES.items():
        if key in user_lower:
            return template.format(disease=disease_name, confidence=confidence)
    return None

def get_rag_response(user_message: str, disease_info: dict) -> dict:
    """Get response from RAG service with product recommendations"""
    try:
        from app.services.rag_chat import generate_response
        
        # Enhance user message with disease context if available
        enhanced_message = user_message
        if disease_info:
            disease_name = disease_info.get('disease', '')
            if disease_name:
                enhanced_message = f"{user_message} (Kondisi kulit terdeteksi: {disease_name})"
        
        # Get response from RAG service
        result = generate_response(enhanced_message, disease_info)
        
        # Add disease info to response if available
        if disease_info and result.get('response'):
            disease_name = disease_info.get('disease', '')
            confidence = disease_info.get('confidence', 0) * 100
            
            # Add context about detected condition
            if disease_name and 'detection' not in result['response'].lower():
                detection_note = f"\n\n*Catatan: AI mendeteksi kondisi {disease_name} dengan akurasi {confidence:.1f}%. Untuk diagnosis medis yang akurat, konsultasikan dengan dokter kulit.*"
                result['response'] += detection_note
        
        return result
        
    except Exception as e:
        logger.error(f"RAG service error: {e}")
        # Fallback to quick response
        quick_response = get_quick_response(user_message, disease_info)
        return {
            "response": quick_response if quick_response else "Maaf, terjadi kesalahan. Silakan coba lagi atau konsultasi dengan dokter kulit.",
            "products": []
        }

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(chat_request: ChatRequest):
    """
    Chat endpoint untuk konsultasi AI tentang kondisi kulit dengan rekomendasi produk
    """
    try:
        logger.info(f"Chat request: {chat_request.message}")
        logger.info(f"Disease info: {chat_request.disease_info}")
        
        # Validasi input
        if not chat_request.message or len(chat_request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get AI response with product recommendations from RAG service
        result = get_rag_response(
            chat_request.message, 
            chat_request.disease_info or {}
        )
        
        response_text = result.get('response', 'Maaf, terjadi kesalahan.')
        products = result.get('products', [])
        
        logger.info(f"Response generated: {response_text[:100]}...")
        logger.info(f"Products recommended: {len(products)} items")
        
        return ChatResponse(
            success=True,
            response=response_text,
            message="AI response generated successfully",
            products=products
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )