"""
Advanced RAG Chat Service with Comprehensive Intent Understanding
Handles multiple query types with intelligent product recommendations
"""

import requests
import logging
import re
from typing import Dict, List, Optional, Tuple
from app.database.vector_db import search_products
from app.database.products_data import SKINCARE_KNOWLEDGE

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"


class IntentClassifier:
    """Advanced intent classification for user queries"""
    
    INTENT_PATTERNS = {
        'medical_info': [
            'apa itu', 'what is', 'jelaskan', 'explain', 'maksud', 'meaning', 'define',
            'gejala', 'symptom', 'penyebab', 'cause', 'cara mengobati', 'how to treat',
            'berbahaya', 'danger', 'menular', 'contagious', 'ciri-ciri', 'characteristics',
            'kenapa', 'mengapa', 'why', 'apakah', 'is it', 'bisakah', 'can it'
        ],
        'product_search': [
            'rekomendasi', 'recommend', 'saran', 'suggest', 'produk', 'product',
            'bagus', 'good', 'cocok', 'suitable', 'ada', 'have', 'jual', 'sell',
            'cari', 'looking for', 'butuh', 'need', 'mau', 'want', 'ingin', 'wish'
        ],
        'price_query': [
            'harga', 'price', 'murah', 'cheap', 'mahal', 'expensive', 'budget',
            'terjangkau', 'affordable', 'dibawah', 'under', 'maksimal', 'maximum'
        ],
        'comparison': [
            'banding', 'compare', 'vs', 'atau', 'or', 'lebih baik', 'better',
            'pilih', 'choose', 'mana', 'which', 'perbedaan', 'difference'
        ],
        'routine': [
            'rutinitas', 'routine', 'urutan', 'order', 'step', 'langkah',
            'cara pakai', 'how to use', 'pagi', 'morning', 'malam', 'night'
        ],
        'ingredient': [
            'kandungan', 'ingredient', 'komposisi', 'composition', 'mengandung', 'contains',
            'ada niacinamide', 'ada retinol', 'ada vitamin', 'dengan', 'with'
        ]
    }
    
    @staticmethod
    def classify(user_message: str) -> Dict[str, bool]:
        """Classify user intent from message"""
        msg_lower = user_message.lower()
        intents = {}
        
        for intent_type, keywords in IntentClassifier.INTENT_PATTERNS.items():
            intents[intent_type] = any(keyword in msg_lower for keyword in keywords)
        
        return intents


class PriceExtractor:
    """Extract and normalize price constraints from user queries"""
    
    PRICE_PATTERNS = [
        r'(?:di ?bawah|under|maksimal|max|budget|kurang dari|< ?)\s*(?:rp\.?\s*)?(\d+(?:[.,]\d+)*)\s*(?:ribu|rb|k|juta|jt)?',
        r'harga\s*(?:di ?bawah|under|maksimal|max|kurang dari)?\s*(?:rp\.?\s*)?(\d+(?:[.,]\d+)*)\s*(?:ribu|rb|k|juta|jt)?',
        r'(?:rp\.?\s*)?(\d+(?:[.,]\d+)*)\s*(?:ribu|rb|k|juta|jt)\s*(?:ke ?bawah|atau kurang|atau dibawah)',
        r'budget\s*(?:rp\.?\s*)?(\d+(?:[.,]\d+)*)\s*(?:ribu|rb|k|juta|jt)?',
        r'(?:yang|yg)\s*(?:kurang dari|< ?)\s*(?:rp\.?\s*)?(\d+(?:[.,]\d+)*)\s*(?:ribu|rb|k|juta|jt)?'
    ]
    
    @staticmethod
    def extract(user_message: str) -> Optional[int]:
        """Extract price limit from message"""
        msg_lower = user_message.lower()
        
        for pattern in PriceExtractor.PRICE_PATTERNS:
            match = re.search(pattern, msg_lower)
            if match:
                price_str = match.group(1).replace('.', '').replace(',', '')
                try:
                    price_limit = int(price_str)
                    
                    # Handle suffixes
                    if 'juta' in msg_lower or 'jt' in msg_lower:
                        price_limit *= 1000000
                    elif 'ribu' in msg_lower or 'rb' in msg_lower or ('k' in msg_lower and price_limit < 1000):
                        price_limit *= 1000
                    
                    return price_limit
                except ValueError:
                    continue
        
        return None


