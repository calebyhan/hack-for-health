-- Regional Cuisine Mappings Seeds
-- Extends food detection for regional cuisines (Italian, Chinese, Mexican, Indian, Japanese, Middle Eastern)

-- Italian Cuisine
INSERT INTO regional_cuisine_mappings (cuisine_type, model_label, canonical_name, confidence_boost) VALUES
('italian', 'pasta', 'pasta', 0.1),
('italian', 'spaghetti', 'pasta', 0.1),
('italian', 'penne', 'pasta', 0.1),
('italian', 'linguine', 'pasta', 0.1),
('italian', 'fettuccine', 'pasta', 0.1),
('italian', 'lasagna', 'lasagna', 0.1),
('italian', 'risotto', 'risotto', 0.1),
('italian', 'pizza', 'pizza', 0.1),
('italian', 'pizza margherita', 'pizza', 0.1),
('italian', 'calzone', 'pizza', 0.05),
('italian', 'bruschetta', 'bruschetta', 0.1),
('italian', 'tiramisu', 'dessert', 0.05),
('italian', 'gelato', 'ice cream', 0.05),
('italian', 'mozzarella', 'cheese', 0.05),
('italian', 'parmesan', 'cheese', 0.05);

-- Chinese Cuisine
INSERT INTO regional_cuisine_mappings (cuisine_type, model_label, canonical_name, confidence_boost) VALUES
('chinese', 'fried rice', 'rice', 0.1),
('chinese', 'steamed rice', 'rice', 0.1),
('chinese', 'noodles', 'noodles', 0.1),
('chinese', 'lo mein', 'noodles', 0.1),
('chinese', 'chow mein', 'noodles', 0.1),
('chinese', 'dumpling', 'dumplings', 0.1),
('chinese', 'dim sum', 'dumplings', 0.1),
('chinese', 'spring roll', 'spring roll', 0.1),
('chinese', 'wonton', 'dumplings', 0.05),
('chinese', 'kung pao chicken', 'chicken breast', 0.05),
('chinese', 'sweet and sour', 'chicken breast', 0.05),
('chinese', 'peking duck', 'chicken breast', 0.05),
('chinese', 'bok choy', 'vegetables', 0.05),
('chinese', 'tofu', 'tofu', 0.1);

-- Mexican Cuisine
INSERT INTO regional_cuisine_mappings (cuisine_type, model_label, canonical_name, confidence_boost) VALUES
('mexican', 'taco', 'taco', 0.1),
('mexican', 'burrito', 'burrito', 0.1),
('mexican', 'quesadilla', 'quesadilla', 0.1),
('mexican', 'enchilada', 'enchilada', 0.1),
('mexican', 'nachos', 'nachos', 0.1),
('mexican', 'tortilla', 'tortilla', 0.1),
('mexican', 'guacamole', 'guacamole', 0.1),
('mexican', 'salsa', 'salsa', 0.1),
('mexican', 'fajita', 'fajitas', 0.1),
('mexican', 'tamale', 'tamale', 0.1),
('mexican', 'refried beans', 'beans', 0.05),
('mexican', 'black beans', 'beans', 0.05),
('mexican', 'rice and beans', 'rice', 0.05),
('mexican', 'churro', 'dessert', 0.05);

-- Indian Cuisine
INSERT INTO regional_cuisine_mappings (cuisine_type, model_label, canonical_name, confidence_boost) VALUES
('indian', 'curry', 'curry', 0.1),
('indian', 'chicken curry', 'curry', 0.1),
('indian', 'tikka masala', 'curry', 0.1),
('indian', 'butter chicken', 'curry', 0.1),
('indian', 'biryani', 'rice', 0.1),
('indian', 'naan', 'naan', 0.1),
('indian', 'roti', 'naan', 0.05),
('indian', 'chapati', 'naan', 0.05),
('indian', 'samosa', 'samosa', 0.1),
('indian', 'pakora', 'samosa', 0.05),
('indian', 'dal', 'dal', 0.1),
('indian', 'lentils', 'dal', 0.05),
('indian', 'paneer', 'paneer', 0.1),
('indian', 'tandoori chicken', 'chicken breast', 0.05),
('indian', 'raita', 'yogurt', 0.05);

-- Japanese Cuisine
INSERT INTO regional_cuisine_mappings (cuisine_type, model_label, canonical_name, confidence_boost) VALUES
('japanese', 'sushi', 'sushi', 0.1),
('japanese', 'sashimi', 'sushi', 0.05),
('japanese', 'maki', 'sushi', 0.05),
('japanese', 'nigiri', 'sushi', 0.05),
('japanese', 'ramen', 'ramen', 0.1),
('japanese', 'udon', 'noodles', 0.1),
('japanese', 'soba', 'noodles', 0.1),
('japanese', 'tempura', 'tempura', 0.1),
('japanese', 'teriyaki', 'chicken breast', 0.05),
('japanese', 'edamame', 'edamame', 0.1),
('japanese', 'miso soup', 'soup', 0.05),
('japanese', 'onigiri', 'rice', 0.05),
('japanese', 'gyoza', 'dumplings', 0.05),
('japanese', 'tonkatsu', 'chicken breast', 0.05),
('japanese', 'bento', 'rice', 0.05);

