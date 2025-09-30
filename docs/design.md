# Design & Architecture

## System Overview
- **Frontend**: Next.js (App Router), React, TailwindCSS, Upload page + Results view.
- **Backend**: FastAPI with endpoints `/health`, `/analyze`, `/foods`.
- **AI**: Hugging Face image classification (Food‑focused model when available; fallback general image classifier).
- **DB**: Supabase (Postgres) for `nutrition_facts`, `meals`, `meal_items`, `inferences`, and optional `users`.
- **Deploy**: Web on Vercel; API on Railway/Render/Fly.io. Environment variables shared via `.env`.

```
[Browser] --upload--> [Next.js] --multipart--> [FastAPI /analyze]
                                   |                       |
                                   |                 [HF Model Inference]
                                   |                       |
                                [Supabase] <---- persist results ----
```

## Tech Stack (versions suggestive)
- Next.js 15+, React 18+, TailwindCSS 3+
  - DO NOT USE USEEFFECT, USE REACT QUERY
- FastAPI 0.111+, Uvicorn 0.30+, Pillow, python‑multipart
- Hugging Face `transformers` / `torch` (CPU ok for MVP)
- Supabase JS client (frontend), `postgrest` via REST or server‑side service key (backend)

## API Design

### POST `/analyze`
**Request**: `multipart/form-data` with field `image`  
**Response (200)**:
```json
{
  "total_calories": 520,
  "health_score": 62,
  "items": [
    {"label": "pizza", "confidence": 0.91, "servings": 1.0,
     "nutrition": {"calories": 285, "protein_g": 12, "carbs_g": 36, "fat_g": 10}}
  ],
  "tips": ["Consider adding a side salad for fiber."]
}
```
**Errors**: 400 invalid image; 500 model failure.

### GET `/foods`
Returns known foods + per‑serving macronutrients from `nutrition_facts`.

### GET `/health`
Readiness probe.

## AI Integration Pipeline

1. **Load model** (at startup) — prefer a food classifier (e.g., Food‑101 finetuned ViT).  
2. **Preprocess**: Resize to 224×224, normalize.
3. **Inference**: Get top‑K predictions (K=5).
4. **Multi‑label heuristic**:
   - Keep all labels with `p >= p_main * 0.6` and `p >= 0.15` (captures combos like “salad + chicken”).  
   - Cap to max 3 items.
5. **Synonym map**: Normalize labels (e.g., *fries* → *french fries*; *cola* → *soda*).
6. **Nutrition mapping**: For each label, lookup `nutrition_facts` by `canonical_name`. If missing, fallback to a generic class (e.g., *pasta*, *salad*).
7. **Serving estimation (MVP)**: Default `1.0` serving per detected item. (UI can later allow user to tweak.)
8. **Health Score (0–100)**:
   - Start at 100.
   - Penalize per‑calorie density and saturated fat; reward fiber & protein.
   - Example formula (MVP, per total meal):
     \n
     **score = clamp( 100
       − 0.02 * max(0, calories − 500)
       − 1.2 * sat_fat_g
       − 0.2 * added_sugar_g
       + 0.8 * fiber_g
       + 0.5 * protein_g , 0, 100)**
   - If any item is in a *caution list* (e.g., soda, fries), subtract 5–10.
9. **Tips**: Rule‑based suggestions (“Add greens”, “Swap soda for water”).

> **Note:** This is an educational estimate, **not medical advice**.

## Data Model (Supabase)

```sql
-- USERS (optional if you add auth)
create table if not exists users (
  id uuid primary key default uuid_generate_v4(),
  email text unique,
  created_at timestamptz default now()
);

-- CANONICAL FOOD NUTRITION (per serving)
create table if not exists nutrition_facts (
  id bigserial primary key,
  canonical_name text unique not null,   -- e.g., "pizza", "salad", "cola"
  calories int not null,
  protein_g numeric not null,
  carbs_g numeric not null,
  fat_g numeric not null,
  fiber_g numeric default 0,
  sat_fat_g numeric default 0,
  added_sugar_g numeric default 0
);

-- INFERENCES (raw model outputs)
create table if not exists inferences (
  id bigserial primary key,
  created_at timestamptz default now(),
  labels jsonb not null,                 -- e.g., [{"label":"pizza","score":0.91}, ...]
  model_name text,
  latency_ms int
);

-- MEALS (a single upload/result)
create table if not exists meals (
  id bigserial primary key,
  user_id uuid references users(id),
  created_at timestamptz default now(),
  total_calories int,
  health_score int,
  inference_id bigint references inferences(id),
  image_url text                           -- optional if storing on Supabase Storage
);

-- MEAL ITEMS (component foods per meal)
create table if not exists meal_items (
  id bigserial primary key,
  meal_id bigint references meals(id) on delete cascade,
  nutrition_id bigint references nutrition_facts(id),
  label text,
  confidence numeric,
  servings numeric default 1.0,
  calories int,
  protein_g numeric,
  carbs_g numeric,
  fat_g numeric,
  fiber_g numeric,
  sat_fat_g numeric,
  added_sugar_g numeric
);
```

