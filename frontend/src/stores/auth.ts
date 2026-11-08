import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { User } from "../types";
import { authService, type LoginDTO, type RegisterDTO, type CompleteGoogleSignupDTO } from "../services/authService";
import { useAuditStore } from "./audit";

export const useAuthStore = defineStore("auth", () => {
  const rawUser = localStorage.getItem("veritext_user");
  let initialUser: User | null = null;
  try { initialUser = rawUser ? JSON.parse(rawUser) : null; } catch { initialUser = null; }

  const user = ref<User | null>(initialUser);
  const token = ref<string | null>(localStorage.getItem("veritext_access_token"));
  const welcomeName = ref<string | null>(sessionStorage.getItem("veritext_welcome"));
  const isLoading = ref<boolean>(false);

  const isAuthenticated = computed(() => !!token.value);
  const role = computed(() => user.value?.role || "FREE");
  const isAdmin = computed(() => role.value === "ADMIN");
  const tokenBalance = computed(() => user.value?.token_balance ?? 5);

  function markWelcome(name?: string) {
    const val = name || user.value?.full_name || "Pengguna";
    welcomeName.value = val;
    sessionStorage.setItem("veritext_welcome", val);
  }

  function consumeWelcome(): string | null {
    const val = welcomeName.value || sessionStorage.getItem("veritext_welcome");
    welcomeName.value = null;
    sessionStorage.removeItem("veritext_welcome");
    return val;
  }

  function applySession(data: { access_token: string; user: User; refresh_token?: string }) {
    token.value = data.access_token;
    user.value = data.user;
    localStorage.setItem("veritext_access_token", data.access_token);
    if (data.refresh_token) localStorage.setItem("veritext_refresh_token", data.refresh_token);
    localStorage.setItem("veritext_user", JSON.stringify(data.user));
  }

  function decrementTokenBalance(amount: number) {
    if (user.value) {
      user.value.token_balance = Math.max(0, (user.value.token_balance ?? 5) - amount);
      localStorage.setItem("veritext_user", JSON.stringify(user.value));
    }
  }

  function setTokenBalance(balance: number) {
    if (user.value) {
      user.value.token_balance = balance;
      localStorage.setItem("veritext_user", JSON.stringify(user.value));
    }
  }

  async function login(creds: LoginDTO) {
    isLoading.value = true;
    try {
      const data = await authService.login(creds);
      applySession(data);
      markWelcome();
      return data;
    } finally {
      isLoading.value = false;
    }
  }

  async function register(data: RegisterDTO) {
    isLoading.value = true;
    try {
      const res = await authService.register(data);
      const loginData = (res as any)?.data;
      if (loginData?.access_token && loginData?.user) {
        applySession(loginData);
        markWelcome();
      }
      return res;
    } finally {
      isLoading.value = false;
    }
  }

  async function logout() {
    try { await authService.logout(); } catch { /* Ignore network failure */ }
    user.value = null;
    token.value = null;
    welcomeName.value = null;
    sessionStorage.removeItem("veritext_welcome");
    ["veritext_access_token", "veritext_refresh_token", "veritext_user"].forEach((k) => localStorage.removeItem(k));
    try { useAuditStore().reset(); } catch { /* Fallback */ }
  }

  async function fetchProfile() {
    if (!token.value) return;
    try {
      const profile = await authService.getProfile();
      user.value = profile;
      localStorage.setItem("veritext_user", JSON.stringify(profile));
    } catch (err: any) {
      if (err?.response?.status === 401) await logout();
    }
  }

  async function deleteAccount() {
    await authService.deleteAccount();
    await logout();
  }

  async function completeGoogleSignup(data: CompleteGoogleSignupDTO) {
    isLoading.value = true;
    try {
      const res = await authService.completeGoogleSignup(data);
      const sessionData = (res as any)?.data || res;
      if (sessionData?.access_token && sessionData?.user) {
        applySession(sessionData);
        markWelcome();
      }
      return sessionData;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    user,
    token,
    welcomeName,
    isLoading,
    isAuthenticated,
    role,
    tokenBalance,
    isAdmin,
    decrementTokenBalance,
    setTokenBalance,
    login,
    register,
    logout,
    deleteAccount,
    fetchProfile,
    completeGoogleSignup,
    markWelcome,
    consumeWelcome,
  };
});
