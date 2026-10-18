export type UserRole = "TRIAL" | "PREMIUM" | "REVIEWER" | "ADMIN";

export interface User {
  id: string;
  full_name: string;
  email: string;
  institution?: string | null;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  token_balance?: number;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
