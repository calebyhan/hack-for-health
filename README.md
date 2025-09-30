# Healthy Eating Helper

🍎 Photo → nutrition breakdown → health score

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-15+-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)

## Overview

**Healthy Eating Helper** is an AI-powered nutrition analysis web application that transforms food photography into actionable health insights. Simply upload a photo of your meal and instantly receive comprehensive nutritional analysis with personalized health scoring.

### Key Features

- 🔍 **Smart Food Detection**: AI-powered recognition of top 1-3 food items in any meal photo
- 📊 **Detailed Nutrition Analysis**: Complete macronutrient breakdown (carbs, protein, fat) and calorie estimation per item and total meal
- 🎯 **Health Score Algorithm**: Scientifically-based scoring system (0-100) that considers calories, saturated fat, sugar, fiber, and protein
- 💡 **Friendly Guidance**: Easy-to-understand recommendations for healthier eating choices
- 📱 **Responsive Design**: Seamless experience across desktop and mobile devices
- ⚡ **Real-time Processing**: Fast analysis powered by optimized AI models

## Tech Stack

- **Frontend**: Next.js 15+, React 18+, TailwindCSS, React Query
- **Backend**: FastAPI, Hugging Face Transformers
- **Database**: Supabase (PostgreSQL)
- **AI**: Food-focused image classifier with multi-label detection

## Project Structure

```
healthy-eating-helper/
├── README.md
├── NOTES.md
├── .gitignore
├── .env.example
├── web/                # Next.js + Tailwind app
│   ├── README.md
│   ├── .env.local.example
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── app/
│   │   ├── page.tsx
│   │   ├── api/analyze/route.ts
│   │   ├── globals.css
│   │   └── components/
│   │       ├── UploadCard.tsx
│   │       ├── ResultCard.tsx
│   │       └── MacroBars.tsx
│   └── lib/
│       └── supabaseClient.ts
├── api/                # FastAPI service
│   ├── README.md
│   ├── .env.example
│   ├── requirements.txt
│   ├── main.py
│   ├── Dockerfile
│   └── scripts/
│       └── preload_model.py
└── supabase/
    ├── schema.sql
    ├── seeds.sql
    └── README.md
```

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account

### Setup

1. **Clone and install dependencies**:
```bash
# Install web dependencies
cd web && npm install

# Install API dependencies
cd ../api && pip install -r requirements.txt
```

2. **Environment setup**:
```bash
# Copy environment templates
cp web/.env.local.example web/.env.local
cp api/.env.example api/.env

# Fill in your Supabase credentials in both files
```

3. **Database setup**:
- Create a Supabase project
- Run `supabase/schema.sql` in the SQL editor
- Run `supabase/seeds.sql` to populate nutrition facts

4. **Start development servers**:
```bash
# Terminal 1: Start API
cd api && uvicorn main:app --reload --port 8000

# Terminal 2: Start web app
cd web && npm run dev
```

5. **Test the app**:
- Open http://localhost:3000
- Upload a food image
- View nutrition analysis and health score

## Health Score Formula

The health score (0-100) is calculated as:

```
score = clamp(100
  - 0.02 * max(0, calories - 500)
  - 1.2 * sat_fat_g
  - 0.2 * added_sugar_g
  + 0.8 * fiber_g
  + 0.5 * protein_g, 0, 100)
```

Additional penalties apply for items in the caution list (soda, fries, etc.).

## API Endpoints

### POST `/analyze`
Upload food image for analysis
- **Request**: `multipart/form-data` with `image` field
- **Response**: JSON with detected foods, nutrition, and health score

### GET `/foods`
List known foods and their nutritional information

### GET `/health`
Service health check

## Deployment

### Web (Vercel)
```bash
cd web && vercel --prod
```

### API (Railway/Render)
```bash
cd api && docker build -t healthy-eating-api .
```

## Contributing

This is an educational project demonstrating:
- Computer vision for food recognition
- Nutritional analysis algorithms
- Modern web application architecture
- Full-stack development with AI integration

### Development Guidelines

1. **Code Quality**: Follow TypeScript/Python best practices
2. **Testing**: Add tests for new features
3. **Documentation**: Update README and inline docs
4. **Performance**: Optimize for mobile and slow connections

### Getting Involved

- 🐛 **Bug Reports**: Use GitHub Issues
- 💡 **Feature Requests**: Describe use cases and benefits
- 🔧 **Pull Requests**: Include tests and documentation
- 📖 **Documentation**: Help improve setup guides

## Acknowledgments

- **Hugging Face**: For providing pre-trained computer vision models
- **Supabase**: For managed PostgreSQL and real-time capabilities
- **Vercel/Next.js**: For excellent developer experience and deployment
- **Nutrition Data**: USDA FoodData Central and nutrition research

## Disclaimer

**Note**: This application provides educational estimates and should not be used as a substitute for professional medical or nutritional advice. Nutritional values are estimates based on standard databases and may vary from actual values. Always consult with healthcare professionals for personalized dietary guidance.

## License

MIT License - see [LICENSE](LICENSE) for details.