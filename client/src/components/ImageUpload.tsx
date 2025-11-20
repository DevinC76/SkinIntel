import { useState, useRef } from 'react'
import { Upload, X, Image as ImageIcon, Loader2 } from 'lucide-react'
import { api } from '../lib/api'
import { useAuth } from '../hooks/useAuth'
import type { Analysis } from '../types'

interface ImageUploadProps {
  onAnalysisComplete: (analysis: Analysis) => void
}

export default function ImageUpload({ onAnalysisComplete }: ImageUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const { session } = useAuth()

  const handleFile = (selectedFile: File) => {
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please select an image file')
      return
    }

    setFile(selectedFile)
    setError('')

    // Create preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(selectedFile)
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const clearFile = () => {
    setFile(null)
    setPreview(null)
    setError('')
    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  const handleAnalyze = async () => {
    if (!file || !session?.access_token) return

    setLoading(true)
    setError('')

    try {
      const result = await api.analyzeImage(file, session.access_token)
      onAnalysisComplete(result)
      clearFile()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="upload-container">
      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''} ${preview ? 'has-preview' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !preview && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          onChange={handleChange}
          style={{ display: 'none' }}
        />

        {preview ? (
          <div className="preview-container">
            <img src={preview} alt="Preview" className="preview-image" />
            <button className="clear-btn" onClick={(e) => { e.stopPropagation(); clearFile(); }}>
              <X size={20} />
            </button>
          </div>
        ) : (
          <div className="upload-placeholder">
            <Upload size={48} />
            <p>Drag and drop an image here, or click to select</p>
            <span>Supports JPG, PNG, WEBP</span>
          </div>
        )}
      </div>

      {error && <p className="upload-error">{error}</p>}

      {file && (
        <div className="upload-actions">
          <div className="file-info">
            <ImageIcon size={20} />
            <span>{file.name}</span>
          </div>
          <button
            className="btn btn-primary"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 size={20} className="spin" />
                Analyzing...
              </>
            ) : (
              'Analyze Skin'
            )}
          </button>
        </div>
      )}
    </div>
  )
}
