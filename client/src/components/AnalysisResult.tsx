import type { Analysis } from '../types'
import {
  AlertTriangle,
  CheckCircle,
  Activity,
  Droplets,
  Circle
} from 'lucide-react'

interface AnalysisResultProps {
  analysis: Analysis
}

export default function AnalysisResult({ analysis }: AnalysisResultProps) {
  const getSeverity = (count: number): 'low' | 'medium' | 'high' => {
    if (count === 0) return 'low'
    if (count <= 10) return 'medium'
    return 'high'
  }

  const severity = getSeverity(analysis.acne_count)

  return (
    <div className="analysis-result">
      <div className="result-header">
        <h3>Analysis Results</h3>
        <span className={`severity-badge ${severity}`}>
          {severity === 'low' && <CheckCircle size={16} />}
          {severity === 'medium' && <Activity size={16} />}
          {severity === 'high' && <AlertTriangle size={16} />}
          {severity.charAt(0).toUpperCase() + severity.slice(1)} Severity
        </span>
      </div>

      <div className="result-grid">
        {/* Acne Overview */}
        <div className="result-card">
          <h4>Acne Detection</h4>
          <div className="stat-large">
            {analysis.acne_count}
            <span>lesions detected</span>
          </div>
          {analysis.acne_detected && (
            <div className="lesion-breakdown">
              <div className="lesion-item">
                <Circle size={12} fill="var(--color-papule)" />
                <span>Papules: {analysis.papules_count}</span>
              </div>
              <div className="lesion-item">
                <Circle size={12} fill="var(--color-pustule)" />
                <span>Pustules: {analysis.pustules_count}</span>
              </div>
              <div className="lesion-item">
                <Circle size={12} fill="var(--color-comedone)" />
                <span>Comedones: {analysis.comedone_count}</span>
              </div>
              <div className="lesion-item">
                <Circle size={12} fill="var(--color-nodule)" />
                <span>Nodules: {analysis.nodules_count}</span>
              </div>
            </div>
          )}
        </div>

        {/* Redness Analysis */}
        <div className="result-card">
          <h4>
            <Droplets size={20} />
            Redness Analysis
          </h4>
          <div className="redness-stats">
            <div className="redness-item">
              <span>Average Redness</span>
              <div className="redness-bar">
                <div
                  className="redness-fill"
                  style={{ width: `${Math.min(analysis.avg_redness * 100, 100)}%` }}
                />
              </div>
              <span>{(analysis.avg_redness * 100).toFixed(1)}%</span>
            </div>
            <div className="redness-item">
              <span>Global Redness</span>
              <div className="redness-bar">
                <div
                  className="redness-fill"
                  style={{ width: `${Math.min(analysis.global_redness * 100, 100)}%` }}
                />
              </div>
              <span>{(analysis.global_redness * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Skin Classification */}
        <div className="result-card">
          <h4>Skin Classification</h4>
          {analysis.skin_disease_label && analysis.skin_disease_label !== 'NULL' ? (
            <div className="classification-result">
              <span className="disease-label">{analysis.skin_disease_label}</span>
              {analysis.skin_disease_confidence && (
                <span className="confidence">
                  {(analysis.skin_disease_confidence * 100).toFixed(1)}% confidence
                </span>
              )}
            </div>
          ) : (
            <p className="no-detection">No specific skin condition detected</p>
          )}

          {analysis.skin_classification_labels && (
            <div className="tags">
              {analysis.skin_classification_labels.split(',').map((label, i) => (
                <span key={i} className="tag">{label.trim()}</span>
              ))}
            </div>
          )}
        </div>

        {/* Dimensions (if acne detected) */}
        {analysis.acne_detected && (
          <div className="result-card">
            <h4>Average Lesion Size</h4>
            <div className="dimensions">
              <div className="dimension-item">
                <span>Width</span>
                <strong>{analysis.avg_acne_width.toFixed(1)}px</strong>
              </div>
              <div className="dimension-item">
                <span>Height</span>
                <strong>{analysis.avg_acne_height.toFixed(1)}px</strong>
              </div>
              <div className="dimension-item">
                <span>Area</span>
                <strong>{analysis.avg_acne_area.toFixed(1)}px²</strong>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
