import uvicorn

import os
os.environ.setdefault("KERAS_BACKEND", "tensorflow")
os.environ.setdefault("TRANSFORMERS_KERAS_IMPLEMENTATION", "tf")
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload saat ada perubahan code
        log_level="info"
    )