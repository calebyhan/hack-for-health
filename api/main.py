"""
Healthy Eating Helper API
FastAPI backend for food image analysis and nutrition estimation
"""
import os
import time
import io
from typing import List, Dict, Any, Optional
import logging

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Healthy Eating Helper API",
    description="Food image analysis and nutrition estimation service",
    version="1.0.0"
)

# CORS middleware
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "nateraw/food")

# Global model variable for lazy loading
model = None

# Expanded synonym mapping for food labels - improves accuracy
LABELS_MAP = {
    # Fries variations
    "fries": "french fries",
    "chips": "french fries",
    "potato fries": "french fries",
    "fried potatoes": "french fries",

    # Soda variations
    "cola": "soda",
    "coke": "soda",
    "pepsi": "soda",
    "soft drink": "soda",
    "carbonated drink": "soda",

    # Burger variations
    "hamburger": "burger",
    "cheeseburger": "burger",
    "beefburger": "burger",

    # Salad variations
    "salad greens": "salad",
    "green salad": "salad",
    "mixed salad": "salad",
    "garden salad": "salad",
    "tossed salad": "salad",

    # Rice variations
    "white rice": "rice",
    "steamed rice": "rice",
    "fried rice": "rice",
    "rice bowl": "rice",

    # Chicken variations
    "grilled chicken": "chicken breast",
    "chicken breast": "chicken breast",
    "chicken fillet": "chicken breast",
    "roasted chicken": "chicken breast",

    # Pizza variations
    "pizza slice": "pizza",
    "cheese pizza": "pizza",
    "pepperoni pizza": "pizza",

    # Sandwich variations
    "sub": "sandwich",
    "hoagie": "sandwich",
    "panini": "sandwich",

    # Pasta variations
    "spaghetti": "pasta",
    "noodles": "pasta",
    "linguine": "pasta",
    "penne": "pasta",

    # Fruit variations
    "apples": "apple",
    "bananas": "banana",
    "oranges": "orange",

    # Beverage variations
    "coffee cup": "coffee",
    "espresso": "coffee",
    "latte": "coffee"
}

# Caution foods that get health score penalties
CAUTION_FOODS = {
    "soda": 10,
    "french fries": 8,
    "burger": 5,
    "pizza": 3,
    "dessert": 7
}

def load_model():
    """
    Lazy load the AI model to avoid cold start delays
    Uses food-specific model with optimized settings for accuracy
    """
    global model
    if model is None:
        try:
            logger.info(f"Loading model: {HF_MODEL_ID}")
            from transformers import pipeline

            # Load with optimized settings for food classification
            model = pipeline(
                "image-classification",
                model=HF_MODEL_ID,
                top_k=10  # Get top 10 predictions for better multi-label detection
            )
            logger.info("Model loaded successfully with optimized settings")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Fallback to a general model
            try:
                logger.info("Trying fallback model: google/vit-base-patch16-224")
                model = pipeline(
                    "image-classification",
                    model="google/vit-base-patch16-224",
                    top_k=10
                )
                logger.info("Fallback model loaded")
            except Exception as fallback_error:
                logger.error(f"Fallback model failed: {fallback_error}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to load AI model"
                )
    return model

def preprocess_image_adaptive(img: Image.Image) -> tuple[Image.Image, dict]:
    """
    ADAPTIVE STRATEGY: Quality-aware preprocessing with dynamic enhancement.
    Best for: General use, mixed quality images.

    Features:
    - EXIF rotation handling
    - Adaptive lighting normalization based on brightness
    - Quality-based contrast/sharpness adjustment
    - Balanced approach for most scenarios

    Returns: (processed_image, quality_metrics)
    """
    from PIL import ImageEnhance, ImageStat, ImageOps

    quality_metrics = {'strategy': 'adaptive'}

    # 1. Handle EXIF orientation
    try:
        img = ImageOps.exif_transpose(img)
        quality_metrics['exif_corrected'] = True
    except Exception:
        quality_metrics['exif_corrected'] = False

    # Ensure RGB mode
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # 2. Assess image quality
    stat = ImageStat.Stat(img)
    mean_brightness = sum(stat.mean) / 3
    std_dev = sum(stat.stddev) / 3

    brightness_quality = 1.0 - min(abs(mean_brightness - 130) / 130, 1.0)
    variance_quality = min(std_dev / 50, 1.0)
    quality_score = (brightness_quality + variance_quality) / 2

    quality_metrics['brightness'] = mean_brightness
    quality_metrics['variance'] = std_dev
    quality_metrics['quality_score'] = quality_score

    # 3. Adaptive lighting normalization
    if mean_brightness < 80:
        brightness_factor = 1.3
        quality_metrics['lighting_adjusted'] = 'brightened'
    elif mean_brightness > 180:
        brightness_factor = 0.8
        quality_metrics['lighting_adjusted'] = 'darkened'
    else:
        brightness_factor = 1.0
        quality_metrics['lighting_adjusted'] = 'none'

    if brightness_factor != 1.0:
        brightener = ImageEnhance.Brightness(img)
        img = brightener.enhance(brightness_factor)

    # 4. Resize
    target_size = (224, 224)
    img.thumbnail((target_size[0] * 2, target_size[1] * 2), Image.Resampling.LANCZOS)
    new_img = Image.new('RGB', target_size, (255, 255, 255))
    paste_x = (target_size[0] - img.size[0]) // 2
    paste_y = (target_size[1] - img.size[1]) // 2
    new_img.paste(img, (paste_x, paste_y))

    # 5. Adaptive contrast enhancement
    contrast_factor = 1.1 + (0.2 * (1 - quality_score))
    enhancer = ImageEnhance.Contrast(new_img)
    enhanced_img = enhancer.enhance(contrast_factor)
    quality_metrics['contrast_factor'] = contrast_factor

    # 6. Adaptive sharpness enhancement
    sharpness_factor = 1.1 + (0.15 * (1 - quality_score))
    sharpener = ImageEnhance.Sharpness(enhanced_img)
    final_img = sharpener.enhance(sharpness_factor)
    quality_metrics['sharpness_factor'] = sharpness_factor

    return final_img, quality_metrics


