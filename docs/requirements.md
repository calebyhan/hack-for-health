# Requirements

## Project Title
**Healthy Eating Helper** — photo → nutrition breakdown → health score

## Problem
People struggle to estimate what’s in their meals, especially when eating out or tracking casually. Manual logging is tedious; most apps require searching databases. A fast, photo‑based helper lowers friction and encourages awareness.

## Goal
Build a web app that lets a user upload a meal photo and instantly see:
- Detected foods (top 1–3 items)
- Estimated macronutrients & calories (per item + total)
- A single **Health Score (0–100)** with friendly guidance

## Non‑Goals (MVP)
- Exact portion size estimation from image geometry
- Medical advice or diagnosis
- Full diet planning or meal scheduling

## Users
- Health‑curious students and professionals
- People wanting a quick nutrition glance while dining out

## Success Metrics
- Time to result < 5 seconds on common images (after cold‑start)
- Reasonable detection on common foods (pizza, salad, burger, rice bowls, fruit)
- Clear, friendly UI with a one‑screen result

## Deliverables
- Next.js web app with image upload & results view
- FastAPI backend that accepts images and returns structured nutrition estimates
- Supabase database storing nutrition facts and meal history
- Short demo video (2–3 minutes)
- Public repo + README + screenshots

## Judging Alignment
- **Impact**: Lowers friction of nutrition awareness; supports healthier choices.
- **Innovation**: Combines CV model + heuristic scoring + clean UX.
- **Technical Implementation**: HF image classification, FastAPI service, Supabase schema, Next.js UI.
- **Design**: Simple, accessible, responsive layout with meaningful visualizations.