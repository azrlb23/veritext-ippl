export type AuditDepth = "TIER1_ONLY" | "FULL";
export type AuditStatus = "QUEUED" | "PROCESSING" | "SUCCESS" | "FAILED" | "CANCELLED" | "REVOKED";
export type TierLevel = "T1" | "T2" | "T3";
export type AnnotationColor = "RED" | "ORANGE" | "YELLOW" | "RESOLVED_GREEN";

export interface SecondarySourceRef {
  source_title?: string;
  source_category?: string;
  similarity?: number;
  matched_source_text?: string;
}

export interface HeatmapAnnotation {
  sentence_id?: string;
  start: number;
  end: number;
  tier: TierLevel;
  color: AnnotationColor;
  source_title?: string;
  source_category?: string;
  source_chunk_id?: string;
  similarity: number;
  text_snippet?: string;
  matched_source_text?: string;
  secondary_sources?: SecondarySourceRef[];
  source_url?: string;
  reason?: string;
  ai_flag?: boolean;
  ai_reason?: string;
  ai_score?: number;
  active_view?: "LEXICAL" | "SEMANTIC" | "AI" | "RESOLVED";
  is_modified?: boolean;
}

export interface MatchedSource {
  corpus_doc_id: string;
  title: string;
  category?: string;
  contribution_pct: number;
  source_url?: string;
}

export interface SourcePreviewMatch {
  sentence_text: string;
  matched_source_text: string;
  similarity: number;
  tier?: string;
}

export interface SourcePreviewData {
  title: string;
  category: string;
  source_type: string;
  source_url?: string | null;
  full_text: string;
  matched_highlights: SourcePreviewMatch[];
}

export interface AuditReport {
  id: string;
  audit_task_id: string;
  verification_uuid: string;
  score_lexical: number | null;
  score_semantic: number | null;
  score_stylometric: number | null;
  score_composite: number | null;
  heatmap_annotations: HeatmapAnnotation[];
  matched_sources: MatchedSource[];
  pdf_path?: string | null;
  generated_at: string;
  document_title?: string | null;
  document_text?: string | null;
  user_name?: string | null;
}

export interface AuditTask {
  id?: string;
  task_id: string;
  document_id: string;
  celery_task_id?: string | null;
  audit_depth: AuditDepth;
  status: AuditStatus;
  progress_pct: number;
  current_stage?: string | null;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
  document_title?: string | null;
  score_composite?: number | null;
}
