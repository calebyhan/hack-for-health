'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Utensils, Brain, TrendingUp, Github } from 'lucide-react'
import UploadCard from './components/UploadCard'
import ResultCard from './components/ResultCard'

// Types based on API contract from design.md
interface NutritionInfo {
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
  fiber_g?: number
  sat_fat_g?: number
  added_sugar_g?: number
}

interface FoodItem {
  label: string
  confidence: number
  servings: number
  nutrition: NutritionInfo
}

interface AnalysisResult {
  total_calories: number
  health_score: number
  items: FoodItem[]
  tips: string[]
}

// API configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null)

  // Mutation for food analysis using React Query (no useEffect as specified)
  const analyzeFood = useMutation({
    mutationFn: async (file: File): Promise<AnalysisResult> => {
      const formData = new FormData()
      formData.append('image', file)

      // Try direct API call first, fallback to Next.js API route if CORS issues
      let response: Response
      try {
        response = await fetch(`${API_URL}/analyze`, {
          method: 'POST',
          body: formData,
        })
      } catch (error) {
        // Fallback to Next.js API route for CORS issues
        console.warn('Direct API call failed, using Next.js proxy:', error)
        response = await fetch('/api/analyze', {
          method: 'POST',
          body: formData,
        })
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
        throw new Error(errorData.error || errorData.detail || `HTTP ${response.status}`)
      }

      return response.json()
    },
    onSuccess: (data) => {
      setResult(data)
    },
    onError: (error) => {
      console.error('Analysis failed:', error)
      // Error handling is done by the mutation state
    },
  })

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
    setResult(null)

    // Create preview URL for the uploaded image
    const previewUrl = URL.createObjectURL(file)
    setImagePreviewUrl(previewUrl)

    analyzeFood.mutate(file)
  }

  const handleReset = () => {
    setResult(null)
    setSelectedFile(null)

    // Clean up preview URL
    if (imagePreviewUrl) {
      URL.revokeObjectURL(imagePreviewUrl)
      setImagePreviewUrl(null)
    }

    analyzeFood.reset()
  }

  return (
    <main className="min-h-screen">
      {/* Header */}
      <header className="relative z-10 px-4 py-8">
        <div className="max-w-6xl mx-auto text-center">
          <div className="flex items-center justify-center mb-6">
            <div className="bg-primary-600 rounded-2xl p-4 shadow-lg">
              <Utensils className="w-8 h-8 text-white" />
            </div>
          </div>

          <h1 className="text-4xl md:text-6xl font-bold text-slate-900 mb-4">
            <span className="gradient-text">Healthy Eating</span> Helper
          </h1>

          <p className="text-lg md:text-xl text-slate-600 mb-8 max-w-3xl mx-auto text-balance">
            Photo → nutrition breakdown → health score. Get instant AI-powered nutrition analysis
            for your meals and make healthier choices.
          </p>

          {/* Feature highlights */}
          <div className="flex flex-wrap justify-center gap-6 mb-8">
            <div className="flex items-center space-x-2 text-slate-700">
              <Brain className="w-5 h-5 text-primary-600" />
              <span className="text-sm font-medium">AI Food Detection</span>
            </div>
            <div className="flex items-center space-x-2 text-slate-700">
              <TrendingUp className="w-5 h-5 text-success-600" />
              <span className="text-sm font-medium">Health Score 0-100</span>
            </div>
            <div className="flex items-center space-x-2 text-slate-700">
              <Utensils className="w-5 h-5 text-warning-600" />
              <span className="text-sm font-medium">Macro Breakdown</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="px-4 pb-12">
        <div className="max-w-6xl mx-auto">
          {!result ? (
            <div className="space-y-8">
              <UploadCard
                onFileSelect={handleFileSelect}
                isUploading={analyzeFood.isPending}
                disabled={analyzeFood.isPending}
              />

              {/* Error display */}
              {analyzeFood.isError && (
                <div className="max-w-2xl mx-auto">
                  <div className="card bg-danger-50 border-danger-200">
                    <div className="text-center">
                      <h3 className="text-lg font-semibold text-danger-800 mb-2">
                        Analysis Failed
                      </h3>
                      <p className="text-danger-700 mb-4">
                        {analyzeFood.error?.message || 'Unable to analyze the image. Please try again.'}
                      </p>
                      <button
                        onClick={handleReset}
                        className="btn-secondary"
                      >
                        Try Again
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Loading state with file preview */}
              {analyzeFood.isPending && selectedFile && (
                <div className="max-w-2xl mx-auto">
                  <div className="card text-center">
                    <div className="animate-pulse">
                      <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Brain className="w-8 h-8 text-primary-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-slate-800 mb-2">
                        Analyzing your meal...
                      </h3>
                      <p className="text-slate-600 mb-4">
                        Our AI is identifying foods and calculating nutrition information
                      </p>
                      <div className="w-full bg-slate-200 rounded-full h-2">
                        <div className="bg-primary-600 h-2 rounded-full animate-pulse-slow" style={{ width: '70%' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <ResultCard
              result={result}
              imageUrl={imagePreviewUrl}
              onReset={handleReset}
              className="animate-fade-in"
            />
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white/50 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-6 mb-4">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-900 transition-colors"
              >
                <Github className="w-4 h-4" />
                <span className="text-sm">View Source</span>
              </a>
            </div>

            <p className="text-sm text-slate-500 mb-2">
              Built with Next.js, FastAPI, and Hugging Face Transformers
            </p>

            <p className="text-xs text-slate-400 max-w-2xl mx-auto">
              This tool provides educational nutrition estimates based on AI food recognition.
              Results may not reflect exact portions or preparation methods.
              <strong> This is not medical advice.</strong> Consult healthcare professionals for dietary guidance.
            </p>
          </div>
        </div>
      </footer>
    </main>
  )
}