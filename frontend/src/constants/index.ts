// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: "/auth/login",
    LOGOUT: "/auth/logout",
    ME: "/auth/me",
  },
  PROFILE: "/profile",
  GAMES: "/games/",
} as const;

// Game results
export const GAME_RESULTS = {
  WHITE_WIN: "1-0",
  BLACK_WIN: "0-1",
  DRAW: "1/2-1/2",
} as const;

// Colors for game results
export const RESULT_COLORS: Record<string, string> = {
  "1-0": "green",
  "0-1": "red",
  "1/2-1/2": "gray",
};

// Pagination defaults
export const DEFAULT_PAGE_SIZE = 10;
export const DEFAULT_PAGE = 1;
