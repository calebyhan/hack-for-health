# Healthy Eating Helper Web App

Next.js frontend for the Healthy Eating Helper project.

## Features

- 📷 Drag-and-drop food image upload
- 🤖 AI-powered food detection and analysis
- 📊 Nutrition breakdown with macro visualizations
- 🎯 Health score (0-100) with traffic-light indicators
- 📱 Responsive design with Tailwind CSS
- ⚡ React Query for efficient data fetching (no useEffect)

## Tech Stack

- Next.js 14+ (App Router)
- React 18+
- TypeScript
- Tailwind CSS 3+
- React Query (TanStack Query)
- React Dropzone for file uploads
- Supabase client

## Setup

1. **Install dependencies**:
```bash
npm install
```

2. **Environment setup**:
```bash
cp .env.local.example .env.local
# Edit .env.local with your API URL and Supabase credentials
```

3. **Start development server**:
```bash
npm run dev
```

4. **Build for production**:
```bash
npm run build
npm start
```

## Project Structure

```
web/
├── app/
│   ├── page.tsx           # Main upload page
│   ├── api/analyze/route.ts # Optional proxy route
│   ├── globals.css        # Global styles
│   └── components/
│       ├── UploadCard.tsx # File upload component
│       ├── ResultCard.tsx # Analysis results display
│       └── MacroBars.tsx  # Nutrition visualization
├── lib/
│   └── supabaseClient.ts  # Supabase configuration
├── package.json
├── next.config.js
└── tailwind.config.js
```

## Components

### UploadCard
- Drag-and-drop image upload
- File validation (type, size)
- Image preview
- Upload progress indication

### ResultCard
- Health score with color-coded indicator
- Detected foods list with confidence scores
- Health tips and recommendations

### MacroBars
- Visual macronutrient breakdown
- Calorie, protein, carbs, fat display
- Responsive bar charts

## Environment Variables

Create `.env.local` with:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase Configuration (for future auth/features)
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## Deployment

Deploy to Vercel:

```bash
vercel --prod
```

The app will automatically deploy from your git repository.