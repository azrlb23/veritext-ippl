export interface SystemMetric {
  total_users: number;
  total_audits: number;
  total_corpus_docs: number;
  vector_count: number;
  avg_processing_time_ms: number;
  system_load_pct: number;
}

export interface SystemConfig {
  winnowing_kgram: number;
  winnowing_window: number;
  hnsw_similarity_threshold: number;
  hnsw_ef_search: number;
  stylometric_burstiness_threshold: number;
  sandbox_mode: boolean;
}

export interface ManagedUser {
  id: string;
  full_name: string;
  email: string;
  institution?: string | null;
  role: "TRIAL" | "PREMIUM" | "REVIEWER" | "ADMIN";
  token_balance: number;
  is_active: boolean;
  created_at: string;
}

export interface AuditLogItem {
  id: string;
  timestamp: string;
  actor_name: string;
  actor_email: string;
  action:
    | "USER_SUSPEND"
    | "USER_ACTIVATE"
    | "TOKEN_ADJUST"
    | "ROLE_CHANGE"
    | "CONFIG_UPDATE"
    | "CORPUS_INGEST"
    | "AUTH_LOGIN"
    | "DOCUMENT_PURGE";
  target_resource: string;
  ip_address: string;
  status: "SUCCESS" | "FAILED";
  details?: string;
}

