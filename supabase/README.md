# Supabase Setup

This folder contains the database schema and seed data for the Healthy Eating Helper project.

## Files

- `schema.sql` - Database tables and RLS policies
- `seeds.sql` - Initial nutrition facts data for common foods

## Setup Instructions

1. Create a new Supabase project at https://supabase.com
2. Navigate to the SQL Editor in your Supabase dashboard
3. Run `schema.sql` first to create tables and policies
4. Run `seeds.sql` to populate nutrition facts with common foods
5. Copy your project URL and keys to the environment files

## Tables Created

- `users` - User accounts (optional for MVP)
- `nutrition_facts` - Canonical nutritional information per food item
- `inferences` - Raw AI model outputs for debugging
- `meals` - User meal submissions with total nutrition
- `meal_items` - Individual food items detected in each meal

## Row Level Security

RLS is enabled on user-facing tables with policies that ensure users can only access their own data when authenticated.