def preprocess_image_aggressive(img: Image.Image) -> tuple[Image.Image, dict]:
    """
    AGGRESSIVE STRATEGY: Strong enhancement for difficult images.
    Best for: Low-quality images, poor lighting, blurry photos.

    Features:
    - Strong contrast boost (1.4x)
    - High sharpness enhancement (1.3x)
    - Aggressive brightness correction
    - Color saturation boost

    Returns: (processed_image, quality_metrics)
    """
    from PIL import ImageEnhance, ImageStat, ImageOps

    quality_metrics = {'strategy': 'aggressive'}

    # Handle EXIF
    try:
        img = ImageOps.exif_transpose(img)
        quality_metrics['exif_corrected'] = True
    except Exception:
        quality_metrics['exif_corrected'] = False

    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Assess quality
    stat = ImageStat.Stat(img)
    mean_brightness = sum(stat.mean) / 3
    std_dev = sum(stat.stddev) / 3

    # Calculate quality score (same as adaptive)
    brightness_quality = 1.0 - min(abs(mean_brightness - 130) / 130, 1.0)
    variance_quality = min(std_dev / 50, 1.0)
    quality_score = (brightness_quality + variance_quality) / 2

    quality_metrics['brightness'] = mean_brightness
    quality_metrics['variance'] = std_dev
    quality_metrics['quality_score'] = quality_score

    # Aggressive lighting correction
    if mean_brightness < 100:
        brightness_factor = 1.5
    elif mean_brightness > 160:
        brightness_factor = 0.7
    else:
        brightness_factor = 1.1

    quality_metrics['brightness_factor'] = brightness_factor
    brightener = ImageEnhance.Brightness(img)
    img = brightener.enhance(brightness_factor)

    # Resize
    target_size = (224, 224)
    img.thumbnail((target_size[0] * 2, target_size[1] * 2), Image.Resampling.LANCZOS)
    new_img = Image.new('RGB', target_size, (255, 255, 255))
    paste_x = (target_size[0] - img.size[0]) // 2
    paste_y = (target_size[1] - img.size[1]) // 2
    new_img.paste(img, (paste_x, paste_y))

    # Aggressive enhancements
    # Contrast
    contrast_factor = 1.4
    enhancer = ImageEnhance.Contrast(new_img)
    enhanced_img = enhancer.enhance(contrast_factor)
    quality_metrics['contrast_factor'] = contrast_factor

    # Sharpness
    sharpness_factor = 1.3
    sharpener = ImageEnhance.Sharpness(enhanced_img)
    sharpened_img = sharpener.enhance(sharpness_factor)
    quality_metrics['sharpness_factor'] = sharpness_factor

    # Color saturation boost
    color_factor = 1.2
    color_enhancer = ImageEnhance.Color(sharpened_img)
    final_img = color_enhancer.enhance(color_factor)
    quality_metrics['color_factor'] = color_factor

    return final_img, quality_metrics


def preprocess_image_minimal(img: Image.Image) -> tuple[Image.Image, dict]:
    """
    MINIMAL STRATEGY: Light preprocessing for high-quality images.
    Best for: Professional photos, good lighting, clear images.

    Features:
    - EXIF rotation only
    - Minimal contrast (1.05x)
    - Minimal sharpness (1.05x)
    - Preserves original image characteristics

    Returns: (processed_image, quality_metrics)
    """
    from PIL import ImageEnhance, ImageStat, ImageOps

    quality_metrics = {'strategy': 'minimal'}

    # Handle EXIF
    try:
        img = ImageOps.exif_transpose(img)
        quality_metrics['exif_corrected'] = True
    except Exception:
        quality_metrics['exif_corrected'] = False

    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Basic quality metrics
    stat = ImageStat.Stat(img)
    mean_brightness = sum(stat.mean) / 3
    std_dev = sum(stat.stddev) / 3

    # Calculate quality score (same as adaptive)
    brightness_quality = 1.0 - min(abs(mean_brightness - 130) / 130, 1.0)
    variance_quality = min(std_dev / 50, 1.0)
    quality_score = (brightness_quality + variance_quality) / 2

    quality_metrics['brightness'] = mean_brightness
    quality_metrics['variance'] = std_dev
    quality_metrics['quality_score'] = quality_score

    # Resize
    target_size = (224, 224)
    img.thumbnail((target_size[0] * 2, target_size[1] * 2), Image.Resampling.LANCZOS)
    new_img = Image.new('RGB', target_size, (255, 255, 255))
    paste_x = (target_size[0] - img.size[0]) // 2
    paste_y = (target_size[1] - img.size[1]) // 2
    new_img.paste(img, (paste_x, paste_y))

    # Minimal enhancements
    contrast_factor = 1.05
    enhancer = ImageEnhance.Contrast(new_img)
    enhanced_img = enhancer.enhance(contrast_factor)
    quality_metrics['contrast_factor'] = contrast_factor

    sharpness_factor = 1.05
    sharpener = ImageEnhance.Sharpness(enhanced_img)
    final_img = sharpener.enhance(sharpness_factor)
    quality_metrics['sharpness_factor'] = sharpness_factor

    return final_img, quality_metrics


