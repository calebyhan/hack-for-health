# Healthy Eating Helper API

FastAPI backend service for food image analysis and nutrition estimation.

## Features

- `/health` - Service health check
- `/analyze` - Upload food image for AI analysis
- `/foods` - List known foods and nutrition facts
- Hugging Face food classification model integration
- Supabase database persistence
- Multi-label food detection with confidence thresholds
- Health score calculation (0-100)

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Environment setup**:
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

3. **Run locally**:
```bash
uvicorn main:app --reload --port 8000
```

4. **Test endpoints**:
```bash
# Health check
curl http://localhost:8000/health

# Analyze food image
curl -X POST -F "image=@path/to/food.jpg" http://localhost:8000/analyze

# Get foods list
curl http://localhost:8000/foods
```

## API Reference

### POST `/analyze`
Upload food image for nutrition analysis.

**Request**: `multipart/form-data` with `image` field
**Response**:
```json
{
  "total_calories": 520,
  "health_score": 62,
  "items": [
    {
      "label": "pizza",
      "confidence": 0.91,
      "servings": 1.0,
      "nutrition": {
        "calories": 285,
        "protein_g": 12,
        "carbs_g": 36,
        "fat_g": 10
      }
    }
  ],
  "tips": ["Consider adding a side salad for fiber."]
}
```

### GET `/foods`
List all known foods and their nutritional information.

### GET `/health`
Service readiness check.

## Deployment

Build and deploy with Docker:

```bash
docker build -t healthy-eating-api .
docker run -p 8000:8000 --env-file .env healthy-eating-api
```