import { apiClient } from "./api";
import type { User } from "../types";

export interface RegisterDTO {
  full_name: string;
  email: string;
  password: string;
}

export interface LoginDTO {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  user: User;
  refresh_token?: string;
}

export interface CompleteGoogleSignupDTO {
  ticket: string;
  full_name: string;
  password: string;
}

export const authService = {
  async register(data: RegisterDTO) {
    const res = await apiClient.post<{ data: LoginResponse | User; message: string }>("/auth/register", data);
    return res.data;
  },

  async login(data: LoginDTO) {
    const res = await apiClient.post<{ data: LoginResponse }>("/auth/login", data);
    return res.data.data;
  },

  async logout() {
    const res = await apiClient.post("/auth/logout");
    return res.data;
  },

  async getProfile() {
    const res = await apiClient.get<{ data: User }>("/auth/me");
    return res.data.data;
  },

  async forgotPassword(email: string) {
    const res = await apiClient.post<{ message: string; data: Record<string, unknown> }>("/auth/forgot-password", { email });
    return res.data;
  },

  async resetPassword(token: string, new_password: string) {
    const res = await apiClient.post<{ message: string; data: Record<string, unknown> }>("/auth/reset-password", { token, new_password });
    return res.data;
  },

  async updateProfile(fullName: string) {
    const res = await apiClient.patch<{ data: User }>("/auth/profile", { full_name: fullName });
    return res.data.data;
  },

  async changePassword(oldPassword: string, newPassword: string) {
    const res = await apiClient.post("/auth/change-password", { old_password: oldPassword, new_password: newPassword });
    return res.data;
  },

  async deleteAccount() {
    const res = await apiClient.delete("/auth/me");
    return res.data;
  },

  async completeGoogleSignup(data: CompleteGoogleSignupDTO) {
    const res = await apiClient.post<{ data: LoginResponse }>("/auth/google/complete", data);
    return res.data.data;
  },
};
