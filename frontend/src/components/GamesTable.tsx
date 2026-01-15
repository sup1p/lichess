import { Game } from "../types";
import { formatDate } from "../utils";
import "./games-table.css";

interface GamesTableProps {
  games: Game[];
  isLoading: boolean;
  username?: string;
}

export default function GamesTable({ games, isLoading, username }: GamesTableProps) {
  if (isLoading) {
    return (
      <div className="games-table-container">
        <div className="no-games">Loading games...</div>
      </div>
    );
  }

  if (games.length === 0) {
    return (
      <div className="games-table-container">
        <div className="no-games">No games found. Play some games on Lichess!</div>
      </div>
    );
  }

  const getResultForUser = (game: Game, currentUser?: string) => {
    if (!currentUser) return game.result;
    
    const isWhite = game.white.toLowerCase() === currentUser.toLowerCase();
    if (game.result === "1-0") return isWhite ? "Win" : "Loss";
    if (game.result === "0-1") return isWhite ? "Loss" : "Win";
    return "Draw";
  };

  const getResultClass = (game: Game, currentUser?: string) => {
    const result = getResultForUser(game, currentUser);
    if (result === "Win") return "result-white";
    if (result === "Loss") return "result-black";
    return "result-draw";
  };

  const getOpponent = (game: Game, currentUser?: string) => {
    if (!currentUser) return `${game.white} vs ${game.black}`;
    const isWhite = game.white.toLowerCase() === currentUser.toLowerCase();
    return isWhite ? game.black : game.white;
  };

  return (
    <div className="games-table-container">
      <table className="games-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Opponent</th>
            <th>Result</th>
            <th>Opening</th>
            <th>Time</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          {games.map((game) => (
            <tr key={game.game_id}>
              <td>{game.played_at ? formatDate(game.played_at) : "-"}</td>
              <td>{getOpponent(game, username)}</td>
              <td>
                <span className={`result-badge ${getResultClass(game, username)}`}>
                  {getResultForUser(game, username)}
                </span>
              </td>
              <td>{game.opening || "-"}</td>
              <td>{game.time_class}</td>
              <td>
                <a 
                  href={`https://lichess.org/${game.game_id}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="game-link"
                >
                  View
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
