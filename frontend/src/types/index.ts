//TypeScript type definitions

export interface User {
  id: number;
  username: string;
  lichess_id: string;
}

export interface Game {
  id: number;
  game_id: string;
  white: string;
  black: string;
  result: string;
  opening: string;
  time_class: string;
  played_at: string | null;
  pgn: string | null;
}

export interface GamesResponse {
  games: Game[];
  total: number;
  page: number;
  per_page: number;
}

export interface Profile {
  username: string;
  created_at: number;
  seen_at: number;
  ratings: Record<string, number>;
  counts: {
    all?: number;
    rated?: number;
    win?: number;
    loss?: number;
    draw?: number;
  };
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: () => void;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}
