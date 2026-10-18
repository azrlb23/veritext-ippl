export type AuditDepth = "TIER1_ONLY" | "FULL";
export type AuditStatus = "QUEUED" | "PROCESSING" | "SUCCESS" | "FAILED" | "CANCELLED" | "REVOKED";
export type TierLevel = "T1" | "T2" | "T3";
export type AnnotationColor = "RED" | "ORANGE" | "YELLOW";

export interface HeatmapAnnotation {
  start: number;
  end: number;
  tier: TierLevel;
  color: AnnotationColor;
  source_title?: string;
  source_chunk_id?: string;
  similarity: number;
  text_snippet?: string;
}

export interface MatchedSource {
  corpus_doc_id: string;
  title: string;
  category?: string;
  contribution_pct: number;
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
