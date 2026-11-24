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
  role: "FREE" | "PREMIUM" | "ADMIN";
  token_balance: number;
  is_active: boolean;
  created_at: string;
}

export interface AdminAnalytics {
  total_documents: number;
  avg_similarity: number;
  total_revenue: number;
  active_users: number;
}

export interface SystemHealthMetrics {
  database_status: string;
  db_latency_ms: number;
  total_vector_chunks: number;
  redis_status: string;
  celery_active_tasks: number;
  total_audits: number;
  total_corpus_docs: number;
  queue_depth?: number;
  celery_workers?: number;
  cpu_percent?: number;
  memory_percent?: number;
  redis_mem_mb?: number;
  pgvector_latency_ms?: number;
  timestamp?: string;
}

export interface AdminTransactionItem {
  id?: string;
  order_id: string;
  user_id?: string;
  package_name?: string;
  token_amount?: number;
  gross_amount: number;
  payment_method?: string | null;
  status: string;
  paid_at?: string | null;
  created_at?: string | null;
}

export interface AuditLogItem {
  id: string;
  actor_id?: string | null;
  actor_ip?: string | null;
  action_type: string;
  resource_type?: string | null;
  resource_id?: string | null;
  action_result: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface AdminUserItem {
  id: string;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
  balance: number;
  ai_trial_remaining: number;
  audit_count: number;
  is_locked: boolean;
  created_at: string;
}

export interface TrendPoint {
  date: string;
  audits: number;
  revenue: number;
}

export interface OverviewExtras {
  new_users_7d: number;
  audits_today: number;
  tokens_spent_30d: number;
  role_distribution: Record<string, number>;
  trends: TrendPoint[];
}

export interface InvoiceSummary {
  total_revenue: number;
  paid: number;
  pending: number;
  failed: number;
  top_package: string | null;
}

export interface SystemExtras {
  failed_audits_24h: number;
  queued_audits: number;
  processing_audits: number;
}

export interface AdminPaginationMeta {
  total: number;
  page: number;
  limit: number;
  pages: number;
}
