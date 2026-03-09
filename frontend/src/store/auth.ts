import { create } from "zustand";
import api from "@/api/axios";

export type UserRole = "superadmin" | "hr" | "manager" | "employee";

export interface CurrentUser {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  department_id: number | null;
  position: string | null;
  is_active: boolean;
}

interface AuthState {
  user: CurrentUser | null;
  loading: boolean;
  setUser: (user: CurrentUser | null) => void;
  fetchMe: () => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: true,
  setUser: (user) => set({ user }),
  fetchMe: async () => {
    try {
      const { data } = await api.get<CurrentUser>("/auth/me");
      set({ user: data, loading: false });
    } catch {
      set({ user: null, loading: false });
    }
  },
  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null });
    window.location.href = "/login";
  },
}));
