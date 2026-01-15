import type { Profile } from "../types";
import "./profile-card.css";

interface ProfileCardProps {
  profile: Profile | null;
  isLoading: boolean;
}

export default function ProfileCard({ profile, isLoading }: ProfileCardProps) {
  if (isLoading) {
    return <div className="card">Loading profile...</div>;
  }

  if (!profile) {
    return <div className="card">No profile data</div>;
  }

  const counts = profile.counts || {};
  const ratings = profile.ratings || {};

  return (
    <div className="card profile-card">
      <div className="profile-header">
        <h2 className="profile-username">{profile.username}</h2>
      </div>
      
      <div className="stats-grid">
        <div className="stat-item">
          <span className="stat-value">{counts.all || 0}</span>
          <span className="stat-label">Games</span>
        </div>
        <div className="stat-item win">
          <span className="stat-value">{counts.win || 0}</span>
          <span className="stat-label">Wins</span>
        </div>
        <div className="stat-item loss">
          <span className="stat-value">{counts.loss || 0}</span>
          <span className="stat-label">Losses</span>
        </div>
        <div className="stat-item draw">
          <span className="stat-value">{counts.draw || 0}</span>
          <span className="stat-label">Draws</span>
        </div>
      </div>

      {Object.keys(ratings).length > 0 && (
        <div className="ratings-section">
          <h3>Ratings</h3>
          <div className="ratings-grid">
            {Object.entries(ratings).map(([mode, rating]) => (
              <div key={mode} className="rating-item">
                <span className="rating-mode">{mode}</span>
                <span className="rating-value">{rating}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
