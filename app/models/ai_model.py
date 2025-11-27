# app/models/ai_model.py
import os
import logging
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from PIL import Image
import io

# Import custom layers BEFORE loading model
from .custom_layers import MBConvBlock

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PyTorchViTWrapper:
    """Wrapper untuk PyTorch ViT model agar compatible dengan Keras-style API"""
    
    def __init__(self, model):
        self.model = model
        self.device = "cuda" if self._has_cuda() else "cpu"
        self.model.to(self.device)
        logger.info(f"  Using device: {self.device}")
    
    def _has_cuda(self):
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def predict(self, image_array, verbose=0):
        """Keras-style predict method"""
        import torch
        from torchvision import transforms
        from PIL import Image
        
        try:
            # Convert numpy array to PIL Image
            if image_array.shape[0] == 1:
                img = Image.fromarray((image_array[0] * 255).astype(np.uint8))
            else:
                img = Image.fromarray((image_array * 255).astype(np.uint8))
            
            # ViT preprocessing
            transform = transforms.Compose([
                transforms.Resize((224, 224)),  # ViT uses 224x224
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
            ])
            
            img_tensor = transform(img).unsqueeze(0).to(self.device)
            
            # Inference
            with torch.no_grad():
                outputs = self.model(img_tensor)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=-1)
            
            # Return numpy array like Keras (batch_size, num_classes)
            result = probs.cpu().numpy()
            logger.info(f" PyTorch prediction successful: shape={result.shape}, max_prob={result.max():.4f}")
            return result
            
        except Exception as e:
            logger.error(f" PyTorch prediction failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Return zeros array to prevent crashes
            return np.zeros((1, self.model.config.num_labels))
    
    @property
    def input_shape(self):
        return (None, 224, 224, 3)  # ViT standard input
    
    @property
    def output_shape(self):
        return (None, self.model.config.num_labels)

class SkinDiseaseModel:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.model_error = None
        self.use_fallback = False
        self.is_huggingface_model = False
        
        # Default class names (8 classes for local model)
        self.idx_to_label = [
            'Acitinic Keratosis', 'Basal Cell Carcinoma', 'Dermatofibroma', 'Nevus', 
            'Pigmented Benign Keratosis', 'Seborrheic Keratosis', 
            'Squamous Cell Carcinoma', 'Vascular Lesion'
        ]
        logger.info(f" Initialized with {len(self.idx_to_label)} labels")

    def _create_enhanced_model(self):
        """Create enhanced CNN model dengan architecture yang lebih baik"""
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, Model
            
            logger.info("🏗️ Creating enhanced CNN model...")
            
            # Enhanced CNN architecture
            inputs = tf.keras.Input(shape=(512, 512, 3))
            
            # Initial convolution block
            x = layers.Conv2D(64, 7, strides=2, padding='same', use_bias=False)(inputs)
            x = layers.BatchNormalization()(x)
            x = layers.Activation('relu')(x)
            x = layers.MaxPooling2D(3, strides=2, padding='same')(x)
            
            # Residual-like blocks
            def conv_block(x, filters, kernel_size=3, strides=1):
                shortcut = x
                
                # Main path
                x = layers.Conv2D(filters, kernel_size, strides=strides, padding='same', use_bias=False)(x)
                x = layers.BatchNormalization()(x)
                x = layers.Activation('relu')(x)
                
                x = layers.Conv2D(filters, kernel_size, padding='same', use_bias=False)(x)
                x = layers.BatchNormalization()(x)
                
                # Shortcut connection
                if strides != 1 or shortcut.shape[-1] != filters:
                    shortcut = layers.Conv2D(filters, 1, strides=strides, use_bias=False)(shortcut)
                    shortcut = layers.BatchNormalization()(shortcut)
                
                x = layers.Add()([x, shortcut])
                x = layers.Activation('relu')(x)
                return x
            
            # Stack of convolutional blocks
            x = conv_block(x, 64, strides=1)
            x = conv_block(x, 64)
            x = conv_block(x, 128, strides=2)
            x = conv_block(x, 128)
            x = conv_block(x, 256, strides=2)
            x = conv_block(x, 256)
            x = conv_block(x, 512, strides=2)
            x = conv_block(x, 512)
            
            # Global features
            x = layers.GlobalAveragePooling2D()(x)
            
            # Classification head dengan lebih banyak capacity
            x = layers.Dense(1024, activation='relu')(x)
            x = layers.Dropout(0.5)(x)
            x = layers.Dense(512, activation='relu')(x)
            x = layers.Dropout(0.3)(x)
            x = layers.Dense(256, activation='relu')(x)
            outputs = layers.Dense(len(self.idx_to_label), activation='softmax')(x)
            
            model = Model(inputs, outputs, name="enhanced_skin_model")
            
            # Compile dengan optimizer yang lebih baik
            model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            logger.info(" Enhanced model created!")
            return model
            
        except Exception as e:
            logger.error(f" Enhanced model failed: {e}")
            return self._create_simple_model()

    def _create_simple_model(self):
        """Create simple fallback model"""
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, Model
            
            logger.info(" Creating simple CNN model...")
            
            inputs = tf.keras.Input(shape=(512, 512, 3))
            
            # Simple CNN
            x = layers.Conv2D(32, 3, activation='relu', padding='same')(inputs)
            x = layers.MaxPooling2D(2)(x)
            x = layers.Conv2D(64, 3, activation='relu', padding='same')(x)
            x = layers.MaxPooling2D(2)(x)
            x = layers.Conv2D(128, 3, activation='relu', padding='same')(x)
            x = layers.GlobalAveragePooling2D()(x)
            x = layers.Dense(256, activation='relu')(x)
            x = layers.Dropout(0.3)(x)
            x = layers.Dense(128, activation='relu')(x)
            outputs = layers.Dense(len(self.idx_to_label), activation='softmax')(x)
            
            model = Model(inputs, outputs, name="simple_skin_model")
            model.compile(optimizer='adam', loss='categorical_crossentropy')
            
            logger.info(" Simple model created!")
            return model
            
        except Exception as e:
            logger.error(f" Simple model failed: {e}")
            return None

    def _load_saved_model(self):
        """Try to load model - checks multiple formats"""
        weights_dir = Path(__file__).parent / "weights"
        
        # Priority 1: Load from Hugging Face Hub - PyTorch ViT Model (0xnu/skincare-detection)
        try:
            logger.info(" Trying to load PyTorch ViT model from Hugging Face Hub...")
            
            import torch
            from transformers import ViTForImageClassification
            
            # Load pre-trained Vision Transformer
            model = ViTForImageClassification.from_pretrained(
                '0xnu/skincare-detection',
                trust_remote_code=True
            )
            model.eval()  # Set to evaluation mode
            
            logger.info(" PyTorch ViT model loaded from Hugging Face Hub!")
            logger.info(f" Model: Vision Transformer (ViT)")
            logger.info(f"  Classes: {model.config.num_labels}")
            
            # Mark as HuggingFace model and update labels if id2label exists
            self.is_huggingface_model = True
            if hasattr(model.config, 'id2label') and model.config.id2label:
                # Use labels from HuggingFace config
                self.idx_to_label = [model.config.id2label[i] for i in range(model.config.num_labels)]
                logger.info(f" Using {len(self.idx_to_label)} labels from HuggingFace config")
            else:
                # Generate generic labels
                self.idx_to_label = [f"Skin Condition {i+1}" for i in range(model.config.num_labels)]
                logger.info(f" Generated {len(self.idx_to_label)} generic labels")
            
            # Wrap model in PyTorchWrapper
            return PyTorchViTWrapper(model)
            
        except Exception as e:
            logger.warning(f"  HF Hub PyTorch loading failed: {str(e)[:200]}")
        
        # Priority 2: Try local .h5 file (most compatible)
        h5_path = weights_dir / "skin_model.h5"
        if h5_path.exists():
            logger.info(f"📦 Found .h5 file ({h5_path.stat().st_size / (1024**3):.2f} GB)")
            model = self._load_h5_model(h5_path)
            if model is not None:
                return model
        
        # Priority 3: Try .keras file
        keras_path = weights_dir / "skin_model.keras"
        if keras_path.exists():
            logger.info(f"📦 Found .keras file ({keras_path.stat().st_size / (1024**3):.2f} GB)")
            model = self._load_keras_model(keras_path)
            if model is not None:
                return model
        
        # Priority 4: Try SavedModel directory
        saved_model_path = weights_dir / "skin_model_saved"
        if saved_model_path.exists() and saved_model_path.is_dir():
            logger.info(f"📦 Found SavedModel directory")
            model = self._load_saved_model_format(saved_model_path)
            if model is not None:
                return model
        
        logger.error(" No model found in any format")
        return None
    
    def _load_h5_model(self, model_path):
        """Load model dari .h5 file (PALING STABLE)"""
        try:
            import tensorflow as tf
            
            logger.info("🔧 Loading .h5 model with TensorFlow...")
            
            # Try with tf.keras (legacy)
            try:
                os.environ["TF_USE_LEGACY_KERAS"] = "1"
                model = tf.keras.models.load_model(str(model_path), compile=False)
                logger.info(" Model loaded with TF Keras (legacy)!")
            except Exception as e1:
                logger.warning(f"Legacy Keras failed: {str(e1)[:100]}")
                
                # Try with Keras 3
                os.environ["TF_USE_LEGACY_KERAS"] = "0"
                import keras
                model = keras.models.load_model(str(model_path), compile=False)
                logger.info(" Model loaded with Keras 3!")
            
            # Compile
            model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            logger.info(f" Input shape: {model.input_shape}")
            logger.info(f"📊 Output shape: {model.output_shape}")
            return model
            
        except Exception as e:
            logger.error(f" Failed to load .h5 model: {e}")
            return None
    
    def _load_keras_model(self, model_path):
        """Load model dari .keras file (Keras 3 format)"""
        try:
            import keras
            from .custom_layers import MBConvBlock
            
            logger.info(f"🔧 Loading .keras model with Keras {keras.__version__}...")
            
            # Try with custom_objects
            try:
                model = keras.models.load_model(
                    str(model_path),
                    custom_objects={'MBConvBlock': MBConvBlock},
                    compile=False
                )
                logger.info(" Model loaded with custom layers!")
            except Exception as e1:
                logger.warning(f"Custom layers failed: {str(e1)[:100]}")
                # Try without custom objects
                model = keras.models.load_model(str(model_path), compile=False)
                logger.info(" Model loaded!")
            
            model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            logger.info(f" Input shape: {model.input_shape}")
            logger.info(f"📊 Output shape: {model.output_shape}")
            return model
            
        except Exception as e:
            logger.error(f" Failed to load .keras model: {e}")
            return None
    
    def _load_saved_model_format(self, model_path):
        """Load model dari SavedModel format (TensorFlow native)"""
        try:
            import tensorflow as tf
            
            logger.info("🔧 Loading SavedModel format...")
            model = tf.keras.models.load_model(str(model_path))
            logger.info(" SavedModel loaded!")
            
            logger.info(f" Input shape: {model.input_shape}")
            logger.info(f"📊 Output shape: {model.output_shape}")
            return model
            
        except Exception as e:
            logger.error(f" Failed to load SavedModel: {e}")
            return None
    
    def _ensure_loaded(self):
        """Ensure model is loaded - try trained model first, use fallback if needed"""
        if self.model_loaded:
            return
        
        # Try to load saved model
        logger.info(" Loading trained model...")
        self.model = self._load_saved_model()
        
        if self.model is not None:
            self.model_loaded = True
            self.use_fallback = False
            logger.info(" Using TRAINED model for predictions!")
            return
        
        # NO FALLBACK - User explicitly wants trained model only
        logger.error("="*80)
        logger.error(" TRAINED MODEL LOADING FAILED!")
        logger.error("="*80)
        logger.error("  No trained model file found or failed to load")
        logger.error("")
        logger.error(" SOLUTION: Convert your trained model to .h5 format")
        logger.error("")
        logger.error("   OPTION 1 - From Colab/Kaggle (RECOMMENDED):")
        logger.error("   ```python")
        logger.error("   # Load your trained model")
        logger.error("   model = keras.models.load_model('skin_model.keras')")
        logger.error("")
        logger.error("   # Save as .h5")
        logger.error("   model.save('skin_model.h5', save_format='h5')")
        logger.error("")
        logger.error("   # Download and copy to:")
        logger.error("   # backend/app/models/weights/skin_model.h5")
        logger.error("   ```")
        logger.error("")
        logger.error("   OPTION 2 - Use converter script:")
        logger.error("   python backend/convert_keras_to_h5.py")
        logger.error("")
        logger.error(" APPLICATION CANNOT START WITHOUT TRAINED MODEL")
        logger.error("="*80)
        
        raise RuntimeError("No trained model available. Convert model to .h5 format first.")

    def _preprocess(self, image_bytes: bytes, target_size=(512, 512)) -> np.ndarray:
        """Preprocess image"""
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img = img.resize(target_size, Image.Resampling.BILINEAR)
            img_array = np.array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = img_array.astype(np.float32) / 255.0
            return img_array
        except Exception as e:
            raise ValueError(f"Image preprocessing failed: {e}")

    def predict_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """Predict skin disease from image bytes"""
        self._ensure_loaded()
        
        try:
            processed_image = self._preprocess(image_bytes)
            predictions = self.model.predict(processed_image, verbose=0)
            
            predicted_class_index = np.argmax(predictions, axis=1)[0]
            predicted_class_name = self.idx_to_label[predicted_class_index]
            confidence = float(np.max(predictions, axis=1)[0])
            
            # Get top 3 predictions
            topk = min(3, len(predictions[0]))
            top_indices = np.argsort(-predictions[0])[:topk]
            
            topk_results = []
            for idx in top_indices:
                topk_results.append({
                    "index": int(idx),
                    "label": self.idx_to_label[idx],
                    "score": float(predictions[0][idx])
                })
            
            model_status = "enhanced_fallback" if self.use_fallback else "saved_model"
            note = self.model_error if self.use_fallback else "Using trained model"
            
            result = {
                "topk": topk_results,
                "best": {
                    "index": int(predicted_class_index),
                    "label": predicted_class_name, 
                    "score": confidence
                },
                "model_status": model_status,
                "note": note
            }
            
            logger.info(f" Predicted: {predicted_class_name} ({confidence:.2%})")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                "topk": [],
                "best": {"index": -1, "label": "Error", "score": 0.0},
                "model_status": f"Error: {str(e)}",
                "error": str(e)
            }

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        self._ensure_loaded()
        model_type = "enhanced_fallback" if self.use_fallback else "saved_model"
        note = self.model_error if self.use_fallback else "Using trained Keras model"
        
        return {
            "loaded": self.model_loaded,
            "model_type": model_type,
            "use_fallback": self.use_fallback,
            "error": self.model_error,
            "input_shape": str(self.model.input_shape) if self.model and hasattr(self.model, 'input_shape') else None,
            "output_shape": str(self.model.output_shape) if self.model and hasattr(self.model, 'output_shape') else None,
            "labels": self.idx_to_label,
            "note": note
        }

# Global instance
skin_model = SkinDiseaseModel()