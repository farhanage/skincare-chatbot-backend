# app/services/rag_chat.py
from app.database.vector_db import search_products
import logging
import requests
import json
import re

logger = logging.getLogger(__name__)

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:latest"  # Change this to your installed model

def call_ollama(prompt: str, context: str = "") -> dict:
    """Call Ollama API for text generation and return response with product references"""
    try:
        # First check if Ollama is accessible
        try:
            health_check = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
            if health_check.status_code != 200:
                logger.warning(f"Ollama health check failed with status {health_check.status_code}")
                return None
        except requests.exceptions.RequestException:
            logger.warning("Ollama is not running or not accessible. Start with: ollama serve")
            return None
        
        full_prompt = f"""You are a skincare expert assistant for a skincare products e-commerce platform.

CONTEXT:
{context}

USER QUESTION: {prompt}

Provide a helpful, concise response in Indonesian language. When recommending products:
1. Explain WHY each product is suitable for the user's condition
2. Mention the product name clearly
3. Highlight key benefits or ingredients
4. Keep total response under 200 words

Be conversational and helpful. If multiple products are available, recommend 2-3 best options."""

        logger.info(f"Calling Ollama with model: {OLLAMA_MODEL}")
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 200  # Limit response length for faster generation
                }
            },
            timeout=60  # Increased to 60s for first-time model loading
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("Ollama response received successfully")
            return {"response": result.get("response", "").strip(), "success": True}
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Cannot connect to Ollama at {OLLAMA_BASE_URL}: {e}")
        logger.error("Make sure Ollama is running: ollama serve")
        return None
    except requests.exceptions.Timeout:
        logger.error("Ollama request timed out (60s). Model may be loading or system is slow.")
        logger.error("Try: ollama run llama3.2 'test' (to preload model)")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling Ollama: {e}", exc_info=True)
        return None

