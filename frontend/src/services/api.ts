import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem("veritext_access_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("veritext_access_token");
      localStorage.removeItem("veritext_user");
      try {
        const { useAuthStore } = await import("../stores/auth");
        const authStore = useAuthStore();
        authStore.logout();
      } catch {
        // Safe fallback if invoked outside active pinia context
      }
      if (typeof window !== "undefined" && window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    // Normalisasi error boundary untuk gateway 502/503/504 & network offline
    if (!error.response) {
      error.message = error.message || "Network error: Layanan server tidak dapat dihubungi atau sedang offline.";
    } else if (error.response.status === 502 || error.response.status === 503 || error.response.status === 504) {
      error.message = "Gateway Error: Layanan backend sementara tidak tersedia. Silakan coba beberapa saat lagi.";
    }

    return Promise.reject(error);
  }
);

