export interface Analysis {
  id: string
  filename: string
  acne_count: number
  avg_acne_width: number
  avg_acne_height: number
  avg_acne_area: number
  papules_count: number
  pustules_count: number
  comedone_count: number
  nodules_count: number
  avg_redness: number
  global_redness: number
  skin_disease_label: string | null
  skin_disease_confidence: number | null
  skin_classification_labels: string
  acne_detected: boolean
  created_at?: string
}

export interface User {
  id: string
  email: string
  created_at?: string
}
