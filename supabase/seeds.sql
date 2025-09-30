-- Seed data for nutrition_facts table
-- Run this after schema.sql to populate common foods

INSERT INTO nutrition_facts (canonical_name, calories, protein_g, carbs_g, fat_g, fiber_g, sat_fat_g, added_sugar_g) VALUES
-- Fruits
('apple', 95, 0.5, 25, 0.3, 4.4, 0.1, 19),
('banana', 105, 1.3, 27, 0.4, 3.1, 0.1, 14),
('orange', 62, 1.2, 15, 0.2, 3.1, 0.0, 12),
('grapes', 104, 1.1, 27, 0.2, 1.4, 0.1, 23),

-- Vegetables & Salads
('salad', 150, 4, 10, 10, 3, 2, 1),
('broccoli', 55, 4.0, 11, 0.6, 5.1, 0.1, 0),
('carrots', 50, 1.0, 12, 0.3, 3.4, 0.1, 6),
('spinach', 23, 2.9, 3.6, 0.4, 2.2, 0.1, 0),

-- Proteins
('chicken breast', 231, 43.5, 0, 5.0, 0, 1.4, 0),
('salmon', 208, 30.5, 0, 8.8, 0, 1.8, 0),
('beef', 250, 35, 0, 11, 0, 4.5, 0),
('eggs', 155, 13, 1.1, 11, 0, 3.3, 0),

-- Grains & Starches
('rice', 205, 4.3, 45, 0.4, 0.6, 0.1, 0),
('bread', 265, 9, 49, 3.2, 2.7, 0.6, 3),
('pasta', 220, 8, 44, 1.3, 2.5, 0.3, 1),
('potato', 161, 4.3, 37, 0.2, 2.3, 0.1, 0),

-- Common Restaurant/Fast Foods
('pizza', 285, 12, 36, 10, 2, 4, 2),
('burger', 540, 31, 41, 27, 3, 10, 5),
('french fries', 365, 4, 48, 17, 4, 3, 0),
('sandwich', 300, 15, 35, 12, 3, 3, 4),

-- Beverages & Snacks
('soda', 150, 0, 39, 0, 0, 0, 39),
('coffee', 5, 0.3, 1, 0, 0, 0, 0),
('milk', 150, 8, 12, 8, 0, 5, 12),

-- Generic fallbacks for unknown foods
('snack', 200, 3, 25, 8, 2, 2, 10),
('dessert', 350, 4, 45, 15, 2, 8, 25),
('soup', 120, 6, 15, 4, 2, 1, 3)

ON CONFLICT (canonical_name) DO NOTHING;