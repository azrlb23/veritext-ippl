export type DocumentStatus = "UPLOADED" | "PROCESSING" | "READY" | "ERROR" | "DELETED";

export interface DocumentItem {
  id: string;
  user_id: string;
  original_filename: string;
  file_size_bytes: number;
  mime_type: string;
  word_count?: number | null;
  sha256_hash?: string | null;
  status: DocumentStatus;
  created_at: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  task_id?: string | null;
  original_filename: string;
  message: string;
}
