# app/database/vector_db.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

# ==== [OPSI: pakai static PRODUCTS lebih dulu] =========================
def _load_products_from_static():
    """
    Load dari app/database/products_data.py -> PRODUCTS (list of dict)
    Return: list of dict dengan field seragam
    """
    try:
        from .products_data import PRODUCTS as STATIC_PRODUCTS, SKINCARE_KNOWLEDGE
        if not STATIC_PRODUCTS:
            return []

        normalized = []
        for p in STATIC_PRODUCTS:
            # Enhance description with ingredients and usage for better RAG
            full_description = p.get("description", "")
            if p.get("ingredients"):
                full_description += f" Ingredients: {p['ingredients']}."
            if p.get("usage"):
                full_description += f" Usage: {p['usage']}"
            
            normalized.append({
                "id": p.get("id"),
                "name": p.get("name", "") or "",
                "description": full_description or "",
                "price": p.get("price", 0) or 0,
                "category": p.get("category", "") or "",
                "image_url": p.get("image_url", "") or "",
                "for_conditions": p.get("for_conditions", []) or [],
                "ingredients": p.get("ingredients", "") or "",
                "usage": p.get("usage", "") or "",
            })
        return normalized
    except Exception as e:
        logger.warning(f"Static products import failed: {e}")
        return []

def _load_products_from_db():
    """
    Fallback: ambil dari DB (schema: id, name, description, price, category, image_url)
    """
    try:
        from .connection import get_db
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, description, price, category, image_url FROM products")
        rows = cursor.fetchall()

        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "name": r[1] or "",
                "description": r[2] or "",
                "price": r[3] or 0,
                "category": r[4] or "",
                "image_url": r[5] or "",
                "for_conditions": [],  # kolom ini biasanya gak ada di DB
            })
        return result
    except Exception as e:
        logger.error(f"DB fetch failed: {e}")
        return []
    finally:
        try:
            db.close()
        except Exception:
            pass

def _fetch_all_products():
    """
    Prefer static list; fallback DB kalau static kosong/gagal.
    """
    static_products = _load_products_from_static()
    if static_products:
        logger.info(f"Loaded {len(static_products)} products from static PRODUCTS")
        return static_products

    db_products = _load_products_from_db()
    logger.info(f"Loaded {len(db_products)} products from DB")
    return db_products

# ==== [Embedding sederhana] ============================================
def get_text_embedding(text: str) -> np.ndarray:
    """
    Simple text embedding menggunakan approach sederhana (karakter + keyword boost).
    """
    if not text:
        return np.zeros(100, dtype=float)

    text = text.lower().strip()

    # char-frequency-ish features (first 100 chars)
    embedding = np.zeros(100, dtype=float)
    for i, char in enumerate(text[:100]):
        embedding[i % 100] += ord(char) / 1000.0

    # keyword boosts
    skincare_keywords = {
        'kulit': 1.0, 'skin': 1.0, 'jerawat': 0.9, 'acne': 0.9, 
        'kering': 0.8, 'dry': 0.8, 'berminyak': 0.8, 'oily': 0.8,
        'sensitif': 0.7, 'sensitive': 0.7, 'pori': 0.6, 'pore': 0.6,
        'bekas': 0.5, 'scar': 0.5, 'merah': 0.5, 'redness': 0.5,
        'gatal': 0.4, 'itchy': 0.4, 'face': 0.3
    }
    keys = list(skincare_keywords.keys())
    for word, weight in skincare_keywords.items():
        if word in text:
            idx = len(embedding) - 1 - (keys.index(word) % 10)
            embedding[idx] += weight

    # normalize
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    return embedding

# ==== [Search] =========================================================
def search_products(query: str, top_k: int = 3):
    """
    Search products berdasarkan cosine similarity antara embedding query vs product text.
    Sumber data: static PRODUCTS (prefer) → fallback ke DB.
    """
    try:
        products = _fetch_all_products()
        if not products:
            logger.info("No products available to search.")
            return []

        # query embedding
        query_embedding = get_text_embedding(query or "")

        # hitung similarity
        scored = []
        for p in products:
            # representasi teks produk (pakai fields yang ada)
            cond_text = " ".join(p.get("for_conditions", [])) if p.get("for_conditions") else ""
            product_text = f"{p.get('name','')} {p.get('description','')} {p.get('category','')} {cond_text}"
            prod_emb = get_text_embedding(product_text)
            sim = float(cosine_similarity([query_embedding], [prod_emb])[0][0])
            scored.append((p, sim))

        # urutkan & ambil top_k
        scored.sort(key=lambda x: x[1], reverse=True)
        top_results = [prod for prod, _ in scored[:top_k]]

        logger.info(f"Search found {len(top_results)} products for query: '{query}'")
        return top_results

    except Exception as e:
        logger.error(f"Search error: {e}")
        return []
