'use client'

import { useMemo, useState, useCallback } from 'react'
import { Lightbulb, RotateCcw, TrendingUp, Award, ImageIcon, Minus, Plus } from 'lucide-react'
import Image from 'next/image'
import MacroBars from './MacroBars'

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

interface ResultCardProps {
  result: AnalysisResult
  imageUrl: string | null
  onReset: () => void
  className?: string
}

export default function ResultCard({ result, imageUrl, onReset, className = '' }: ResultCardProps) {
  // State for adjustable servings per item (per design.md line 59: "UI can later allow user to tweak")
  const [servingAdjustments, setServingAdjustments] = useState<Record<number, number>>(() => {
    // Initialize with original servings from API
    const initial: Record<number, number> = {}
    result.items.forEach((_, index) => {
      initial[index] = result.items[index].servings
    })
    return initial
  })

  // Update serving size for a specific item
  const updateServing = useCallback((itemIndex: number, newServing: number) => {
    // Clamp between 0.25 and 5 servings
    const clamped = Math.max(0.25, Math.min(5, newServing))
    setServingAdjustments(prev => ({
      ...prev,
      [itemIndex]: clamped
    }))
  }, [])

  // Recalculate nutrition based on adjusted servings (per design.md health score formula)
  const adjustedNutrition = useMemo(() => {
    return result.items.reduce(
      (total, item, index) => {
        const servingMultiplier = servingAdjustments[index] || item.servings
        return {
          calories: total.calories + (item.nutrition.calories * servingMultiplier),
          protein_g: total.protein_g + (item.nutrition.protein_g * servingMultiplier),
          carbs_g: total.carbs_g + (item.nutrition.carbs_g * servingMultiplier),
          fat_g: total.fat_g + (item.nutrition.fat_g * servingMultiplier),
          fiber_g: total.fiber_g + ((item.nutrition.fiber_g || 0) * servingMultiplier),
          sat_fat_g: total.sat_fat_g + ((item.nutrition.sat_fat_g || 0) * servingMultiplier),
          added_sugar_g: total.added_sugar_g + ((item.nutrition.added_sugar_g || 0) * servingMultiplier)
        }
      },
      { calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0, fiber_g: 0, sat_fat_g: 0, added_sugar_g: 0 }
    )
  }, [result.items, servingAdjustments])

  // Recalculate health score based on adjusted nutrition (design.md formula)
  const adjustedHealthScore = useMemo(() => {
    const { calories, sat_fat_g, added_sugar_g, fiber_g, protein_g } = adjustedNutrition

    // Apply exact formula from design.md line 65-70
    let score = 100
      - 0.02 * Math.max(0, calories - 500)
      - 1.2 * sat_fat_g
      - 0.2 * added_sugar_g
      + 0.8 * fiber_g
      + 0.5 * protein_g

    // Apply caution food penalties
    result.items.forEach((item, index) => {
      const servingMultiplier = servingAdjustments[index] || item.servings
      const label = item.label.toLowerCase()

      // Penalties scale with serving size
      if (label.includes('soda') || label.includes('cola')) score -= 10 * servingMultiplier
      else if (label.includes('fries') || label.includes('chips')) score -= 8 * servingMultiplier
      else if (label.includes('burger')) score -= 5 * servingMultiplier
      else if (label.includes('pizza')) score -= 3 * servingMultiplier
      else if (label.includes('dessert')) score -= 7 * servingMultiplier
    })

    // Clamp to 0-100
    return Math.max(0, Math.min(100, Math.round(score)))
  }, [adjustedNutrition, result.items, servingAdjustments])

  const healthScoreConfig = useMemo(() => {
    // Use adjusted score instead of original
    const score = adjustedHealthScore

    if (score >= 80) {
      return {
        label: 'Excellent',
        color: 'health-score-excellent',
        icon: Award,
        bgColor: 'bg-success-500',
        description: 'Great nutritional balance!'
      }
    } else if (score >= 65) {
      return {
        label: 'Good',
        color: 'health-score-good',
        icon: TrendingUp,
        bgColor: 'bg-success-400',
        description: 'Solid nutrition choices'
      }
    } else if (score >= 45) {
      return {
        label: 'Moderate',
        color: 'health-score-moderate',
        icon: TrendingUp,
        bgColor: 'bg-warning-500',
        description: 'Room for improvement'
      }
    } else {
      return {
        label: 'Poor',
        color: 'health-score-poor',
        icon: TrendingUp,
        bgColor: 'bg-danger-500',
        description: 'Consider healthier options'
      }
    }
  }, [adjustedHealthScore])

  const confidenceLevel = (confidence: number) => {
    if (confidence >= 0.8) return { label: 'High', style: 'confidence-high' }
    if (confidence >= 0.5) return { label: 'Medium', style: 'confidence-medium' }
    return { label: 'Low', style: 'confidence-low' }
  }

  const totalNutrition = adjustedNutrition

  const IconComponent = healthScoreConfig.icon

  return (
    <div className={`w-full max-w-4xl mx-auto space-y-6 ${className}`}>
      {/* Uploaded Image Display */}
      {imageUrl && (
        <div className="card card-hover animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900 flex items-center">
              <ImageIcon className="w-5 h-5 text-primary-600 mr-2" />
              Your Meal
            </h3>
          </div>
          <div className="relative w-full h-64 md:h-80 bg-slate-100 rounded-lg overflow-hidden">
            <Image
              src={imageUrl}
              alt="Uploaded meal"
              fill
              className="object-contain"
              priority
            />
          </div>
        </div>
      )}

      {/* Health Score Header */}
      <div className="card card-hover animate-fade-in">
        <div className="text-center">
          <div className="flex items-center justify-center mb-4">
            <div className={`relative w-24 h-24 rounded-full ${healthScoreConfig.bgColor} flex items-center justify-center`}>
              <span className="text-2xl font-bold text-white">{result.health_score}</span>
              <div className="absolute -top-2 -right-2 bg-white rounded-full p-1">
                <IconComponent className="w-4 h-4 text-slate-600" />
              </div>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-slate-900 mb-1">
            Health Score: {adjustedHealthScore}/100
          </h2>
          <p className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${healthScoreConfig.color}`}>
            {healthScoreConfig.label} - {healthScoreConfig.description}
          </p>

          <div className="mt-4 text-slate-600">
            <p className="text-lg font-medium">{Math.round(adjustedNutrition.calories)} total calories</p>
            {adjustedHealthScore !== result.health_score && (
              <p className="text-xs text-slate-500 mt-1">
                Adjusted from original: {result.health_score}/100 ({result.total_calories} cal)
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Detected Foods */}
        <div className="card animate-fade-in">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
            <span className="w-2 h-2 bg-primary-500 rounded-full mr-2"></span>
            Detected Foods
          </h3>

          <div className="space-y-3">
            {result.items.map((item, index) => {
              const conf = confidenceLevel(item.confidence)
              const currentServing = servingAdjustments[index] || item.servings
              const adjustedCals = Math.round(item.nutrition.calories * currentServing)
              const adjustedProtein = Math.round(item.nutrition.protein_g * currentServing)
              const adjustedCarbs = Math.round(item.nutrition.carbs_g * currentServing)
              const adjustedFat = Math.round(item.nutrition.fat_g * currentServing)

              return (
                <div key={index} className="border border-slate-200 rounded-lg p-4 hover:bg-slate-50 transition-colors">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-slate-900 capitalize">
                      {item.label}
                    </h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${conf.style}`}>
                      {conf.label} ({Math.round(item.confidence * 100)}%)
                    </span>
                  </div>

                  {/* Portion Size Controls */}
                  <div className="mb-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-slate-700">Serving Size</span>
                      <span className="text-sm font-semibold text-primary-600">
                        {currentServing.toFixed(2)}x
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => updateServing(index, currentServing - 0.25)}
                        className="p-1.5 rounded-lg bg-white border border-slate-300 hover:bg-slate-100 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                        disabled={currentServing <= 0.25}
                        aria-label="Decrease serving"
                      >
                        <Minus className="w-4 h-4 text-slate-600" />
                      </button>
                      <input
                        type="range"
                        min="0.25"
                        max="5"
                        step="0.25"
                        value={currentServing}
                        onChange={(e) => updateServing(index, parseFloat(e.target.value))}
                        className="flex-1 h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                        aria-label={`Adjust ${item.label} serving size`}
                      />
                      <button
                        onClick={() => updateServing(index, currentServing + 0.25)}
                        className="p-1.5 rounded-lg bg-white border border-slate-300 hover:bg-slate-100 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                        disabled={currentServing >= 5}
                        aria-label="Increase serving"
                      >
                        <Plus className="w-4 h-4 text-slate-600" />
                      </button>
                    </div>
                    <div className="flex justify-between mt-2 text-xs text-slate-500">
                      <span>0.25x</span>
                      <span>5x</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-sm text-slate-600">
                    <div>
                      <span className="font-medium">Calories:</span> {adjustedCals}
                    </div>
                    <div>
                      <span className="font-medium">Protein:</span> {adjustedProtein}g
                    </div>
                    <div>
                      <span className="font-medium">Carbs:</span> {adjustedCarbs}g
                    </div>
                    <div>
                      <span className="font-medium">Fat:</span> {adjustedFat}g
                    </div>
                  </div>

                  {currentServing !== item.servings && (
                    <div className="mt-2 text-xs text-primary-600">
                      Original: {item.servings}x serving ({item.nutrition.calories} cal)
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Nutrition Breakdown */}
        <div className="card animate-fade-in">
          <MacroBars nutrition={totalNutrition} showDetails={true} />
        </div>
      </div>

      {/* Health Tips */}
      {result.tips && result.tips.length > 0 && (
        <div className="card animate-fade-in">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
            <Lightbulb className="w-5 h-5 text-warning-500 mr-2" />
            Health Tips
          </h3>

          <div className="space-y-2">
            {result.tips.map((tip, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-slate-700 leading-relaxed">{tip}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <button
          onClick={onReset}
          className="btn-secondary flex items-center justify-center space-x-2"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Analyze Another Photo</span>
        </button>
      </div>

      {/* Disclaimer */}
      <div className="text-center">
        <p className="text-xs text-slate-500 max-w-2xl mx-auto leading-relaxed">
          <strong>Disclaimer:</strong> This analysis provides educational nutritional estimates based on AI food recognition.
          Results may not reflect exact portion sizes or preparation methods. This is not medical advice.
          Consult healthcare professionals for dietary guidance.
        </p>
      </div>
    </div>
  )
}