# Strategy selector with A/B testing support
PREPROCESSING_STRATEGIES = {
    'adaptive': preprocess_image_adaptive,
    'aggressive': preprocess_image_aggressive,
    'minimal': preprocess_image_minimal
}


def select_preprocessing_strategy(quality_score: float = None, user_preference: str = None) -> str:
    """
    Select preprocessing strategy based on image quality or user preference.

    For A/B testing: randomly select strategy if no preference provided.
    For production: use quality-based selection.

    Args:
        quality_score: Image quality score (0-1), if available
        user_preference: User's preferred strategy name

    Returns:
        Strategy name ('adaptive', 'aggressive', or 'minimal')
    """
    import random

    # User preference takes priority
    if user_preference and user_preference in PREPROCESSING_STRATEGIES:
        return user_preference

    # A/B testing mode: random selection (enable via env var)
    if os.getenv("ENABLE_AB_TESTING", "false").lower() == "true":
        strategy = random.choice(list(PREPROCESSING_STRATEGIES.keys()))
        logger.info(f"A/B Testing: Selected random strategy '{strategy}'")
        return strategy

    # Quality-based selection (default)
    if quality_score is None:
        return 'adaptive'  # Default fallback

    if quality_score >= 0.7:
        return 'minimal'  # High quality images
    elif quality_score >= 0.4:
        return 'adaptive'  # Medium quality images
    else:
        return 'aggressive'  # Low quality images


def preprocess_image(img: Image.Image, strategy: str = None) -> tuple[Image.Image, dict]:
    """
    Main preprocessing entry point with strategy selection.

    Args:
        img: Input PIL Image
        strategy: Optional strategy override ('adaptive', 'aggressive', 'minimal')

    Returns:
        (processed_image, quality_metrics)
    """
    from PIL import ImageStat

    # Quick quality assessment for strategy selection
    if strategy is None:
        stat = ImageStat.Stat(img.convert('RGB'))
        mean_brightness = sum(stat.mean) / 3
        std_dev = sum(stat.stddev) / 3
        brightness_quality = 1.0 - min(abs(mean_brightness - 130) / 130, 1.0)
        variance_quality = min(std_dev / 50, 1.0)
        quality_score = (brightness_quality + variance_quality) / 2
        strategy = select_preprocessing_strategy(quality_score)

    logger.info(f"Using preprocessing strategy: {strategy}")

    preprocess_func = PREPROCESSING_STRATEGIES.get(strategy, preprocess_image_adaptive)
    return preprocess_func(img)

def normalize_label(label: str) -> str:
    """Normalize food labels using synonym mapping"""
    cleaned = label.lower().strip()
    return LABELS_MAP.get(cleaned, cleaned)

