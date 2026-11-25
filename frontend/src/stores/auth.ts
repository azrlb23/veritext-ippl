import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { User } from "../types";
import { authService, type LoginDTO, type RegisterDTO, type CompleteGoogleSignupDTO } from "../services/authService";
import { useAuditStore } from "./audit";
import {
  getStoredToken,
  getStoredUser,
  saveStoredSession,
  updateStoredUser,
  clearStoredSession,
} from "../utils/sessionStorage";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(getStoredUser<User>());
  const token = ref<string | null>(getStoredToken());
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

  function applySession(data: { access_token: string; user: User }, remember = true) {
    token.value = data.access_token;
    user.value = data.user;
    saveStoredSession(data.access_token, data.user, remember);
  }

  function decrementTokenBalance(amount: number) {
    if (user.value) {
      user.value.token_balance = Math.max(0, (user.value.token_balance ?? 5) - amount);
      updateStoredUser(user.value);
    }
  }

  function setTokenBalance(balance: number) {
    if (user.value) {
      user.value.token_balance = balance;
      updateStoredUser(user.value);
    }
  }

  async function login(creds: LoginDTO) {
    isLoading.value = true;
    try {
      const data = await authService.login(creds);
      applySession(data, creds.remember_me ?? true);
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

  function clearLocalSession() {
    user.value = null;
    token.value = null;
    welcomeName.value = null;
    sessionStorage.removeItem("veritext_welcome");
    clearStoredSession();
    try { useAuditStore().reset(); } catch { /* Fallback */ }
  }

  async function logout() {
    try { await authService.logout(); } catch { /* Ignore network failure */ }
    clearLocalSession();
  }

  async function fetchProfile() {
    if (!token.value) return;
    try {
      const profile = await authService.getProfile();
      user.value = profile;
      updateStoredUser(profile);
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

  async function exchangeGoogleCode(code: string) {
    isLoading.value = true;
    try {
      const sessionData = await authService.exchangeGoogleCode(code);
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
    user, token, welcomeName, isLoading, isAuthenticated, role, tokenBalance, isAdmin,
    decrementTokenBalance, setTokenBalance, login, register, logout, clearLocalSession, deleteAccount,
    fetchProfile, completeGoogleSignup, exchangeGoogleCode, markWelcome, consumeWelcome,
  };
});
