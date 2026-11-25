import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from "axios";
import { clearStoredSession, getStoredToken, updateStoredToken } from "../utils/sessionStorage";

const baseURL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

let onAuthExpired: (() => void) | null = null;
export function registerAuthExpiredHandler(handler: () => void) {
  onAuthExpired = handler;
}

function clearClientSession() {
  clearStoredSession();
  try {
    onAuthExpired?.();
  } catch {
    // Safe fallback if invoked outside active pinia context
  }
  if (typeof window !== "undefined" && window.location.pathname !== "/login") {
    window.location.href = "/login";
  }
}

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getStoredToken();
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
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;

    if (
      error.response &&
      error.response.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/auth/login") &&
      !originalRequest.url?.includes("/auth/logout") &&
      !originalRequest.url?.includes("/auth/refresh")
    ) {
      originalRequest._retry = true;

      try {
        // Mengandalkan HttpOnly cookie refresh_token sepenuhnya
        const refreshResponse = await axios.post(
          `${baseURL}/auth/refresh`,
          {},
          {
            withCredentials: true,
            headers: { "Content-Type": "application/json" },
          }
        );

        const newAccessToken =
          refreshResponse.data?.data?.access_token ||
          refreshResponse.data?.access_token;

        if (newAccessToken) {
          updateStoredToken(newAccessToken);
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          }
          return apiClient(originalRequest);
        }
      } catch {
        // Silent refresh failed - proceed to clean up and logout
      }

      clearClientSession();
    } else if (
      error.response &&
      error.response.status === 401 &&
      (originalRequest?._retry || originalRequest?.url?.includes("/auth/refresh"))
    ) {
      clearClientSession();
    }

    if (!error.response) {
      error.message = error.message || "Network error: Layanan server tidak dapat dihubungi atau sedang offline.";
    } else if (error.response.status === 502 || error.response.status === 503 || error.response.status === 504) {
      error.message = "Gateway Error: Layanan backend sementara tidak tersedia. Silakan coba beberapa saat lagi.";
    }

    return Promise.reject(error);
  }
);
