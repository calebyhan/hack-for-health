'use client'

import { useMemo } from 'react'

interface MacroData {
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
  fiber_g?: number
}

interface MacroBarsProps {
  nutrition: MacroData
  showDetails?: boolean
  className?: string
}

export default function MacroBars({ nutrition, showDetails = true, className = '' }: MacroBarsProps) {
  const macros = useMemo(() => {
    const { calories, protein_g, carbs_g, fat_g, fiber_g = 0 } = nutrition

    // Calculate calories from macros (for percentage calculation)
    const proteinCals = protein_g * 4
    const carbsCals = carbs_g * 4
    const fatCals = fat_g * 9
    const totalMacroCals = proteinCals + carbsCals + fatCals

    // Calculate percentages (handle division by zero)
    const proteinPercent = totalMacroCals > 0 ? (proteinCals / totalMacroCals) * 100 : 0
    const carbsPercent = totalMacroCals > 0 ? (carbsCals / totalMacroCals) * 100 : 0
    const fatPercent = totalMacroCals > 0 ? (fatCals / totalMacroCals) * 100 : 0

    return [
      {
        name: 'Calories',
        value: calories,
        unit: 'kcal',
        color: 'macro-bar-calories',
        percentage: 100, // Calories is the total, so always 100%
        bgColor: 'bg-primary-100',
        textColor: 'text-primary-700'
      },
      {
        name: 'Protein',
        value: protein_g,
        unit: 'g',
        color: 'macro-bar-protein',
        percentage: proteinPercent,
        bgColor: 'bg-success-100',
        textColor: 'text-success-700'
      },
      {
        name: 'Carbs',
        value: carbs_g,
        unit: 'g',
        color: 'macro-bar-carbs',
        percentage: carbsPercent,
        bgColor: 'bg-warning-100',
        textColor: 'text-warning-700'
      },
      {
        name: 'Fat',
        value: fat_g,
        unit: 'g',
        color: 'macro-bar-fat',
        percentage: fatPercent,
        bgColor: 'bg-danger-100',
        textColor: 'text-danger-700'
      }
    ]
  }, [nutrition])

  const fiberDisplay = useMemo(() => {
    if (!nutrition.fiber_g || nutrition.fiber_g === 0) return null
    return {
      name: 'Fiber',
      value: nutrition.fiber_g,
      unit: 'g',
      bgColor: 'bg-emerald-100',
      textColor: 'text-emerald-700'
    }
  }, [nutrition.fiber_g])

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900">Nutrition Breakdown</h3>
        <div className="text-sm text-slate-500">
          Total: {nutrition.calories} calories
        </div>
      </div>

      <div className="space-y-3">
        {macros.map((macro, index) => (
          <div key={macro.name} className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700">{macro.name}</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-semibold text-slate-900">
                  {Math.round(macro.value)} {macro.unit}
                </span>
                {showDetails && macro.name !== 'Calories' && (
                  <span className="text-xs text-slate-500">
                    ({Math.round(macro.percentage)}%)
                  </span>
                )}
              </div>
            </div>

            <div className="macro-bar">
              <div
                className={`macro-bar-fill ${macro.color}`}
                style={{
                  width: macro.name === 'Calories'
                    ? '100%'
                    : `${Math.min(macro.percentage, 100)}%`
                }}
              />
            </div>
          </div>
        ))}

        {/* Fiber display (if available) */}
        {fiberDisplay && showDetails && (
          <div className="pt-2 border-t border-slate-200">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700">{fiberDisplay.name}</span>
              <span className="text-sm font-semibold text-slate-900">
                {Math.round(fiberDisplay.value)} {fiberDisplay.unit}
              </span>
            </div>
          </div>
        )}
      </div>

      {showDetails && (
        <div className="pt-3 border-t border-slate-200">
          <div className="grid grid-cols-2 gap-4 text-xs text-slate-600">
            <div>
              <span className="font-medium">Protein:</span> {Math.round(nutrition.protein_g * 4)} cal
            </div>
            <div>
              <span className="font-medium">Carbs:</span> {Math.round(nutrition.carbs_g * 4)} cal
            </div>
            <div>
              <span className="font-medium">Fat:</span> {Math.round(nutrition.fat_g * 9)} cal
            </div>
            {fiberDisplay && (
              <div>
                <span className="font-medium">Fiber:</span> {Math.round(fiberDisplay.value)}g
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}