import { apiClient } from "./api";
import type { User } from "../types";

export interface RegisterDTO {
  full_name: string;
  email: string;
  institution?: string;
  password: string;
}

export interface LoginDTO {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  user: User;
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

  async deleteAccount() {
    const res = await apiClient.delete("/auth/me");
    return res.data;
  },
};
