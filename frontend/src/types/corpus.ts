export type CorpusStatus = "PENDING_INDEX" | "INDEXING" | "INDEXED" | "ERROR" | "DELETED";

export interface CorpusDocument {
  id: string;
  uploaded_by: string;
  title: string;
  category?: string | null;
  academic_year?: string | null;
  stored_filename: string;
  sha256_hash: string;
  status: CorpusStatus;
  total_chunks?: number | null;
  created_at: string;
  updated_at: string;
}
