# Skincare Chatbot Backend API

Backend API for skincare e-commerce platform with AI chatbot, disease detection, and personalized product recommendations using Multi-Armed Bandit (Thompson Sampling).

## Frontend

```
https://skincare.farhanage.site
```

## Base URL

```
Production: https://skincare-api.farhanage.site
Development: http://localhost:8000
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

---

## 📋 API Endpoints

### 🔐 Authentication

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=password123
```

**Response:**
```json
{
  "success": true,
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

---

### 🛍️ Products

#### Get All Products
```http
GET /api/products?category=serum&search=acne
Authorization: Bearer <token>
```

#### Get Product by ID
```http
GET /api/products/{product_id}
Authorization: Bearer <token>
```

#### Get Product Recommendations (Bandit)
```http
GET /api/bandit/recommend?n_recommendations=5&category=serum&exclude_product_ids=1&exclude_product_ids=2
Authorization: Bearer <token>
```

Optional JSON-style query example:
```http
GET /api/bandit/recommend?n_recommendations=5&category=serum&exclude_product_ids=1,2,3
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "algorithm": "Thompson Sampling",
  "recommendations": [
    {
      "id": 10,
      "name": "Product Name",
      "price": 150000,
      "thompson_sample": 0.85,
      "bandit_stats": {
        "impressions": 100,
        "expected_reward": 0.836
      }
    }
  ]
}
```

#### Get Similar Products
```http
GET /api/products/recommend/{product_id}?top_k=5
Authorization: Bearer <token>
```

---

### 🛒 Cart & Orders

#### Get Cart
```http
GET /api/products/cart
Authorization: Bearer <token>
```

#### Add to Cart
```http
POST /api/products/cart
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": "1",
  "quantity": 2
}
```

#### Update Cart Item
```http
PUT /api/products/cart
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": "1",
  "quantity": 3
}
```

#### Checkout (Create Order)
```http
POST /api/orders/checkout
Authorization: Bearer <token>
```

#### Get User Orders
```http
GET /api/orders
Authorization: Bearer <token>
```

---

### 🤖 AI Chat

#### Get User Chats
```http
GET /api/users/{user_id}/chats
Authorization: Bearer <token>
```

#### Create New Chat
```http
POST /api/users/{user_id}/chats
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Konsultasi Jerawat"
}
```

#### Get Chat Messages
```http
GET /api/chats/{chat_id}/messages?limit=50&order=asc
Authorization: Bearer <token>
```

#### Send Message (AI Response)
```http
POST /api/chats/{chat_id}/messages
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Saya punya masalah jerawat",
  "disease_context": {
    "disease": "Acne",
    "confidence": 0.95
  }
}
```

**Response:**
```json
{
  "user_message": {
    "id": "msg_123",
    "text": "Saya punya masalah jerawat",
    "is_bot": false,
    "timestamp": "2025-12-05T10:00:00Z"
  },
  "bot_message": {
    "id": "msg_124",
    "text": "Untuk mengatasi jerawat...",
    "is_bot": true,
    "timestamp": "2025-12-05T10:00:05Z",
    "products": [
      {
        "id": 1,
        "name": "Acne Serum",
        "reason": "Mengandung salicylic acid"
      }
    ]
  }
}
```

#### Delete Chat
```http
DELETE /api/chats/{chat_id}
Authorization: Bearer <token>
```

---

### 🔬 Disease Detection

#### Predict Skin Disease
```http
POST /api/predict
Content-Type: multipart/form-data

file: <image_file>
```

**Note:** No authentication required

**Response:**
```json
{
  "success": true,
  "prediction": {
    "topk": [
      {
        "label": "Acne",
        "score": 0.95,
        "index": 0
      }
    ],
    "best": {
      "label": "Acne",
      "score": 0.95
    }
  }
}
```

---

### 📊 User Interactions & Bandit

#### Track Interaction
```http
POST /api/interactions/track
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": 10,
  "action": "click",
  "reward": 1.0
}
```

**Actions & Rewards:**
- `click`: 1.0
- `add_to_cart`: 2.0

**Note:** This automatically updates the bandit state

#### Get User Interaction History
```http
GET /api/interactions/user?limit=50&offset=0
Authorization: Bearer <token>
```

#### Update Bandit State
```http
POST /api/bandit/update
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": 10,
  "reward": 2.0,
  "impression_count": 1
}
```

#### Get Bandit Statistics
```http
GET /api/bandit/statistics
Authorization: Bearer <token>
```

---

## 🚀 Quick Start

### JavaScript Example

```javascript
// Login
const login = async (username, password) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username, password })
  });
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  return data;
};

// Get Bandit Recommendations
const getRecommendations = async (n = 5, category = null, excludeProductIds = []) => {
  const token = localStorage.getItem('token');
  const params = new URLSearchParams({ n_recommendations: n });
  if (category) params.append('category', category);
  if (excludeProductIds && excludeProductIds.length > 0) {
    excludeProductIds.forEach(id => params.append('exclude_product_ids', id));
  }
  const response = await fetch(`/api/bandit/recommend?${params.toString()}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.json();
};

// Track Interaction
const trackInteraction = async (productId, action) => {
  const token = localStorage.getItem('token');
  const response = await fetch('/api/interactions/track', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ product_id: productId, action })
  });
  return response.json();
};

// Send Chat Message
const sendMessage = async (chatId, message, diseaseInfo = {}) => {
  const token = localStorage.getItem('token');
  const response = await fetch(`/api/chats/${chatId}/messages`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text: message,
      disease_context: diseaseInfo
    })
  });
  return response.json();
};

// Upload Image for Disease Detection
const detectDisease = async (imageFile) => {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch('/api/predict', {
    method: 'POST',
    body: formData
  });
  return response.json();
};
```

---

## 🎯 Recommended Workflow

1. **User Registration/Login** → Get JWT token
2. **Disease Detection** → Upload skin image, get diagnosis
3. **Get Recommendations** → Use bandit endpoint with disease context
4. **Track Interactions** → Track clicks/cart additions (auto-updates bandit)
5. **Chat Consultation** → Create chat, send messages with disease context
6. **Purchase Flow** → Add to cart, checkout

---

## 🔧 Environment Variables

Required in `.env`:

```env
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
CORS_ALLOWED_ORIGINS=https://your-frontend.com
LLM_INFERENCE_API=https://your-llm-api.com
DISEASE_DETECTION_API=https://your-vit-api.com
```

---

## 📚 Error Responses

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

**Common Status Codes:**
- `200` - Success
- `401` - Unauthorized (invalid/expired token)
- `403` - Forbidden (no access)
- `404` - Not Found
- `500` - Internal Server Error

---

## 📖 Features

- ✅ JWT Authentication
- ✅ Product catalog & search
- ✅ Shopping cart & orders
- ✅ AI chatbot with product recommendations
- ✅ Skin disease detection (Vision Transformer)
- ✅ Multi-Armed Bandit recommendations (Thompson Sampling)
- ✅ User interaction tracking
- ✅ Personalized product suggestions

---

## 🤝 Support

For issues or questions, contact the backend team or open an issue.

**API Version:** 1.0.0  
**Last Updated:** December 5, 2025