async def get_supabase_client():
    """Get Supabase client for database operations"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("Supabase not configured - using in-memory nutrition data")
        return None

    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        return supabase
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        return None

async def lookup_nutrition(name: str, cuisine_type: str = None) -> Dict[str, float]:
    """
    Lookup nutritional information for a food item with regional cuisine support.

    Args:
        name: Food label from model
        cuisine_type: Optional cuisine type (e.g., 'italian', 'chinese', 'mexican')

    Returns:
        Dictionary with nutritional information
    """
    canonical = normalize_label(name)

    # Try to get from Supabase first
    supabase = await get_supabase_client()
    if supabase:
        try:
            # If cuisine type is provided, check regional mappings first
            if cuisine_type:
                regional_result = supabase.table('regional_cuisine_mappings').select('*').eq('cuisine_type', cuisine_type).eq('model_label', name.lower()).execute()
                if regional_result.data:
                    canonical = regional_result.data[0].get('canonical_name', canonical)
                    logger.info(f"Mapped '{name}' to '{canonical}' via {cuisine_type} cuisine")

            result = supabase.table('nutrition_facts').select('*').eq('canonical_name', canonical).execute()
            if result.data:
                nutrition = result.data[0]
                return {
                    "calories": nutrition.get("calories", 0),
                    "protein_g": float(nutrition.get("protein_g", 0)),
                    "carbs_g": float(nutrition.get("carbs_g", 0)),
                    "fat_g": float(nutrition.get("fat_g", 0)),
                    "fiber_g": float(nutrition.get("fiber_g", 0)),
                    "sat_fat_g": float(nutrition.get("sat_fat_g", 0)),
                    "added_sugar_g": float(nutrition.get("added_sugar_g", 0))
                }
        except Exception as e:
            logger.error(f"Database lookup failed for {canonical}: {e}")

    # Fallback to hardcoded nutrition table
    nutrition_table = {
        "pizza": {"calories": 285, "protein_g": 12, "carbs_g": 36, "fat_g": 10, "fiber_g": 2, "sat_fat_g": 4, "added_sugar_g": 2},
        "salad": {"calories": 150, "protein_g": 4, "carbs_g": 10, "fat_g": 10, "fiber_g": 3, "sat_fat_g": 2, "added_sugar_g": 1},
        "soda": {"calories": 150, "protein_g": 0, "carbs_g": 39, "fat_g": 0, "fiber_g": 0, "sat_fat_g": 0, "added_sugar_g": 39},
        "french fries": {"calories": 365, "protein_g": 4, "carbs_g": 48, "fat_g": 17, "fiber_g": 4, "sat_fat_g": 3, "added_sugar_g": 0},
        "burger": {"calories": 540, "protein_g": 31, "carbs_g": 41, "fat_g": 27, "fiber_g": 3, "sat_fat_g": 10, "added_sugar_g": 5},
        "chicken breast": {"calories": 231, "protein_g": 43.5, "carbs_g": 0, "fat_g": 5.0, "fiber_g": 0, "sat_fat_g": 1.4, "added_sugar_g": 0},
        "rice": {"calories": 205, "protein_g": 4.3, "carbs_g": 45, "fat_g": 0.4, "fiber_g": 0.6, "sat_fat_g": 0.1, "added_sugar_g": 0},
        "apple": {"calories": 95, "protein_g": 0.5, "carbs_g": 25, "fat_g": 0.3, "fiber_g": 4.4, "sat_fat_g": 0.1, "added_sugar_g": 19},
        "banana": {"calories": 105, "protein_g": 1.3, "carbs_g": 27, "fat_g": 0.4, "fiber_g": 3.1, "sat_fat_g": 0.1, "added_sugar_g": 14}
    }

    return nutrition_table.get(canonical, {
        "calories": 250, "protein_g": 6, "carbs_g": 30, "fat_g": 9,
        "fiber_g": 2, "sat_fat_g": 2, "added_sugar_g": 2
    })

def calculate_health_score(totals: Dict[str, float], detected_foods: List[str]) -> int:
    """
    Calculate health score (0-100) based on nutritional content.
    Formula from design.md:
    score = clamp(100 - 0.02 * max(0, calories - 500) - 1.2 * sat_fat_g
                  - 0.2 * added_sugar_g + 0.8 * fiber_g + 0.5 * protein_g, 0, 100)
    """
    cal = totals.get("calories", 0)
    sat = totals.get("sat_fat_g", 0)
    sug = totals.get("added_sugar_g", 0)
    fib = totals.get("fiber_g", 0)
    pro = totals.get("protein_g", 0)

    # Base calculation
    score = (100
             - 0.02 * max(0, cal - 500)
             - 1.2 * sat
             - 0.2 * sug
             + 0.8 * fib
             + 0.5 * pro)

    # Apply caution food penalties
    for food in detected_foods:
        normalized = normalize_label(food)
        if normalized in CAUTION_FOODS:
            penalty = CAUTION_FOODS[normalized]
            score -= penalty
            logger.info(f"Applied {penalty} point penalty for {normalized}")

    # Clamp to 0-100 range
    return max(0, min(100, int(round(score))))

def generate_tips_fallback(totals: Dict[str, float]) -> List[str]:
    """Generate fallback health tips based on nutritional content (used if AI fails)"""
    tips = []

    if totals.get("added_sugar_g", 0) >= 20:
        tips.append("Swap sugary drinks for water or unsweetened tea.")

    if totals.get("fiber_g", 0) < 5:
        tips.append("Add veggies or whole grains to increase fiber.")

    if totals.get("protein_g", 0) < 15:
        tips.append("Add a lean protein for satiety.")

    if totals.get("sat_fat_g", 0) >= 8:
        tips.append("Consider choosing leaner options to reduce saturated fat.")

    if totals.get("calories", 0) >= 600:
        tips.append("This is a calorie-dense meal - consider portion control.")

    if len(tips) == 0:
        tips.append("Great nutritional balance!")

    return tips


async def generate_tips_ai_huggingface(detected_foods: List[str], totals: Dict[str, float], health_score: int) -> List[str]:
    """
    Generate personalized health tips using FREE Hugging Face Inference API.

    Uses: meta-llama/Llama-3.2-3B-Instruct (free, no API key required)

    Provides context-aware, actionable advice based on:
    - Detected foods
    - Nutritional breakdown
    - Health score
    """
    try:
        import json
        import re

        # Prepare meal summary
        foods_str = ", ".join(detected_foods)

        prompt = f"""You are a friendly nutritionist. Provide 2-4 brief, actionable health tips for this meal.

Meal: {foods_str}
Calories: {int(totals.get('calories', 0))} | Protein: {totals.get('protein_g', 0):.1f}g | Carbs: {totals.get('carbs_g', 0):.1f}g | Fat: {totals.get('fat_g', 0):.1f}g
Fiber: {totals.get('fiber_g', 0):.1f}g | Sat Fat: {totals.get('sat_fat_g', 0):.1f}g | Sugar: {totals.get('added_sugar_g', 0):.1f}g
Health Score: {health_score}/100

Requirements:
- Keep each tip under 15 words
- Be specific to THIS meal
- Focus on actionable swaps or additions
- Be encouraging and positive

