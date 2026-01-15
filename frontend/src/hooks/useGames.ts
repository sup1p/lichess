import { useState, useEffect, useCallback } from "react";
import { gameService } from "../services/api";
import type { Game } from "../types";

export const useGames = (pageSize: number = 10) => {
  const [games, setGames] = useState<Game[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchGames = useCallback(
    async (currentPage: number) => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await gameService.getGames(currentPage, pageSize);
        setGames(response.games);
        setTotal(response.total);
      } catch (err) {
        setError("Failed to fetch games");
        console.error("Error fetching games:", err);
      } finally {
        setIsLoading(false);
      }
    },
    [pageSize]
  );

  useEffect(() => {
    fetchGames(page);
  }, [page, fetchGames]);

  const nextPage = useCallback(() => {
    if (page * pageSize < total) {
      setPage((p) => p + 1);
    }
  }, [page, pageSize, total]);

  const prevPage = useCallback(() => {
    if (page > 1) {
      setPage((p) => p - 1);
    }
  }, [page]);

  const goToPage = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  return {
    games,
    total,
    page,
    isLoading,
    error,
    nextPage,
    prevPage,
    goToPage,
    refresh: () => fetchGames(page),
  };
};