def generate_response(user_message: str, conversation_history: list = None) -> dict:
    """
    Generate response using RAG (Retrieval Augmented Generation) with Ollama
    Returns: {
        "response": str (text response),
        "products": list (recommended products with full details)
    }
    """
    try:
        # Load skincare knowledge base
        from app.database.products_data import SKINCARE_KNOWLEDGE
        
        # Detect if this is an information/medical question
        user_msg_lower = user_message.lower()
        info_keywords = ['apa itu', 'what is', 'jelaskan', 'explain', 'maksud', 'meaning', 'define', 
                         'gejala', 'symptom', 'penyebab', 'cause', 'cara mengobati', 'how to treat',
                         'berbahaya', 'danger', 'menular', 'contagious']
        is_info_question = any(keyword in user_msg_lower for keyword in info_keywords)
        
        # Check for price filter FIRST
        price_limit = None
        if 'dibawah' in user_msg_lower or 'di bawah' in user_msg_lower or 'under' in user_msg_lower or 'harga' in user_msg_lower:
            # Remove dots and extract numbers
            # "100.000" -> "100000", "100 ribu" -> "100000"
            normalized = user_msg_lower.replace('.', '').replace(',', '')
            normalized = normalized.replace(' ribu', '000').replace('ribu', '000')
            normalized = normalized.replace(' rb', '000').replace('rb', '000')
            normalized = normalized.replace(' k', '000').replace('k', '000')
            
            # Find all numbers
            numbers = re.findall(r'\d+', normalized)
            if numbers:
                # Take the first number found
                price_limit = int(numbers[0])
        logger.info(f"Extracted price limit: Rp {price_limit:,}")
        
        # Search relevant products (increase to 15 for better selection before price filtering)
        top_k = 15 if price_limit else 5
        relevant_products = search_products(user_message, top_k=top_k)
        
        # Apply price filter if detected
        if price_limit and relevant_products:
            original_count = len(relevant_products)
            relevant_products = [p for p in relevant_products if p.get('price', 0) <= price_limit]
            logger.info(f"Price filter applied: {original_count} -> {len(relevant_products)} products (≤ Rp {price_limit:,})")
        
        # Build comprehensive context from products and knowledge base
        product_context = f"SKINCARE KNOWLEDGE BASE:\n{SKINCARE_KNOWLEDGE}\n\n"
        
        if relevant_products and not is_info_question:
            if price_limit:
                product_context += f"=== AVAILABLE PRODUCTS WITHIN BUDGET (≤ Rp {price_limit:,}) ===\n\n"
            else:
                product_context += "=== AVAILABLE PRODUCTS IN OUR STORE ===\n\n"
            
            for idx, product in enumerate(relevant_products, 1):
                product_context += f"{idx}. **{product['name']}** (Rp {product['price']:,})\n"
                product_context += f"   Category: {product.get('category', 'General')}\n"
                if product.get('for_conditions'):
                    product_context += f"   Best for: {', '.join(product['for_conditions'])}\n"
                product_context += f"   Description: {product['description']}\n"
                if product.get('ingredients'):
                    product_context += f"   Key Ingredients: {product['ingredients']}\n"
                if product.get('usage'):
                    product_context += f"   How to Use: {product['usage']}\n"
                product_context += "\n"
            
            # Add note if no products found within budget
            if price_limit and len(relevant_products) == 0:
                product_context += f"NOTE: No products found within budget of Rp {price_limit:,}. Minimum product price is Rp 18,000.\n"
        
        # Customize prompt based on question type
        if is_info_question:
            # For info questions, add explicit instruction to NOT recommend products
            custom_instruction = "\n\nIMPORTANT: User is asking for MEDICAL INFORMATION, not product recommendations. Provide educational information about the condition ONLY. DO NOT recommend products. Guide them to consult a dermatologist for diagnosis."
            enhanced_message = user_message + custom_instruction
        elif price_limit:
            # For price queries, emphasize the budget constraint
            custom_instruction = f"\n\nIMPORTANT: User has a budget constraint of Rp {price_limit:,}. ONLY recommend products from the list that are within this budget. Mention the price clearly."
            enhanced_message = user_message + custom_instruction
        else:
            enhanced_message = user_message
        
        # Try to get response from Ollama
        ollama_result = call_ollama(enhanced_message, product_context)
        
        if ollama_result and ollama_result.get("success"):
            logger.info(f"Generated response using Ollama for: '{user_message}'")
            # For info questions, don't return products
            if is_info_question:
                return {
                    "response": ollama_result["response"],
                    "products": []  # No products for medical info questions
                }
            else:
                return {
                    "response": ollama_result["response"],
                    "products": relevant_products[:3]  # Return top 3 products
                }
        
        # Fallback to rule-based response if Ollama is not available
        logger.warning("Ollama not available, using fallback response")
        
        user_msg_lower = user_message.lower()
        
        # Check if this is an information/medical question (not product request)
        info_keywords = ['apa itu', 'what is', 'jelaskan', 'explain', 'maksud', 'meaning', 'define', 
                         'gejala', 'symptom', 'penyebab', 'cause', 'cara mengobati', 'how to treat',
                         'berbahaya', 'danger', 'menular', 'contagious']
        is_info_question = any(keyword in user_msg_lower for keyword in info_keywords)
        
        # Check for price filter
        price_limit = None
        if 'dibawah' in user_msg_lower or 'di bawah' in user_msg_lower or 'under' in user_msg_lower:
            # Extract number (e.g., "dibawah 100000" or "dibawah 100 ribu")
            # Replace word forms with zeros first, then find all numbers
            normalized = user_msg_lower.replace(' ribu', '000').replace('ribu', '000').replace(' rb', '000').replace('rb', '000').replace('k', '000')
            numbers = re.findall(r'\d+', normalized)
            if numbers:
                price_limit = int(numbers[0])
                # Filter products by price
                if relevant_products:
                    relevant_products = [p for p in relevant_products if p.get('price', 0) <= price_limit]
        
        # If asking about medical condition/disease (not product related)
        if is_info_question:
            # Try to extract the disease/condition name from the question
            disease_name = None
            
            # Look for patterns like "apa itu X", "what is X", "jelaskan X"
            patterns = [
                r'apa itu\s+([a-zA-Z\s]+?)(?:\?|$|,|\s+terus)',
                r'what is\s+([a-zA-Z\s]+?)(?:\?|$|,)',
                r'jelaskan\s+(?:tentang\s+)?([a-zA-Z\s]+?)(?:\?|$|,)',
                r'gejala\s+(?:dari\s+)?([a-zA-Z\s]+?)(?:\?|$|,)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, user_msg_lower)
                if match:
                    disease_name = match.group(1).strip()
                    break
            
            # Build response
            if disease_name:
                response = f"Untuk informasi medis tentang **{disease_name.title()}**, saya sarankan:\n\n"
            else:
                response = "Untuk informasi medis yang Anda tanyakan, saya sarankan:\n\n"
            
            response += "1. **Konsultasi dengan Dokter Kulit (Sp.KK)** untuk diagnosis dan penjelasan medis yang akurat\n"
            response += "2. Gunakan fitur **Upload Gambar** di aplikasi untuk deteksi AI (bukan diagnosis medis)\n"
            response += "3. Baca **Knowledge Base** aplikasi untuk informasi umum kondisi kulit\n\n"
            
            # Add helpful note about Ollama being offline
            response += "⚠️ *Catatan: Chatbot AI sedang offline. Untuk penjelasan detail, pastikan Ollama running.*\n\n"
            response += "Apakah Anda ingin saya rekomendasikan **produk perawatan** untuk kondisi ini?"
            
            return {
                "response": response,
                "products": []  # Don't show products for medical questions
            }
        
        # Product recommendation logic
        if any(word in user_msg_lower for word in ['kulit', 'skin', 'jerawat', 'acne', 'wajah', 'face']):
            if relevant_products:
                # Apply price filter info to response
                price_info = f" dengan harga di bawah Rp {price_limit:,}" if price_limit else ""
                products_text = "\n".join([f"- **{p['name']}** - Rp {p['price']:,}: {p['description'][:80]}..." for p in relevant_products[:3]])
                response = f"Rekomendasi produk{price_info}:\n\n{products_text}\n\n💡 Tips: Gunakan fitur upload gambar untuk diagnosis kulit yang lebih akurat."
            else:
                if price_limit:
                    response = f"Maaf, tidak ada produk yang sesuai dengan budget di bawah Rp {price_limit:,}. Produk kami mulai dari Rp 18,000. Apakah Anda ingin melihat produk terjangkau lainnya?"
                else:
                    response = "Saya memahami Anda bertanya tentang kulit. Untuk diagnosis kulit yang akurat, silakan gunakan fitur upload gambar pada aplikasi kami. Untuk produk perawatan kulit, kami memiliki berbagai pilihan yang tersedia."
        
        elif any(word in user_msg_lower for word in ['harga', 'price', 'mahal', 'murah', 'beli', 'buy', 'budget']):
            if relevant_products:
                price_info = f" di bawah Rp {price_limit:,}" if price_limit else ""
                products_text = "\n".join([f"- **{p['name']}** - Rp {p['price']:,}" for p in relevant_products[:3]])
                response = f"Produk{price_info}:\n\n{products_text}\n\n📦 Klik produk untuk detail lengkap dan tambahkan ke keranjang."
            else:
                if price_limit:
                    response = f"Tidak ada produk dengan harga di bawah Rp {price_limit:,} untuk kriteria tersebut. Produk termurah kami adalah Nivea Creme Soap (Rp 18,000). Apakah Anda ingin melihat produk affordable lainnya?"
                else:
                    response = "Silakan sebutkan produk spesifik yang ingin Anda ketahui harganya, atau jelaskan kebutuhan kulit Anda dengan budget yang diinginkan."
        
        elif any(word in user_msg_lower for word in ['rekomendasi', 'recommend', 'sarankan', 'suggest', 'bagus', 'terbaik', 'best']):
            if relevant_products:
                price_info = f" (budget di bawah Rp {price_limit:,})" if price_limit else ""
                products_text = "\n".join([f"- **{p['name']}** - Rp {p['price']:,}: {p['description'][:80]}..." for p in relevant_products[:3]])
                response = f"Rekomendasi produk untuk Anda{price_info}:\n\n{products_text}\n\n✨ Produk-produk ini dipilih berdasarkan kebutuhan yang Anda sebutkan."
            else:
                if price_limit:
                    response = f"Maaf, tidak ada produk yang match dengan budget Rp {price_limit:,}. Bisa sebutkan jenis produk yang dibutuhkan? (cleanser, serum, sunscreen, dll)"
                else:
                    response = "Bisa Anda jelaskan lebih detail tentang jenis kulit atau masalah kulit yang ingin diatasi? Saya akan berusaha memberikan rekomendasi yang tepat."
        
        else:
            # General query - only show products if they seem relevant
            if relevant_products and any(word in user_msg_lower for word in ['produk', 'product', 'skincare', 'perawatan', 'treatment']):
                price_info = f" di bawah Rp {price_limit:,}" if price_limit else ""
                products_text = "\n".join([f"- **{p['name']}** - Rp {p['price']:,}" for p in relevant_products[:3]])
                response = f"Produk yang mungkin Anda cari{price_info}:\n\n{products_text}\n\n💬 Tanyakan lebih spesifik untuk rekomendasi yang lebih tepat!"
            else:
                response = "Terima kasih atas pertanyaan Anda! Saya adalah asisten produk skincare. Tanyakan tentang:\n\n"
                response += "🔹 Rekomendasi produk (e.g., 'produk untuk jerawat')\n"
                response += "🔹 Harga produk (e.g., 'produk dibawah 100ribu')\n"
                response += "🔹 Info kondisi kulit (gunakan fitur upload gambar)\n\n"
                response += "Ada yang bisa saya bantu?"
        
        return {
            "response": response,
            "products": relevant_products[:3] if relevant_products else []
        }
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return {
            "response": "Maaf, terjadi error dalam memproses permintaan Anda. Silakan coba lagi atau gunakan fitur upload gambar untuk konsultasi kulit.",
            "products": []
        }