Return ONLY a JSON array of tip strings, nothing else.
Example: ["Add a side salad for fiber", "Swap soda for water"]"""

        # Use Hugging Face Inference API
        hf_api_key = os.getenv("HF_API_KEY", "")
        if not hf_api_key:
            logger.warning("HF_API_KEY not set - HuggingFace requires free API key for Llama models")
            logger.warning("Get free key at: https://huggingface.co/settings/tokens")
            return generate_tips_fallback(totals)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {hf_api_key}"
        }

        # Free model: meta-llama/Llama-3.2-3B-Instruct
        api_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False
            }
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)

            if response.status_code == 503:
                # Model loading (retry once after 5s)
                logger.info("HF model loading, retrying in 5s...")
                import asyncio
                await asyncio.sleep(5)
                response = await client.post(api_url, headers=headers, json=payload)

            response.raise_for_status()
            result = response.json()

        # Parse response
        if isinstance(result, list) and len(result) > 0:
            response_text = result[0].get("generated_text", "").strip()
        else:
            response_text = result.get("generated_text", "").strip()

        # Extract JSON array from response
        json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
        if json_match:
            tips = json.loads(json_match.group(0))
            if isinstance(tips, list) and len(tips) > 0:
                logger.info(f"Generated {len(tips)} HuggingFace AI tips")
                return tips[:4]

        logger.warning("HF AI returned invalid format, using fallback")
        return generate_tips_fallback(totals)

    except Exception as e:
        logger.error(f"HuggingFace AI tip generation failed: {e}, using fallback")
        return generate_tips_fallback(totals)


async def generate_tips_ai_openai(detected_foods: List[str], totals: Dict[str, float], health_score: int) -> List[str]:
    """
    Generate personalized health tips using OpenAI ChatGPT API.

    Uses: gpt-4o-mini (cheap, fast)
    Requires: OPENAI_API_KEY
    """
    try:
        import json
        import re

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("OPENAI_API_KEY not set, using fallback tips")
            return generate_tips_fallback(totals)

        # Prepare meal summary
        foods_str = ", ".join(detected_foods)

        prompt = f"""You are a friendly nutritionist providing brief, actionable health tips.

Meal Analysis:
- Detected foods: {foods_str}
- Total calories: {int(totals.get('calories', 0))}
- Protein: {totals.get('protein_g', 0):.1f}g
- Carbs: {totals.get('carbs_g', 0):.1f}g
- Fat: {totals.get('fat_g', 0):.1f}g
- Fiber: {totals.get('fiber_g', 0):.1f}g
- Saturated fat: {totals.get('sat_fat_g', 0):.1f}g
- Added sugar: {totals.get('added_sugar_g', 0):.1f}g
- Health score: {health_score}/100

Provide 2-4 brief, actionable health tips (1 sentence each):
1. Focus on practical improvements specific to THIS meal
2. Be encouraging and positive
3. Suggest specific swaps or additions when relevant
4. Keep tips under 15 words each

Return ONLY the tips as a JSON array of strings, no other text.
Example format: ["Tip 1 here", "Tip 2 here", "Tip 3 here"]"""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful nutritionist. Always respond with valid JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()

        # Parse response
        response_text = result["choices"][0]["message"]["content"].strip()

        # Extract JSON array (handle markdown code blocks)
        if "```" in response_text:
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)

        tips = json.loads(response_text)

        if isinstance(tips, list) and len(tips) > 0:
            logger.info(f"Generated {len(tips)} OpenAI tips")
            return tips[:4]
        else:
            logger.warning("OpenAI returned invalid format, using fallback")
            return generate_tips_fallback(totals)

    except Exception as e:
        logger.error(f"OpenAI tip generation failed: {e}, using fallback")
        return generate_tips_fallback(totals)


async def generate_tips_ai_anthropic(detected_foods: List[str], totals: Dict[str, float], health_score: int) -> List[str]:
    """
    Generate personalized health tips using Claude AI (Anthropic).

    Uses: claude-3-5-haiku-20241022
    Requires: ANTHROPIC_API_KEY
    """
    try:
        import anthropic
        import json
        import re

        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY not set, using fallback tips")
            return generate_tips_fallback(totals)

        client = anthropic.Anthropic(api_key=anthropic_api_key)

        # Prepare meal summary
        foods_str = ", ".join(detected_foods)

        prompt = f"""You are a friendly nutritionist providing brief, actionable health tips.

Meal Analysis:
- Detected foods: {foods_str}
- Total calories: {int(totals.get('calories', 0))}
- Protein: {totals.get('protein_g', 0):.1f}g
- Carbs: {totals.get('carbs_g', 0):.1f}g
- Fat: {totals.get('fat_g', 0):.1f}g
- Fiber: {totals.get('fiber_g', 0):.1f}g
- Saturated fat: {totals.get('sat_fat_g', 0):.1f}g
- Added sugar: {totals.get('added_sugar_g', 0):.1f}g
- Health score: {health_score}/100

Provide 2-4 brief, actionable health tips (1 sentence each):
1. Focus on practical improvements specific to THIS meal
2. Be encouraging and positive
3. Suggest specific swaps or additions when relevant
4. Keep tips under 15 words each