class ConditionExtractor:
    """Extract skin conditions and concerns from user queries"""
    
    CONDITION_KEYWORDS = {
        'jerawat': ['jerawat', 'acne', 'breakout', 'pimple', 'komedo', 'blackhead', 'whitehead'],
        'kering': ['kering', 'dry', 'dehidrasi', 'dehydrated', 'flaky', 'bersisik'],
        'berminyak': ['berminyak', 'oily', 'greasy', 'kilang', 'shiny'],
        'sensitif': ['sensitif', 'sensitive', 'iritasi', 'irritated', 'kemerahan', 'redness'],
        'kusam': ['kusam', 'dull', 'tidak cerah', 'gelap', 'dark'],
        'aging': ['aging', 'keriput', 'wrinkle', 'fine line', 'garis halus', 'kendur', 'sagging'],
        'hiperpigmentasi': ['flek', 'dark spot', 'hiperpigmentasi', 'bekas', 'scar', 'melasma'],
        'pori': ['pori', 'pore', 'large pore', 'pori besar']
    }
    
    @staticmethod
    def extract(user_message: str) -> List[str]:
        """Extract skin conditions from message"""
        msg_lower = user_message.lower()
        conditions = []
        
        for condition, keywords in ConditionExtractor.CONDITION_KEYWORDS.items():
            if any(keyword in msg_lower for keyword in keywords):
                conditions.append(condition)
        
        return conditions


