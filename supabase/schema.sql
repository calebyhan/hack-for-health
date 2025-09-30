-- Healthy Eating Helper Database Schema
-- Run this script in your Supabase SQL editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- USERS table (optional for MVP, required for auth)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CANONICAL FOOD NUTRITION (per serving)
CREATE TABLE IF NOT EXISTS nutrition_facts (
  id BIGSERIAL PRIMARY KEY,
  canonical_name TEXT UNIQUE NOT NULL,   -- e.g., "pizza", "salad", "cola"
  calories INT NOT NULL,
  protein_g NUMERIC NOT NULL,
  carbs_g NUMERIC NOT NULL,
  fat_g NUMERIC NOT NULL,
  fiber_g NUMERIC DEFAULT 0,
  sat_fat_g NUMERIC DEFAULT 0,
  added_sugar_g NUMERIC DEFAULT 0
);

-- INFERENCES (raw model outputs for debugging)
CREATE TABLE IF NOT EXISTS inferences (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  labels JSONB NOT NULL,                 -- e.g., [{"label":"pizza","score":0.91}, ...]
  model_name TEXT,
  latency_ms INT
);

-- MEALS (a single upload/result)
CREATE TABLE IF NOT EXISTS meals (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  total_calories INT,
  health_score INT,
  inference_id BIGINT REFERENCES inferences(id),
  image_url TEXT                           -- optional if storing on Supabase Storage
);

-- MEAL ITEMS (component foods per meal)
CREATE TABLE IF NOT EXISTS meal_items (
  id BIGSERIAL PRIMARY KEY,
  meal_id BIGINT REFERENCES meals(id) ON DELETE CASCADE,
  nutrition_id BIGINT REFERENCES nutrition_facts(id),
  label TEXT,
  confidence NUMERIC,
  servings NUMERIC DEFAULT 1.0,
  calories INT,
  protein_g NUMERIC,
  carbs_g NUMERIC,
  fat_g NUMERIC,
  fiber_g NUMERIC,
  sat_fat_g NUMERIC,
  added_sugar_g NUMERIC
);

-- Enable Row Level Security (RLS)
ALTER TABLE meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE meal_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON users
  FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (auth.uid() = id);

-- RLS Policies for meals table
CREATE POLICY "Users can view own meals" ON meals
  FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Users can insert own meals" ON meals
  FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Users can update own meals" ON meals
  FOR UPDATE USING (auth.uid() = user_id OR user_id IS NULL);

-- RLS Policies for meal_items table
CREATE POLICY "Users can view own meal items" ON meal_items
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM meals
      WHERE meals.id = meal_items.meal_id
      AND (meals.user_id = auth.uid() OR meals.user_id IS NULL)
    )
  );

CREATE POLICY "Users can insert own meal items" ON meal_items
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM meals
      WHERE meals.id = meal_items.meal_id
      AND (meals.user_id = auth.uid() OR meals.user_id IS NULL)
    )
  );

-- Public read access to nutrition_facts and inferences (no RLS needed)
-- These tables contain reference data that all users should access

-- PREPROCESSING EXPERIMENTS (A/B testing for preprocessing strategies)
CREATE TABLE IF NOT EXISTS preprocessing_experiments (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  inference_id BIGINT REFERENCES inferences(id),
  strategy_name TEXT NOT NULL,              -- e.g., "adaptive", "aggressive", "minimal"
  quality_metrics JSONB NOT NULL,           -- brightness, variance, quality_score, etc.
  preprocessing_params JSONB NOT NULL,      -- contrast_factor, sharpness_factor, brightness_factor
  detection_accuracy NUMERIC,               -- can be updated later with user feedback
  user_rating INT CHECK (user_rating >= 1 AND user_rating <= 5)
);

-- USER FEEDBACK (for model improvement loop)
CREATE TABLE IF NOT EXISTS user_feedback (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  meal_id BIGINT REFERENCES meals(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id),

  -- Feedback types
  rating INT CHECK (rating >= 1 AND rating <= 5),  -- Overall satisfaction
  accuracy_rating INT CHECK (accuracy_rating >= 1 AND accuracy_rating <= 5),  -- How accurate was detection

  -- Correction data
  detected_items JSONB,                     -- What we detected
  corrected_items JSONB,                    -- What user said it actually was
  missing_items JSONB,                      -- Foods we missed
  incorrect_items JSONB,                    -- Foods we wrongly detected

  -- Additional context
  comments TEXT,
  cuisine_type TEXT,                        -- e.g., "italian", "chinese", "indian", etc.
  image_quality_issue BOOLEAN DEFAULT FALSE,
  portion_accuracy BOOLEAN                  -- Was portion estimate accurate
);

-- REGIONAL CUISINE MAPPINGS (extend synonym support)
CREATE TABLE IF NOT EXISTS regional_cuisine_mappings (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  cuisine_type TEXT NOT NULL,               -- e.g., "italian", "chinese", "mexican", "indian"
  model_label TEXT NOT NULL,                -- What the model detected
  canonical_name TEXT NOT NULL,             -- Maps to nutrition_facts.canonical_name
  confidence_boost NUMERIC DEFAULT 0,       -- Optional boost for region-specific detection
  UNIQUE(cuisine_type, model_label)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_meals_user_id ON meals(user_id);
CREATE INDEX IF NOT EXISTS idx_meals_created_at ON meals(created_at);
CREATE INDEX IF NOT EXISTS idx_meal_items_meal_id ON meal_items(meal_id);
CREATE INDEX IF NOT EXISTS idx_nutrition_facts_canonical_name ON nutrition_facts(canonical_name);
CREATE INDEX IF NOT EXISTS idx_inferences_created_at ON inferences(created_at);
CREATE INDEX IF NOT EXISTS idx_preprocessing_experiments_strategy ON preprocessing_experiments(strategy_name);
CREATE INDEX IF NOT EXISTS idx_preprocessing_experiments_inference ON preprocessing_experiments(inference_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_meal_id ON user_feedback(meal_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_created_at ON user_feedback(created_at);
CREATE INDEX IF NOT EXISTS idx_regional_cuisine_mappings_cuisine ON regional_cuisine_mappings(cuisine_type);

-- Enable RLS for new tables
ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_feedback
CREATE POLICY "Users can view own feedback" ON user_feedback
  FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Users can insert own feedback" ON user_feedback
  FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Users can update own feedback" ON user_feedback
  FOR UPDATE USING (auth.uid() = user_id OR user_id IS NULL);