Return ONLY the tips as a JSON array of strings, no other text.
Example format: ["Tip 1 here", "Tip 2 here", "Tip 3 here"]"""

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=300,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        response_text = message.content[0].text.strip()

        # Extract JSON array (handle markdown code blocks)
        if "```" in response_text:
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)

        tips = json.loads(response_text)

        if isinstance(tips, list) and len(tips) > 0:
            logger.info(f"Generated {len(tips)} Anthropic tips")
            return tips[:4]
        else:
            logger.warning("Anthropic returned invalid format, using fallback")
            return generate_tips_fallback(totals)

    except ImportError:
        logger.warning("anthropic package not installed, using fallback tips")
        return generate_tips_fallback(totals)
    except Exception as e:
        logger.error(f"Anthropic tip generation failed: {e}, using fallback")
        return generate_tips_fallback(totals)


async def generate_tips_ai(detected_foods: List[str], totals: Dict[str, float], health_score: int) -> List[str]:
    """
    Generate personalized health tips using AI (multi-provider support).

    Supports (in priority order):
    1. HuggingFace (FREE, default) - Llama 3.2 3B Instruct
    2. OpenAI - gpt-4o-mini (requires OPENAI_API_KEY)
    3. Anthropic - Claude 3.5 Haiku (requires ANTHROPIC_API_KEY)

    Falls back to rule-based tips if all providers fail.
    """
    # Get AI provider preference
    ai_provider = os.getenv("AI_TIP_PROVIDER", "huggingface").lower()

    logger.info(f"Using AI provider: {ai_provider}")

    # Try preferred provider
    if ai_provider == "openai":
        return await generate_tips_ai_openai(detected_foods, totals, health_score)
    elif ai_provider == "anthropic":
        return await generate_tips_ai_anthropic(detected_foods, totals, health_score)
    else:  # Default to HuggingFace (free)
        return await generate_tips_ai_huggingface(detected_foods, totals, health_score)


async def generate_tips(detected_foods: List[str], totals: Dict[str, float], health_score: int) -> List[str]:
    """
    Generate health tips with AI enhancement when available.

    Uses Claude AI for personalized tips, falls back to rule-based tips if:
    - ANTHROPIC_API_KEY not configured
    - AI request fails
    - Invalid response format
    """
    # Check if AI tips are enabled
    use_ai_tips = os.getenv("ENABLE_AI_TIPS", "true").lower() == "true"

    if use_ai_tips:
        return await generate_tips_ai(detected_foods, totals, health_score)
    else:
        return generate_tips_fallback(totals)

async def persist_preprocessing_experiment(inference_id: int, quality_metrics: Dict, preprocessing_params: Dict) -> Optional[int]:
    """
    Persist preprocessing experiment data for A/B testing analysis.

    Args:
        inference_id: ID of the inference record
        quality_metrics: Image quality metrics (brightness, variance, quality_score)
        preprocessing_params: Preprocessing parameters used (strategy, contrast, sharpness)

    Returns:
        Experiment ID if successful, None otherwise
    """
    supabase = await get_supabase_client()
    if not supabase:
        return None

    try:
        result = supabase.table('preprocessing_experiments').insert({
            'inference_id': inference_id,
            'strategy_name': quality_metrics.get('strategy', 'adaptive'),
            'quality_metrics': quality_metrics,
            'preprocessing_params': preprocessing_params
        }).execute()

        experiment_id = result.data[0]['id'] if result.data else None
        logger.info(f"Persisted preprocessing experiment {experiment_id} with strategy '{quality_metrics.get('strategy')}'")
        return experiment_id
    except Exception as e:
        logger.error(f"Failed to persist preprocessing experiment: {e}")
        return None


async def persist_meal_data(inference_data: Dict, meal_data: Dict, quality_metrics: Dict = None) -> Optional[int]:
    """
    Persist meal analysis to Supabase database with optional preprocessing experiment data.

    Args:
        inference_data: Model inference information
        meal_data: Meal analysis results
        quality_metrics: Optional preprocessing quality metrics for A/B testing

    Returns:
        Meal ID if successful, None otherwise
    """
    supabase = await get_supabase_client()
    if not supabase:
        return None

    try:
        # Insert inference record
        inference_result = supabase.table('inferences').insert({
            'labels': inference_data['labels'],
            'model_name': inference_data.get('model_name', HF_MODEL_ID),
            'latency_ms': inference_data.get('latency_ms', 0)
        }).execute()

        inference_id = inference_result.data[0]['id'] if inference_result.data else None

        # Insert preprocessing experiment if quality metrics provided
        if inference_id and quality_metrics:
            preprocessing_params = {
                'contrast_factor': quality_metrics.get('contrast_factor'),
                'sharpness_factor': quality_metrics.get('sharpness_factor'),
                'brightness_factor': quality_metrics.get('brightness_factor'),
                'color_factor': quality_metrics.get('color_factor'),
                'lighting_adjusted': quality_metrics.get('lighting_adjusted')
            }
            await persist_preprocessing_experiment(inference_id, quality_metrics, preprocessing_params)

        # Insert meal record
        meal_result = supabase.table('meals').insert({
            'user_id': None,  # No auth for MVP
            'total_calories': meal_data['total_calories'],
            'health_score': meal_data['health_score'],
            'inference_id': inference_id
        }).execute()

        meal_id = meal_result.data[0]['id'] if meal_result.data else None

        # Insert meal items
        if meal_id:
            for item in meal_data['items']:
                # Handle both dict and Pydantic model
                if hasattr(item, 'model_dump'):  # Pydantic v2
                    item_dict = item.model_dump()
                elif hasattr(item, 'dict'):  # Pydantic v1
                    item_dict = item.dict()
                else:  # Already a dict
                    item_dict = item

                nutrition = item_dict['nutrition']
                supabase.table('meal_items').insert({
                    'meal_id': meal_id,
                    'label': item_dict['label'],
                    'confidence': item_dict['confidence'],
                    'servings': item_dict['servings'],
                    'calories': nutrition['calories'],
                    'protein_g': nutrition['protein_g'],
                    'carbs_g': nutrition['carbs_g'],
                    'fat_g': nutrition['fat_g'],
                    'fiber_g': nutrition.get('fiber_g', 0),
                    'sat_fat_g': nutrition.get('sat_fat_g', 0),
                    'added_sugar_g': nutrition.get('added_sugar_g', 0)
                }).execute()

        return meal_id
    except Exception as e:
        logger.error(f"Failed to persist meal data: {e}")
        return None

class HealthResponse(BaseModel):
    """Health check response model"""
    ok: bool
    model_loaded: bool = False
    timestamp: str

class NutritionInfo(BaseModel):
    """Nutrition information model"""
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float = 0
    sat_fat_g: float = 0
    added_sugar_g: float = 0

class FoodItem(BaseModel):
    """Detected food item model"""
    label: str
    confidence: float
    servings: float
    nutrition: NutritionInfo

class AnalysisResponse(BaseModel):
    """Food analysis response model"""
    total_calories: int
    health_score: int
    items: List[FoodItem]
    tips: List[str]

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check endpoint"""
    return HealthResponse(
        ok=True,
        model_loaded=model is not None,
        timestamp=str(time.time())
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_food(image: UploadFile = File(...)):
    """
    Analyze food image and return nutrition breakdown with health score.

    Accepts multipart/form-data with 'image' field containing JPEG, PNG, or WebP image.
    Returns detected foods, nutritional information, and health score (0-100).
    """
    # Validate image type
    if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: {image.content_type}. Supported: JPEG, PNG, WebP"
        )

    # Validate image size (8MB limit)
    MAX_SIZE = 8 * 1024 * 1024  # 8MB
    image_data = await image.read()
    if len(image_data) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image too large: {len(image_data)} bytes. Max size: {MAX_SIZE} bytes"
        )

    try:
        # Load and preprocess image with advanced quality assessment
        img = Image.open(io.BytesIO(image_data))
        preprocessed_img, quality_metrics = preprocess_image(img)

        logger.info(f"Image preprocessed successfully with quality score: {quality_metrics['quality_score']:.2f}")

        # Load AI model
        clf = load_model()

        # Run inference with preprocessed image
        start_time = time.time()
        predictions = clf(preprocessed_img)
        inference_time = int((time.time() - start_time) * 1000)

        logger.info(f"Inference completed in {inference_time}ms with {len(predictions)} predictions")

        # Apply improved multi-label heuristic from design.md
        # Using top 10 predictions now (model loaded with top_k=10)
        top_predictions = predictions[:10] if len(predictions) >= 10 else predictions

        if not top_predictions:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Model failed to make predictions"
            )

        # Log top predictions for debugging
        logger.info(f"Top prediction: {top_predictions[0]['label']} ({top_predictions[0]['score']:.3f})")

        # DYNAMIC CONFIDENCE THRESHOLDS based on image quality
        # High quality images (>0.7): stricter thresholds
        # Low quality images (<0.4): more lenient to compensate
        p_main = top_predictions[0]["score"]
        quality_score = quality_metrics['quality_score']

        if quality_score >= 0.7:
            # High quality: be more selective
            base_threshold = 0.14
            relative_threshold = 0.60
            logger.info("High quality image: using stricter thresholds")
        elif quality_score >= 0.4:
            # Medium quality: balanced thresholds
            base_threshold = 0.12
            relative_threshold = 0.55
            logger.info("Medium quality image: using balanced thresholds")
        else:
            # Low quality: be more lenient
            base_threshold = 0.10
            relative_threshold = 0.50
            logger.info("Low quality image: using lenient thresholds")

        # Apply dynamic thresholds
        kept_predictions = [
            p for p in top_predictions
            if p["score"] >= max(base_threshold, p_main * relative_threshold)
        ][:3]  # Cap to max 3 items as per design.md

        # UNCERTAINTY QUANTIFICATION
        # Calculate confidence spread and entropy for prediction quality assessment
        if len(kept_predictions) > 1:
            scores = [p["score"] for p in kept_predictions]
            confidence_spread = max(scores) - min(scores)
            # High spread (>0.3) = clear winner, Low spread (<0.15) = uncertain
            uncertainty_level = "low" if confidence_spread > 0.3 else "medium" if confidence_spread > 0.15 else "high"
            logger.info(f"Prediction uncertainty: {uncertainty_level} (spread: {confidence_spread:.3f})")
            quality_metrics['uncertainty'] = uncertainty_level
            quality_metrics['confidence_spread'] = confidence_spread

        logger.info(f"Kept {len(kept_predictions)} predictions after dynamic threshold filtering")

        # Process detected foods
        items = []
        totals = {
            "calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0,
            "fiber_g": 0, "sat_fat_g": 0, "added_sugar_g": 0
        }
        detected_food_names = []

        for pred in kept_predictions:
            food_name = pred["label"].lower()
            detected_food_names.append(food_name)
            nutrition = await lookup_nutrition(food_name)

            item = FoodItem(
                label=food_name,
                confidence=round(pred["score"], 3),
                servings=1.0,  # Default to 1 serving for MVP
                nutrition=NutritionInfo(**nutrition)
            )
            items.append(item)

            # Accumulate totals
            for key in totals:
                totals[key] += nutrition.get(key, 0)

        # Calculate health score
        health_score = calculate_health_score(totals, detected_food_names)

        # Generate tips (AI-powered with fallback)
        tips = await generate_tips(detected_food_names, totals, health_score)

        # Prepare response
        response_data = {
            "total_calories": int(totals["calories"]),
            "health_score": health_score,
            "items": items,
            "tips": tips
        }

        # Persist to database (async, don't block response)
        try:
            inference_data = {
                "labels": [{"label": p["label"], "score": p["score"]} for p in kept_predictions],
                "model_name": HF_MODEL_ID,
                "latency_ms": inference_time
            }
            await persist_meal_data(inference_data, response_data, quality_metrics)
        except Exception as e:
            logger.error(f"Failed to persist meal data: {e}")

        return AnalysisResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@app.get("/foods")
