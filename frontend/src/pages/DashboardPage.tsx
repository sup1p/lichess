import { useAuth, useGames, useProfile } from "../hooks";
import ProfileCard from "../components/ProfileCard";
import GamesTable from "../components/GamesTable";
import Pagination from "../components/Pagination";
import { DEFAULT_PAGE_SIZE } from "../constants";
import "@/styles/app.css";

export function DashboardPage() {
  const { user, isLoading: authLoading, login, logout } = useAuth();
  const { profile, isLoading: profileLoading } = useProfile();
  const {
    games,
    total,
    page,
    isLoading: gamesLoading,
    nextPage,
    prevPage,
  } = useGames(DEFAULT_PAGE_SIZE);

  if (authLoading) {
    return (
      <div className="layout centered">
        <p>Загрузка...</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="layout centered">
        <div className="auth-container">
          <h1>Lichess Stats</h1>
          <p>Отображение рейтингов и истории игр</p>
          <button className="primary" onClick={login}>
            Войти через Lichess
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="layout">
      <header className="header">
        <h1>Lichess Stats</h1>
        <button className="secondary" onClick={logout}>
          Выйти ({user.username})
        </button>
      </header>

      <ProfileCard profile={profile} isLoading={profileLoading} />
      
      <div className="games-section">
        <h2>Recent Games</h2>
        <GamesTable 
          games={games} 
          isLoading={gamesLoading} 
          username={user.username}
        />
        {!gamesLoading && games.length > 0 && (
          <Pagination
            page={page}
            total={total}
            pageSize={DEFAULT_PAGE_SIZE}
            onPrevPage={prevPage}
            onNextPage={nextPage}
          />
        )}
      </div>
    </div>
  );
}
