/**
 * Next.js API route for food analysis
 * This is an optional proxy route that forwards requests to the FastAPI backend
 * Can be used to avoid CORS issues or add additional processing
 */

import { NextRequest, NextResponse } from 'next/server'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function POST(request: NextRequest) {
  try {
    // Get the form data from the request
    const formData = await request.formData()
    const image = formData.get('image') as File

    if (!image) {
      return NextResponse.json(
        { error: 'No image file provided' },
        { status: 400 }
      )
    }

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
    if (!allowedTypes.includes(image.type)) {
      return NextResponse.json(
        { error: `Unsupported file type: ${image.type}. Supported: JPEG, PNG, WebP` },
        { status: 400 }
      )
    }

    // Validate file size (8MB limit)
    const maxSize = 8 * 1024 * 1024 // 8MB
    if (image.size > maxSize) {
      return NextResponse.json(
        { error: `File too large: ${image.size} bytes. Maximum size: ${maxSize} bytes` },
        { status: 400 }
      )
    }

    // Create new FormData for the backend request
    const backendFormData = new FormData()
    backendFormData.append('image', image)

    // Forward the request to the FastAPI backend
    const response = await fetch(`${API_URL}/analyze`, {
      method: 'POST',
      body: backendFormData,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
      return NextResponse.json(
        { error: errorData.detail || errorData.error || 'Analysis failed' },
        { status: response.status }
      )
    }

    const result = await response.json()

    // Return the result from the backend
    return NextResponse.json(result, {
      headers: {
        'Cache-Control': 'no-store, max-age=0',
      },
    })

  } catch (error) {
    console.error('API route error:', error)

    if (error instanceof Error) {
      if (error.message.includes('fetch')) {
        return NextResponse.json(
          { error: 'Unable to connect to analysis service. Please ensure the API is running.' },
          { status: 503 }
        )
      }
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function GET() {
  // Return API information
  return NextResponse.json({
    message: 'Food Analysis API',
    endpoints: {
      POST: 'Upload food image for analysis'
    },
    backend: API_URL
  })
}

// Handle OPTIONS requests for CORS
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  })
}