async def get_foods():
    """
    Get list of known foods and their nutritional information.

    Returns all foods from the nutrition_facts database table.
    """
    supabase = await get_supabase_client()
    if not supabase:
        # Return hardcoded foods if no database
        return {
            "foods": [
                {"name": "pizza", "calories": 285, "protein_g": 12},
                {"name": "salad", "calories": 150, "protein_g": 4},
                {"name": "burger", "calories": 540, "protein_g": 31}
            ],
            "source": "fallback"
        }

    try:
        result = supabase.table('nutrition_facts').select('*').execute()
        return {
            "foods": result.data,
            "source": "database",
            "count": len(result.data)
        }
    except Exception as e:
        logger.error(f"Failed to fetch foods: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch foods from database"
        )


# User Feedback Models
class UserFeedbackRequest(BaseModel):
    """User feedback submission model"""
    meal_id: int
    rating: int  # 1-5 overall satisfaction
    accuracy_rating: Optional[int] = None  # 1-5 detection accuracy
    detected_items: Optional[List[str]] = None  # What we detected
    corrected_items: Optional[List[str]] = None  # What user says it actually was
    missing_items: Optional[List[str]] = None  # Foods we missed
    incorrect_items: Optional[List[str]] = None  # Foods we wrongly detected
    comments: Optional[str] = None
    cuisine_type: Optional[str] = None  # e.g., "italian", "chinese", "mexican"
    image_quality_issue: Optional[bool] = False
    portion_accuracy: Optional[bool] = None


