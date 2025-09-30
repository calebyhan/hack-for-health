# Tasks

A step‑by‑step, checkbox‑driven plan from zero → demo. Check items off as you complete them.

## Phase 0 — Setup
- [x] **Create repo** with two folders: `web/` (Next.js + React + Tailwind) and `api/` (FastAPI).
- [x] **Initialize** package managers: `pnpm create next-app@latest web` (or `npm`), `uv venv && uv pip install fastapi uvicorn pillow python-multipart` in `api/` (or `pip`).
- [x] **Create shared .env examples**: `web/.env.local.example`, `api/.env.example`.
- [x] **Spin up Supabase** project; copy URL + anon key to `web/.env.local` and service role key to `api/.env` (if needed for server tasks).

## Phase 1 — Database (Supabase)
- [x] Create tables with the SQL in `design.md` (Users, Meals, MealItems, NutritionFacts, Inferences).
- [x] Configure Row Level Security (RLS) as per `design.md` (enable, basic policies).
- [x] Seed minimal `nutrition_facts` rows for top‑20 common foods (banana, apple, rice, chicken breast, pizza slice, salad base...).
- [x] Generate Supabase types for frontend (optional): `npx supabase gen types --project-id ...`.

## Phase 2 — Backend API (FastAPI)
- [x] Implement `/health` (GET) for readiness.
- [x] Implement `/analyze` (POST multipart/form-data) to accept an image.
  - [x] Validate image (size ≤ 8MB, supported formats).
  - [x] Run AI pipeline (see `design.md`): classify foods (multi‑label heuristic), map to nutrition.
  - [x] Estimate servings (simple default 1 serving; allow override via query in future).
  - [x] Compute **Health Score** (0–100) per `design.md`.
  - [x] Persist Meal + Items + Inference to Supabase.
  - [x] Return JSON response with breakdown + score.
- [x] Implement `/foods` (GET) to list known foods and macronutrients (from Supabase).
- [x] Add minimal logging + error handling.
- [x] Containerize API (Dockerfile) for easy deploy (Railway/Fly.io/Render).

## Phase 3 — AI Model Integration
- [x] Add Hugging Face inference: `food101` classifier (e.g., `nateraw/food` or `vit-base-patch16-224` finetunes). Fallback: general image classifier.
- [x] Convert top‑K logits to multi‑label guesses using confidence thresholds.
- [x] Add synonym map (e.g., "fries" → "french fries", "soda" → "cola").
- [x] Create mapping from detected label → nutrition rows (Supabase `nutrition_facts`).

## Phase 4 — Frontend (Next.js)
- [x] Build **Landing**: title, tagline, CTA.
- [x] Build **Upload page**: drag‑and‑drop image (Dropzone), preview thumbnail, submit to `/api/analyze` route.
- [x] Show **Results page/section**:
  - [x] Health Score (big number), traffic‑light chip (green/yellow/red).
  - [x] Macronutrient bars (calories, protein, carbs, fat).
  - [x] Detected foods list with servings and confidence.
  - [x] "Try another photo" button.
- [ ] Add **History** page (optional): list past meals from Supabase for authenticated users.
- [x] Apply **Tailwind** for clean, accessible UI.
- [x] DO NOT USE USEEFFECT, USE REACT QUERY

## Phase 5 — Frontend ↔ Backend wiring
- [x] Next.js API route `/api/analyze` that forwards multipart to FastAPI (or call FastAPI directly from client if CORS safe).
- [x] Configure CORS for `web` origin in FastAPI.
- [x] Store result in Supabase via frontend (or rely on backend persistence).

## Phase 6 — Auth (Optional for MVP)
- [ ] Enable Supabase Auth (Email/Password or OAuth).
- [ ] Use PKCE flow in Next.js. Persist `user_id` with meals.

## Phase 7 — QA & Polish
- [ ] Test with varied images (salad, pizza, mixed plate).
- [ ] Tune thresholds for multi‑label detection.
- [x] Add skeleton loaders, error toasts, empty states.
- [x] Accessibility pass (alt text, focus states, color contrast).

## Phase 8 — Demo & Submission
- [ ] Record a 2–3 min video: intro → upload → results → brief architecture.
- [ ] Prepare Devpost page: title, description, repo links, screenshots.
- [ ] Deploy web (Vercel) + api (Railway/Render). Verify public access.