-- Middle Eastern Cuisine
INSERT INTO regional_cuisine_mappings (cuisine_type, model_label, canonical_name, confidence_boost) VALUES
('middle_eastern', 'hummus', 'hummus', 0.1),
('middle_eastern', 'falafel', 'falafel', 0.1),
('middle_eastern', 'shawarma', 'shawarma', 0.1),
('middle_eastern', 'kebab', 'chicken breast', 0.05),
('middle_eastern', 'pita', 'pita', 0.1),
('middle_eastern', 'tabbouleh', 'salad', 0.05),
('middle_eastern', 'baba ganoush', 'hummus', 0.05),
('middle_eastern', 'couscous', 'rice', 0.05),
('middle_eastern', 'baklava', 'dessert', 0.05),
('middle_eastern', 'tahini', 'sauce', 0.05);

-- Add corresponding nutrition facts for new regional foods
INSERT INTO nutrition_facts (canonical_name, calories, protein_g, carbs_g, fat_g, fiber_g, sat_fat_g, added_sugar_g) VALUES
-- Italian
('lasagna', 356, 18.5, 30.5, 17.5, 2.5, 8.5, 3.0),
('risotto', 205, 4.5, 38.0, 4.5, 1.0, 2.5, 1.0),
('bruschetta', 180, 5.0, 28.0, 6.0, 2.0, 1.5, 2.0),
('cheese', 110, 7.0, 1.0, 9.0, 0, 5.5, 0),
('ice cream', 207, 3.5, 24.0, 11.0, 0.7, 7.0, 21.0),

-- Chinese
('noodles', 221, 7.0, 43.0, 2.5, 2.0, 0.5, 0.5),
('dumplings', 187, 8.5, 24.0, 6.5, 1.5, 2.0, 1.0),
('spring roll', 163, 5.5, 17.0, 8.5, 1.8, 1.5, 1.5),
('vegetables', 65, 3.0, 13.0, 0.5, 4.0, 0.1, 5.0),
('tofu', 144, 15.8, 3.5, 8.7, 2.3, 1.3, 0),

-- Mexican
('taco', 226, 11.5, 20.0, 11.5, 3.5, 4.5, 1.0),
('burrito', 506, 22.0, 66.0, 17.0, 8.0, 7.5, 2.0),
('quesadilla', 412, 18.5, 39.5, 20.0, 3.0, 9.5, 1.5),
('enchilada', 323, 14.5, 32.0, 15.5, 4.5, 7.0, 2.5),
('nachos', 346, 9.5, 36.0, 18.5, 3.5, 6.5, 1.0),
('tortilla', 159, 4.3, 27.0, 3.6, 1.6, 0.7, 0.5),
('guacamole', 160, 2.0, 9.0, 14.7, 6.7, 2.1, 0.7),
('salsa', 36, 1.5, 8.0, 0.2, 2.0, 0, 4.5),
('fajitas', 345, 28.0, 32.0, 11.0, 5.0, 3.5, 3.0),
('tamale', 285, 7.5, 29.0, 15.5, 4.5, 5.5, 1.0),
('beans', 127, 7.7, 22.5, 0.5, 6.2, 0.1, 0.4),

-- Indian
('curry', 198, 14.5, 11.5, 11.0, 3.5, 5.5, 4.0),
('naan', 262, 7.6, 45.5, 5.2, 2.0, 1.3, 3.5),
('samosa', 262, 5.5, 28.0, 14.5, 3.5, 2.5, 1.0),
('dal', 116, 9.0, 20.0, 0.4, 8.0, 0.1, 1.5),
('paneer', 265, 18.3, 3.6, 20.8, 0, 13.0, 0),
('yogurt', 59, 3.5, 4.7, 3.3, 0, 2.1, 4.7),

-- Japanese
('sushi', 143, 6.0, 28.0, 1.0, 1.0, 0.2, 3.5),
('ramen', 436, 20.0, 65.0, 10.5, 3.0, 3.5, 2.0),
('tempura', 251, 9.5, 24.0, 13.5, 1.5, 2.0, 1.0),
('edamame', 121, 11.2, 10.0, 5.2, 5.2, 0.6, 2.0),
('soup', 40, 2.8, 5.0, 1.2, 1.0, 0.3, 1.5),

-- Middle Eastern
('hummus', 166, 4.9, 14.3, 9.6, 4.0, 1.2, 0.4),
('falafel', 333, 13.3, 31.8, 17.8, 6.0, 2.3, 1.5),
('shawarma', 429, 28.5, 35.0, 19.5, 3.5, 5.5, 3.0),
('pita', 165, 5.5, 33.4, 0.7, 1.3, 0.1, 0.8),
('sauce', 89, 0.8, 3.6, 8.1, 0.5, 1.2, 0.3),
('dessert', 292, 4.2, 42.0, 12.5, 1.5, 3.5, 28.0)

ON CONFLICT (canonical_name) DO NOTHING;