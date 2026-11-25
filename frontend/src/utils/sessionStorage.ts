const TOKEN_KEY = "veritext_access_token";
const USER_KEY = "veritext_user";
const REFRESH_KEY = "veritext_refresh_token";

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY);
}

export function getStoredUser<T>(): T | null {
  const raw = localStorage.getItem(USER_KEY) || sessionStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export function saveStoredSession(token: string, user: unknown, remember = true): void {
  clearStoredSession();
  const target = remember ? localStorage : sessionStorage;
  target.setItem(TOKEN_KEY, token);
  target.setItem(USER_KEY, JSON.stringify(user));
}

export function updateStoredToken(token: string): void {
  const target = sessionStorage.getItem(TOKEN_KEY) ? sessionStorage : localStorage;
  target.setItem(TOKEN_KEY, token);
}

export function updateStoredUser(user: unknown): void {
  const target = sessionStorage.getItem(TOKEN_KEY) ? sessionStorage : localStorage;
  target.setItem(USER_KEY, JSON.stringify(user));
}

export function clearStoredSession(): void {
  [TOKEN_KEY, USER_KEY, REFRESH_KEY].forEach((k) => {
    localStorage.removeItem(k);
    sessionStorage.removeItem(k);
  });
}
