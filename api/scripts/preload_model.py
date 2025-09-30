#!/usr/bin/env python3
"""
Model preload script for Healthy Eating Helper API

This script can be used to preload the AI model before starting the main server,
which helps reduce cold start times in production deployments.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def preload_model():
    """Preload the Hugging Face model to reduce cold start times"""
    HF_MODEL_ID = os.getenv("HF_MODEL_ID", "nateraw/food")

    print(f"Preloading model: {HF_MODEL_ID}")
    start_time = time.time()

    try:
        from transformers import pipeline

        # Load the model
        model = pipeline("image-classification", model=HF_MODEL_ID)

        # Test with a dummy image to ensure everything works
        from PIL import Image
        import numpy as np

        # Create a small test image
        test_image = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))

        # Run a test prediction
        predictions = model(test_image)

        load_time = time.time() - start_time
        print(f"✓ Model loaded successfully in {load_time:.2f} seconds")
        print(f"✓ Test prediction completed: {predictions[0]['label']} ({predictions[0]['score']:.3f})")

        return True

    except Exception as e:
        print(f"✗ Failed to preload model: {e}")

        # Try fallback model
        print("Trying fallback model: google/vit-base-patch16-224")
        try:
            fallback_model = pipeline("image-classification", model="google/vit-base-patch16-224")
            test_image = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
            predictions = fallback_model(test_image)

            load_time = time.time() - start_time
            print(f"✓ Fallback model loaded successfully in {load_time:.2f} seconds")
            return True

        except Exception as fallback_error:
            print(f"✗ Fallback model also failed: {fallback_error}")
            return False

if __name__ == "__main__":
    print("🤖 Healthy Eating Helper - Model Preloader")
    print("=" * 50)

    success = preload_model()

    if success:
        print("\n✅ Model preloading completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Model preloading failed!")
        sys.exit(1)