def check_ollama_health() -> bool:
    """Check if Ollama service is available"""
    try:
        health_check_url = "http://localhost:11434/api/tags"
        response = requests.get(health_check_url, timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def call_ollama(user_message: str, product_context: str = "", custom_instruction: str = "", 
                temperature: float = 0.7, max_tokens: int = 300) -> Optional[Dict]:
    """Call Ollama API with advanced configuration"""
    try:
        if not check_ollama_health():
            logger.warning("Ollama health check failed")
            return None
        
        # Construct comprehensive system prompt
        system_context = f"""You are an expert skincare consultant AI for a professional online skincare store.

KNOWLEDGE BASE:
{SKINCARE_KNOWLEDGE}

{product_context}

YOUR ROLE:
- Provide accurate, personalized skincare advice
- Recommend suitable products based on user's skin concerns
- Explain product benefits and usage clearly
- Guide users with professional yet friendly tone
- Always prioritize skin health and safety

RESPONSE GUIDELINES:
- Be concise but comprehensive (2-4 paragraphs)
- **IF AI detected a skin condition**: Start by explaining what the condition is, its characteristics, and general care tips
- Recommend 1-3 specific products when relevant
- Explain WHY each product is suitable
- Mention key ingredients and their benefits
- Include usage tips when appropriate
- For serious conditions, advise medical consultation
- Stay focused on skincare topics only

{custom_instruction}"""

        payload = {
            "model": "llama3.2:latest",
            "prompt": f"{system_context}\n\nUser Question: {user_message}\n\nYour Response:",
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": max_tokens,
                "repeat_penalty": 1.1
            }
        }
        
        logger.info(f"Calling Ollama API for: '{user_message[:50]}...'")
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            logger.info("Successfully received response from Ollama")
            return {
                "success": True,
                "response": result.get("response", "").strip()
            }
        else:
            logger.error(f"Ollama API error: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("Ollama request timeout")
        return None
    except Exception as e:
        logger.error(f"Error calling Ollama: {str(e)}")
        return None


def build_product_context(products: List[Dict], price_limit: Optional[int] = None, 
                         conditions: List[str] = None) -> str:
    """Build rich product context for LLM"""
    if not products:
        return ""
    
    context = "\n=== AVAILABLE PRODUCTS IN OUR STORE ===\n\n"
    
    if price_limit:
        context = f"\n=== PRODUCTS WITHIN BUDGET (≤ Rp {price_limit:,}) ===\n\n"
    
    if conditions:
        context += f"User's Concerns: {', '.join(conditions)}\n\n"
    
    for idx, product in enumerate(products, 1):
        context += f"{idx}. {product['name']} - Rp {product['price']:,}\n"
        context += f"   Category: {product.get('category', 'General')}\n"
        
        if product.get('for_conditions'):
            context += f"   Best For: {', '.join(product['for_conditions'])}\n"
        
        context += f"   Description: {product['description']}\n"
        
        if product.get('ingredients'):
            context += f"   Key Ingredients: {product['ingredients']}\n"
        
        if product.get('usage'):
            context += f"   Usage: {product['usage']}\n"
        
        context += "\n"
    
    return context


def generate_fallback_response(user_message: str, products: List[Dict], 
                               intents: Dict, price_limit: Optional[int]) -> str:
    """Generate intelligent fallback response when Ollama is unavailable"""
    
    if intents.get('medical_info'):
        return (
            "Untuk informasi medis yang akurat mengenai kondisi kulit, saya sangat menyarankan "
            "Anda berkonsultasi langsung dengan dokter kulit (dermatologist). Mereka dapat memberikan "
            "diagnosis yang tepat dan perawatan yang sesuai dengan kondisi Anda. "
            "\n\nJika Anda memerlukan produk perawatan kulit umum, saya dengan senang hati dapat "
            "membantu merekomendasikan produk yang sesuai!"
        )
    
    if not products:
        return (
            "Maaf, saat ini saya tidak menemukan produk yang sesuai dengan kriteria Anda. "
            "Coba jelaskan kebutuhan skincare Anda dengan lebih detail, atau hubungi "
            "customer service kami untuk bantuan lebih lanjut!"
        )
    
    # Build product recommendation response
    response = "Berdasarkan kebutuhan Anda, berikut rekomendasi produk dari kami:\n\n"
    
    for idx, product in enumerate(products[:3], 1):
        response += f"{idx}. **{product['name']}** (Rp {product['price']:,})\n"
        response += f"   {product['description'][:150]}...\n\n"
    
    if price_limit:
        response += f"\nSemua produk di atas sesuai dengan budget Anda (≤ Rp {price_limit:,}). "
    
    response += (
        "\n\nProduk-produk ini dipilih berdasarkan kecocokan dengan kebutuhan skincare Anda. "
        "Untuk hasil terbaik, gunakan secara rutin sesuai petunjuk penggunaan. "
        "Jika ada pertanyaan lebih lanjut, jangan ragu untuk bertanya!"
    )
    
    return response


def generate_response(user_message: str, disease_info: dict = None) -> Dict:
    """
    Generate comprehensive RAG response with advanced intent understanding
    and intelligent product recommendations
    """
    try:
        logger.info(f"Processing RAG request: '{user_message}'")
        
        # Step 1: Classify user intent
        intents = IntentClassifier.classify(user_message)
        logger.info(f"Detected intents: {intents}")
        
        # Step 2: Extract price constraints
        price_limit = PriceExtractor.extract(user_message)
        if price_limit:
            logger.info(f"Extracted price limit: Rp {price_limit:,}")
        
        # Step 3: Extract skin conditions
        conditions = ConditionExtractor.extract(user_message)
        if conditions:
            logger.info(f"Detected conditions: {conditions}")
        
        # Step 4: Determine search strategy
        if intents.get('medical_info') and not intents.get('product_search'):
            # Pure medical info query - no product search needed
            logger.info("Medical info query detected - minimal product search")
            relevant_products = []
        else:
            # Product-related query - perform smart search
            # IMPORTANT: Use ALL products if price filter active to ensure enough cheap options
            top_k = 60 if price_limit else 10  # Search all 60 products when filtering by price
            relevant_products = search_products(user_message, top_k=top_k)
            logger.info(f"Found {len(relevant_products)} initial products")
        
        # Step 5: Apply filters
        if price_limit and relevant_products:
            original_count = len(relevant_products)
            relevant_products = [p for p in relevant_products if p.get('price', 0) <= price_limit]
            # Sort by price (cheapest first) when price filter is active
            relevant_products = sorted(relevant_products, key=lambda x: x.get('price', 0))
            logger.info(f"Price filter: {original_count} -> {len(relevant_products)} products (sorted by price)")
        
        # Filter by conditions if detected
        if conditions and relevant_products:
            filtered = []
            for product in relevant_products:
                product_conditions = [c.lower() for c in product.get('for_conditions', [])]
                if any(cond in ' '.join(product_conditions) for cond in conditions):
                    filtered.append(product)
            
            if filtered:
                relevant_products = filtered
                logger.info(f"Condition filter applied: {len(relevant_products)} matching products")
        
        # Step 6: Build context
        product_context = build_product_context(relevant_products[:10], price_limit, conditions)
        
        # Step 7: Prepare custom instructions
        custom_instruction = ""
        
        # Add disease context if available
        if disease_info and disease_info.get('disease'):
            disease_name = disease_info.get('disease', '')
            confidence = disease_info.get('confidence', 0) * 100
            custom_instruction += (
                f"\n\nCONTEXT: AI detection shows user has '{disease_name}' condition (confidence: {confidence:.1f}%). "
                f"START your response by briefly explaining what this condition is, its common causes, and general skincare tips. "
                f"THEN provide product recommendations suitable for this condition."
            )
        
        if intents.get('medical_info') and not intents.get('product_search'):
            custom_instruction = (
                "\n\nIMPORTANT: User is asking for MEDICAL/EDUCATIONAL information about a skin condition. "
                "Provide clear, informative explanation about the condition. DO NOT recommend products unless "
                "explicitly asked. Always advise consulting a dermatologist for proper diagnosis and treatment."
            )
        elif price_limit:
            custom_instruction = (
                f"\n\nIMPORTANT: User has budget constraint of Rp {price_limit:,}. "
                f"ONLY recommend products within this budget. Clearly mention prices."
            )
        elif intents.get('comparison'):
            custom_instruction = (
                "\n\nIMPORTANT: User wants product comparison. Provide detailed comparison of features, "
                "ingredients, benefits, and value for money. Help them make informed decision."
            )
        elif intents.get('routine'):
            custom_instruction = (
                "\n\nIMPORTANT: User asking about skincare routine. Provide step-by-step guidance "
                "with product order and timing. Explain the purpose of each step."
            )
        
        # Step 8: Call Ollama
        temperature = 0.6 if intents.get('medical_info') else 0.7
        max_tokens = 350 if intents.get('comparison') or intents.get('routine') else 250
        
        ollama_result = call_ollama(
            user_message, 
            product_context, 
            custom_instruction,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Step 9: Prepare response
        if ollama_result and ollama_result.get("success"):
            logger.info("Successfully generated Ollama response")
            
            # Return products based on intent
            if intents.get('medical_info') and not intents.get('product_search'):
                products_to_return = []
            else:
                products_to_return = relevant_products[:3]
            
            return {
                "response": ollama_result["response"],
                "products": products_to_return
            }
        
        # Step 10: Fallback response
        logger.warning("Using fallback response")
        fallback_response = generate_fallback_response(
            user_message, 
            relevant_products, 
            intents, 
            price_limit
        )
        
        return {
            "response": fallback_response,
            "products": relevant_products[:3] if not intents.get('medical_info') else []
        }
        
    except Exception as e:
        logger.error(f"Error in generate_response: {str(e)}", exc_info=True)
        return {
            "response": (
                "Maaf, terjadi kesalahan dalam memproses permintaan Anda. "
                "Silakan coba lagi atau hubungi customer service kami untuk bantuan."
            ),
            "products": []
        }