### RLS (sketch)
- Enable RLS on `meals`, `meal_items` with policies: users can select/insert/update their own rows by `user_id`.

## Minimal FastAPI Example

```python
# api/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
import io, time
from typing import List, Dict
import os
from pydantic import BaseModel

app = FastAPI()

# Lazy import to keep cold start fast in local dev
model = None
labels_map = {"fries": "french fries", "cola": "soda"}  # extend

def load_model():
    global model
    if model is None:
        from transformers import pipeline
        model = pipeline("image-classification", model="nateraw/food")
    return model

def health_score(total):
    cal = total.get("calories", 0)
    sat = total.get("sat_fat_g", 0)
    sug = total.get("added_sugar_g", 0)
    fib = total.get("fiber_g", 0)
    pro = total.get("protein_g", 0)
    score = 100 - 0.02*max(0, cal-500) - 1.2*sat - 0.2*sug + 0.8*fib + 0.5*pro
    return max(0, min(100, int(round(score))))

def lookup_nutrition(name: str) -> Dict:
    # TODO: pull from Supabase; for MVP use a tiny in-memory map
    canonical = labels_map.get(name, name).lower()
    table = {
        "pizza": {"calories": 285, "protein_g":12, "carbs_g":36, "fat_g":10, "fiber_g":2, "sat_fat_g":4, "added_sugar_g":2},
        "salad": {"calories": 150, "protein_g":4, "carbs_g":10, "fat_g":10, "fiber_g":3, "sat_fat_g":2, "added_sugar_g":1},
        "soda": {"calories": 150, "protein_g":0, "carbs_g":39, "fat_g":0, "fiber_g":0, "sat_fat_g":0, "added_sugar_g":39},
        "french fries": {"calories": 365, "protein_g":4, "carbs_g":48, "fat_g":17, "fiber_g":4, "sat_fat_g":3, "added_sugar_g":0}
    }
    return table.get(canonical, {"calories": 250, "protein_g":6, "carbs_g":30, "fat_g":9, "fiber_g":2, "sat_fat_g":2, "added_sugar_g":2})

@app.post("/analyze")
async def analyze(image: UploadFile = File(...)):
    if image.content_type not in {"image/jpeg","image/png","image/webp"}:
        raise HTTPException(status_code=400, detail="Unsupported image type")
    raw = await image.read()
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    clf = load_model()
    t0 = time.time()
    preds = clf(img)[:5]
    p_main = preds[0]["score"]
    kept = [p for p in preds if p["score"] >= max(0.15, p_main*0.6)][:3]

    items = []
    totals = {"calories":0, "protein_g":0, "carbs_g":0, "fat_g":0, "fiber_g":0, "sat_fat_g":0, "added_sugar_g":0}
    for p in kept:
        name = p["label"].lower()
        nut = lookup_nutrition(name)
        items.append({
            "label": name,
            "confidence": round(p["score"], 3),
            "servings": 1.0,
            "nutrition": nut
        })
        for k in totals:
            totals[k] += nut.get(k, 0)

    score = health_score(totals)
    tips = []
    if totals["added_sugar_g"] >= 20: tips.append("Swap sugary drinks for water or unsweetened tea.")
    if totals["fiber_g"] < 5: tips.append("Add veggies or whole grains to increase fiber.")
    if totals["protein_g"] < 15: tips.append("Add a lean protein for satiety.")

    return {"total_calories": totals["calories"], "health_score": score, "items": items, "tips": tips}

@app.get("/health")
def health():
    return {"ok": True}
```

## Minimal Next.js Upload Flow (sketch)

```tsx
// web/app/page.tsx
"use client";
import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!file) return;
    setLoading(true);
    const fd = new FormData();
    fd.append("image", file);
    const res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/analyze", { method: "POST", body: fd });
    const data = await res.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <main className="max-w-2xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Healthy Eating Helper</h1>
      <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
      <button onClick={submit} className="px-4 py-2 rounded bg-black text-white disabled:opacity-50" disabled={!file || loading}>
        {loading ? "Analyzing..." : "Analyze Meal"}
      </button>

      {result && (
        <section className="space-y-2">
          <div className="text-2xl">Health Score: <b>{result.health_score}</b></div>
          <div>Total Calories: {result.total_calories}</div>
          <ul className="list-disc pl-5">
            {result.items.map((it: any, i: number) => (
              <li key={i}>{it.label} — conf {it.confidence} — {it.nutrition.calories} kcal</li>
            ))}
          </ul>
          {result.tips?.length ? <div className="text-sm opacity-80">Tips: {result.tips.join(" ")}</div> : null}
        </section>
      )}
    </main>
  );
}
```

## Deployment Notes
- **Web**: Vercel (set `NEXT_PUBLIC_API_URL`).
- **API**: Railway/Render with Dockerfile. Pin Python 3.11+, add `transformers`, `torch`.
- **Cold start**: Warm model on first request; optionally preload at startup.
- **Privacy**: Do not store images by default in MVP. If you do, use Supabase Storage with short‑lived signed URLs.