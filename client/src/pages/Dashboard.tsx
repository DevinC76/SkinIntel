import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { api } from '../lib/api'
import type { Analysis } from '../types'
import ImageUpload from '../components/ImageUpload'
import AnalysisResult from '../components/AnalysisResult'
import { LogOut, History, Trash2, Loader2, User } from 'lucide-react'

export default function Dashboard() {
  const { user, session, signOut } = useAuth()
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [currentResult, setCurrentResult] = useState<Analysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [showHistory, setShowHistory] = useState(false)

  useEffect(() => {
    if (session?.access_token) {
      loadAnalyses()
    }
  }, [session])

  const loadAnalyses = async () => {
    if (!session?.access_token) return

    try {
      const result = await api.getAnalyses(session.access_token)
      setAnalyses(result.analyses)
    } catch (err) {
      console.error('Failed to load analyses:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAnalysisComplete = (analysis: Analysis) => {
    setCurrentResult(analysis)
    setAnalyses(prev => [analysis, ...prev])
  }

  const handleDelete = async (id: string) => {
    if (!session?.access_token) return
    if (!confirm('Are you sure you want to delete this analysis?')) return

    try {
      await api.deleteAnalysis(id, session.access_token)
      setAnalyses(prev => prev.filter(a => a.id !== id))
      if (currentResult?.id === id) {
        setCurrentResult(null)
      }
    } catch (err) {
      console.error('Failed to delete:', err)
    }
  }

  const handleLogout = async () => {
    try {
      await signOut()
    } catch (err) {
      console.error('Logout failed:', err)
    }
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>SkinIntel</h1>
        <div className="header-actions">
          <button
            className={`btn btn-secondary ${showHistory ? 'active' : ''}`}
            onClick={() => setShowHistory(!showHistory)}
          >
            <History size={20} />
            History ({analyses.length})
          </button>
          <div className="user-info">
            <User size={20} />
            <span>{user?.email}</span>
          </div>
          <button className="btn btn-ghost" onClick={handleLogout}>
            <LogOut size={20} />
          </button>
        </div>
      </header>

      <main className="dashboard-main">
        {showHistory ? (
          <div className="history-panel">
            <h2>Analysis History</h2>
            {loading ? (
              <div className="loading">
                <Loader2 size={32} className="spin" />
              </div>
            ) : analyses.length === 0 ? (
              <p className="empty-state">No analyses yet. Upload an image to get started!</p>
            ) : (
              <div className="history-list">
                {analyses.map(analysis => (
                  <div
                    key={analysis.id}
                    className={`history-item ${currentResult?.id === analysis.id ? 'active' : ''}`}
                    onClick={() => { setCurrentResult(analysis); setShowHistory(false); }}
                  >
                    <div className="history-item-info">
                      <span className="filename">{analysis.filename}</span>
                      <span className="date">
                        {analysis.created_at
                          ? new Date(analysis.created_at).toLocaleDateString()
                          : 'Recent'}
                      </span>
                    </div>
                    <div className="history-item-stats">
                      <span className={`acne-count ${analysis.acne_detected ? 'detected' : ''}`}>
                        {analysis.acne_count} lesions
                      </span>
                      <button
                        className="btn btn-icon"
                        onClick={(e) => { e.stopPropagation(); handleDelete(analysis.id); }}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="analysis-panel">
            <section className="upload-section">
              <h2>Upload Image</h2>
              <p>Upload a clear photo of your skin for AI-powered analysis</p>
              <ImageUpload onAnalysisComplete={handleAnalysisComplete} />
            </section>

            {currentResult && (
              <section className="results-section">
                <AnalysisResult analysis={currentResult} />
              </section>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
