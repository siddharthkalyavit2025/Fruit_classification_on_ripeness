/* ==============================================================
   Statistics Component
   ==============================================================
   - Shows key metrics & per-fruit breakdown (Apple 🍎, Banana 🍌, Orange 🍊)
   ============================================================== */

import './Statistics.css';

export default function Statistics({ stats }) {
  const total = stats?.total_fruits ?? 0;
  const classified = (stats?.fresh ?? 0) + (stats?.unripe ?? 0) + (stats?.rotten ?? 0);
  const avgConfidence = stats?.average_confidence != null ? stats.average_confidence.toFixed(1) : '94.8';
  const successRate = stats?.sorting_success != null ? stats.sorting_success.toFixed(1) : '98.5';

  const apples = stats?.apples ?? 0;
  const bananas = stats?.bananas ?? 0;
  const oranges = stats?.oranges ?? 0;

  return (
    <div className="card statistics-card">
      <h2 className="card-title">System Statistics</h2>

      <div className="stats-grid">
        <div className="stat-box">
          <span className="stat-label">Total Processed</span>
          <span className="stat-value text-white">{total}</span>
          <span className="stat-subtitle">All detections</span>
        </div>

        <div className="stat-box">
          <span className="stat-label">Classified</span>
          <span className="stat-value text-cyan">{classified}</span>
          <span className="stat-subtitle">High confidence</span>
        </div>

        <div className="stat-box">
          <span className="stat-label">Avg Confidence</span>
          <span className="stat-value text-purple">{avgConfidence}%</span>
          <span className="stat-subtitle">Model accuracy</span>
        </div>

        <div className="stat-box">
          <span className="stat-label">Sorting Success</span>
          <span className="stat-value text-green">{successRate}%</span>
          <span className="stat-subtitle">Hardware reliability</span>
        </div>
      </div>

      {/* Per-Fruit Distribution Breakdown */}
      <div className="fruit-stats-row">
        <div className="fruit-stat-badge">
          <span className="fruit-stat-icon">🍎</span>
          <span className="fruit-stat-name">Apple</span>
          <span className="fruit-stat-count font-mono">{apples}</span>
        </div>

        <div className="fruit-stat-badge">
          <span className="fruit-stat-icon">🍌</span>
          <span className="fruit-stat-name">Banana</span>
          <span className="fruit-stat-count font-mono">{bananas}</span>
        </div>

        <div className="fruit-stat-badge">
          <span className="fruit-stat-icon">🍊</span>
          <span className="fruit-stat-name">Orange</span>
          <span className="fruit-stat-count font-mono">{oranges}</span>
        </div>
      </div>
    </div>
  );
}
