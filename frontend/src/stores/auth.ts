import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { User } from "../types";
import { authService, type LoginDTO, type RegisterDTO } from "../services/authService";

export const useAuthStore = defineStore("auth", () => {
  const savedUser = localStorage.getItem("veritext_user");
  let initialUser: User | null = null;
  if (savedUser) {
    try {
      initialUser = JSON.parse(savedUser);
    } catch {
      initialUser = null;
    }
  }

  const user = ref<User | null>(initialUser);
  let savedToken = localStorage.getItem("veritext_access_token");
  if (!savedToken && initialUser) {
    savedToken = `demo-token-${initialUser.id}`;
    localStorage.setItem("veritext_access_token", savedToken);
  }
  const token = ref<string | null>(savedToken);
  const isLoading = ref<boolean>(false);

  const isAuthenticated = computed(() => !!token.value || !!user.value);
  const role = computed(() => user.value?.role || "TRIAL");
  const isReviewerOrAdmin = computed(() => ["REVIEWER", "ADMIN"].includes(role.value));
  const tokenBalance = computed(() => user.value?.token_balance ?? 5);

  function setDemoSession(demoUser: User, demoToken: string) {
    user.value = demoUser;
    token.value = demoToken;
    localStorage.setItem("veritext_access_token", demoToken);
    localStorage.setItem("veritext_user", JSON.stringify(demoUser));
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
      token.value = data.access_token;
      user.value = data.user;
      localStorage.setItem("veritext_access_token", data.access_token);
      localStorage.setItem("veritext_user", JSON.stringify(data.user));
      return data;
    } finally {
      isLoading.value = false;
    }
  }

  async function register(data: RegisterDTO) {
    isLoading.value = true;
    try {
      const res = await authService.register(data);
      if (res && "data" in res && res.data && "access_token" in (res.data as any)) {
        const loginData = res.data as { access_token: string; user: User };
        token.value = loginData.access_token;
        user.value = loginData.user;
        localStorage.setItem("veritext_access_token", loginData.access_token);
        localStorage.setItem("veritext_user", JSON.stringify(loginData.user));
      }
      return res;
    } finally {
      isLoading.value = false;
    }
  }

  async function logout() {
    user.value = null;
    token.value = null;
    localStorage.removeItem("veritext_access_token");
    localStorage.removeItem("veritext_user");
    try {
      await authService.logout();
    } catch {
      // Ignore network failure on logout
    }
  }

  async function fetchProfile() {
    if (!token.value || token.value.startsWith("demo-token-")) return;
    try {
      const profile = await authService.getProfile();
      user.value = profile;
      localStorage.setItem("veritext_user", JSON.stringify(profile));
    } catch (err: any) {
      if (err?.response?.status === 401) {
        if (!token.value?.startsWith("demo-token-")) {
          logout();
        }
      }
    }
  }

  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    role,
    tokenBalance,
    isReviewerOrAdmin,
    setDemoSession,
    decrementTokenBalance,
    setTokenBalance,
    login,
    register,
    logout,
    fetchProfile,
  };
});
