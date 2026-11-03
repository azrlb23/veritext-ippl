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
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;

    // Check if 401 Unauthorized and not already retried and not auth routes
    if (
      error.response &&
      error.response.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/auth/login") &&
      !originalRequest.url?.includes("/auth/refresh")
    ) {
      originalRequest._retry = true;

      try {
        const storedRefreshToken = localStorage.getItem("veritext_refresh_token");
        // Call /auth/refresh silently via standalone axios to avoid interceptor recursion
        const refreshResponse = await axios.post(
          `${baseURL}/auth/refresh`,
          { refresh_token: storedRefreshToken },
          {
            withCredentials: true,
            headers: {
              "Content-Type": "application/json",
              ...(storedRefreshToken ? { "X-Refresh-Token": storedRefreshToken } : {}),
            },
          }
        );

        const newAccessToken =
          refreshResponse.data?.data?.access_token ||
          refreshResponse.data?.access_token;
        const newRefreshToken =
          refreshResponse.data?.data?.refresh_token ||
          refreshResponse.data?.refresh_token;

        if (newAccessToken) {
          localStorage.setItem("veritext_access_token", newAccessToken);
          if (newRefreshToken) {
            localStorage.setItem("veritext_refresh_token", newRefreshToken);
          }
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          }
          // Replay failed request with new access token
          return apiClient(originalRequest);
        }
      } catch {
        // Silent refresh failed - proceed to clean up and logout
      }

      // Logout and redirect when refresh fails
      localStorage.removeItem("veritext_access_token");
      localStorage.removeItem("veritext_refresh_token");
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
    } else if (
      error.response &&
      error.response.status === 401 &&
      (originalRequest?._retry || originalRequest?.url?.includes("/auth/refresh"))
    ) {
      localStorage.removeItem("veritext_access_token");
      localStorage.removeItem("veritext_refresh_token");
      localStorage.removeItem("veritext_user");
      try {
        const { useAuthStore } = await import("../stores/auth");
        const authStore = useAuthStore();
        authStore.logout();
      } catch {}
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
