import { api } from "../api/client";
import type { User, Profile, GamesResponse } from "../types";
import { API_ENDPOINTS } from "../constants";

export const authService = {
  async getMe(): Promise<User> {
    const response = await api.get<User>(API_ENDPOINTS.AUTH.ME);
    return response.data;
  },

  login(): void {
    window.location.href = `${api.defaults.baseURL}${API_ENDPOINTS.AUTH.LOGIN}`;
  },

  async logout(): Promise<void> {
    await api.post(API_ENDPOINTS.AUTH.LOGOUT);
  },
};

export const profileService = {
  async getProfile(): Promise<Profile> {
    const response = await api.get<Profile>(API_ENDPOINTS.PROFILE);
    return response.data;
  },
};

export const gameService = {
  async getGames(page: number = 1, pageSize: number = 10, timeClass?: string): Promise<GamesResponse> {
    const params: Record<string, any> = { page, per_page: pageSize };
    if (timeClass) {
      params.time_class = timeClass;
    }
    
    const response = await api.get<GamesResponse>(API_ENDPOINTS.GAMES, { params });
    return response.data;
  },
};