@app.post("/feedback")
async def submit_feedback(feedback: UserFeedbackRequest):
    """
    Submit user feedback for model improvement.

    This endpoint collects user corrections and ratings to improve:
    - Model accuracy through training data collection
    - Preprocessing strategy selection
    - Regional cuisine support
    - Portion size estimation

    Args:
        feedback: UserFeedbackRequest with correction data

    Returns:
        Success message with feedback ID
    """
    supabase = await get_supabase_client()
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Feedback system unavailable"
        )

    try:
        # Validate rating ranges
        if not (1 <= feedback.rating <= 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )

        if feedback.accuracy_rating and not (1 <= feedback.accuracy_rating <= 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Accuracy rating must be between 1 and 5"
            )

        # Insert feedback
        result = supabase.table('user_feedback').insert({
            'meal_id': feedback.meal_id,
            'user_id': None,  # No auth for MVP
            'rating': feedback.rating,
            'accuracy_rating': feedback.accuracy_rating,
            'detected_items': feedback.detected_items,
            'corrected_items': feedback.corrected_items,
            'missing_items': feedback.missing_items,
            'incorrect_items': feedback.incorrect_items,
            'comments': feedback.comments,
            'cuisine_type': feedback.cuisine_type,
            'image_quality_issue': feedback.image_quality_issue,
            'portion_accuracy': feedback.portion_accuracy
        }).execute()

        feedback_id = result.data[0]['id'] if result.data else None

        # Update preprocessing experiment with user rating if available
        if feedback.accuracy_rating:
            try:
                # Get inference_id from meal
                meal_result = supabase.table('meals').select('inference_id').eq('id', feedback.meal_id).execute()
                if meal_result.data:
                    inference_id = meal_result.data[0].get('inference_id')
                    if inference_id:
                        # Update experiment with user rating
                        supabase.table('preprocessing_experiments').update({
                            'user_rating': feedback.accuracy_rating
                        }).eq('inference_id', inference_id).execute()
                        logger.info(f"Updated preprocessing experiment for inference {inference_id} with rating {feedback.accuracy_rating}")
            except Exception as e:
                logger.error(f"Failed to update preprocessing experiment: {e}")

        logger.info(f"Received feedback {feedback_id} for meal {feedback.meal_id}: rating={feedback.rating}, accuracy={feedback.accuracy_rating}")

        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": "Thank you for your feedback! It helps us improve."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@app.get("/feedback/stats")
async def get_feedback_stats():
    """
    Get aggregated feedback statistics for model improvement analysis.

    Returns statistics on:
    - Average ratings by preprocessing strategy
    - Common corrections and missing items
    - Cuisine-specific accuracy
    - Image quality correlation with accuracy

    Useful for:
    - A/B testing analysis
    - Model fine-tuning priorities
    - Regional cuisine expansion
    """
    supabase = await get_supabase_client()
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stats unavailable"
        )

    try:
        # Get all feedback with preprocessing experiment data
        feedback_result = supabase.table('user_feedback').select('*').execute()

        if not feedback_result.data:
            return {
                "total_feedback": 0,
                "message": "No feedback data available yet"
            }

        feedbacks = feedback_result.data
        total_count = len(feedbacks)

        # Calculate average ratings
        avg_rating = sum(f['rating'] for f in feedbacks) / total_count
        accuracy_ratings = [f['accuracy_rating'] for f in feedbacks if f.get('accuracy_rating')]
        avg_accuracy = sum(accuracy_ratings) / len(accuracy_ratings) if accuracy_ratings else None

        # Collect missing items for training data priorities
        missing_items = []
        for f in feedbacks:
            if f.get('missing_items'):
                missing_items.extend(f['missing_items'])

        # Count by cuisine type
        cuisine_counts = {}
        for f in feedbacks:
            cuisine = f.get('cuisine_type')
            if cuisine:
                cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1

        return {
            "total_feedback": total_count,
            "avg_rating": round(avg_rating, 2),
            "avg_accuracy_rating": round(avg_accuracy, 2) if avg_accuracy else None,
            "most_missing_items": list(set(missing_items))[:10],  # Top 10 unique missing items
            "cuisine_distribution": cuisine_counts,
            "image_quality_issues": sum(1 for f in feedbacks if f.get('image_quality_issue'))
        }

    except Exception as e:
        logger.error(f"Failed to get feedback stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)