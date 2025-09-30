'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Camera, X, AlertCircle } from 'lucide-react'
import Image from 'next/image'

interface UploadCardProps {
  onFileSelect: (file: File) => void
  isUploading?: boolean
  disabled?: boolean
}

export default function UploadCard({ onFileSelect, isUploading = false, disabled = false }: UploadCardProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null)

    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0]
      if (rejection.errors[0]?.code === 'file-too-large') {
        setError('Image too large. Please select an image under 8MB.')
      } else if (rejection.errors[0]?.code === 'file-invalid-type') {
        setError('Invalid file type. Please select a JPEG, PNG, or WebP image.')
      } else {
        setError('Invalid file. Please try another image.')
      }
      return
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      setSelectedFile(file)

      // Create preview URL
      const previewUrl = URL.createObjectURL(file)
      setPreview(previewUrl)

      // Notify parent component
      onFileSelect(file)
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/webp': ['.webp']
    },
    maxSize: 8 * 1024 * 1024, // 8MB
    multiple: false,
    disabled: disabled || isUploading
  })

  const clearFile = () => {
    if (preview) {
      URL.revokeObjectURL(preview)
    }
    setPreview(null)
    setSelectedFile(null)
    setError(null)
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="card">
        <div className="text-center mb-6">
          <Camera className="w-12 h-12 text-slate-400 mx-auto mb-3" />
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Upload Food Image</h2>
          <p className="text-slate-600">
            Take a photo or upload an image of your meal for instant nutrition analysis
          </p>
        </div>

        {!preview ? (
          <div
            {...getRootProps()}
            className={`dropzone ${isDragActive ? 'active' : ''} ${isDragReject ? 'reject' : ''}`}
          >
            <input {...getInputProps()} />
            <Upload className="w-8 h-8 text-slate-400 mx-auto mb-3" />

            {isDragActive ? (
              <p className="text-primary-600 font-medium">Drop your image here...</p>
            ) : (
              <div>
                <p className="text-slate-700 font-medium mb-1">
                  Drag and drop an image, or click to browse
                </p>
                <p className="text-sm text-slate-500">
                  Supports: JPEG, PNG, WebP (max 8MB)
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {/* Image Preview */}
            <div className="relative bg-slate-100 rounded-lg overflow-hidden">
              <Image
                src={preview}
                alt="Food preview"
                width={600}
                height={400}
                className="w-full h-64 object-cover"
                priority
              />

              {!isUploading && (
                <button
                  onClick={clearFile}
                  className="absolute top-2 right-2 p-2 bg-white/90 hover:bg-white rounded-full shadow-sm transition-colors"
                  aria-label="Remove image"
                >
                  <X className="w-4 h-4 text-slate-600" />
                </button>
              )}

              {isUploading && (
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                  <div className="bg-white rounded-lg p-4 flex items-center space-x-3">
                    <div className="spinner w-5 h-5"></div>
                    <span className="text-slate-700 font-medium">Analyzing...</span>
                  </div>
                </div>
              )}
            </div>

            {/* File Info */}
            {selectedFile && (
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Camera className="w-5 h-5 text-slate-400" />
                  <div>
                    <p className="text-sm font-medium text-slate-700">{selectedFile.name}</p>
                    <p className="text-xs text-slate-500">{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>

                {!isUploading && (
                  <button
                    onClick={clearFile}
                    className="text-slate-400 hover:text-slate-600 transition-colors"
                    aria-label="Remove file"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-4 flex items-center space-x-2 p-3 bg-danger-50 border border-danger-200 rounded-lg">
            <AlertCircle className="w-5 h-5 text-danger-600 flex-shrink-0" />
            <p className="text-sm text-danger-700">{error}</p>
          </div>
        )}

        {/* Upload Tips */}
        {!preview && !error && (
          <div className="mt-6 p-4 bg-slate-50 rounded-lg">
            <h3 className="text-sm font-medium text-slate-700 mb-2">Tips for best results:</h3>
            <ul className="text-xs text-slate-600 space-y-1">
              <li>• Ensure good lighting and clear visibility of food items</li>
              <li>• Include the entire meal in the frame if possible</li>
              <li>• Avoid blurry or heavily filtered images</li>
              <li>• Try to capture food from a top-down or angled view</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}