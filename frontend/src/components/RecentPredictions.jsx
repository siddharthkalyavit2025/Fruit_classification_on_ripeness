/* ==============================================================
   RecentPredictions Component
   ==============================================================
   - Table displaying recent predictions history
   - Time, Fruit Emoji/Name, Condition badge, Confidence %,
     Servo Angle, Destination, Status, Delete action button
   ============================================================== */

import './RecentPredictions.css';

export default function RecentPredictions({ predictions = [], onDelete }) {
  const getBadgeClass = (condition) => {
    switch (condition?.toLowerCase()) {
      case 'fresh': return 'badge-green';
      case 'unripe': return 'badge-yellow';
      case 'rotten': return 'badge-red';
      default: return 'badge-cyan';
    }
  };

  const formatTime = (ts) => {
    if (!ts) return 'Just now';
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return ts;
    }
  };

  const getFruitLogo = (fruitName, defaultEmoji) => {
    if (defaultEmoji) return defaultEmoji;
    if (!fruitName) return '🍎';
    const name = fruitName.toLowerCase();
    if (name.includes('apple')) return '🍎';
    if (name.includes('banana')) return '🍌';
    if (name.includes('orange')) return '🍊';
    return '🍎';
  };

  return (
    <div className="card recent-predictions-card">
      <h2 className="card-title">Recent Predictions History</h2>

      {predictions.length === 0 ? (
        <div className="predictions-empty font-mono">
          No predictions recorded yet. Capture an image to generate history.
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Fruit</th>
                <th>Condition</th>
                <th>Confidence</th>
                <th>Servo Angle</th>
                <th>Destination</th>
                <th>Status</th>
                <th style={{ textAlign: 'center' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((item, idx) => (
                <tr key={item.id || idx}>
                  <td className="font-mono text-muted">{formatTime(item.timestamp)}</td>
                  <td className="fruit-cell">
                    <span className="table-emoji">{getFruitLogo(item.fruit, item.emoji)}</span>
                    <span className="table-fruit-name">{item.fruit}</span>
                  </td>
                  <td>
                    <span className={`badge ${getBadgeClass(item.condition)}`}>
                      {item.condition?.toUpperCase()}
                    </span>
                  </td>
                  <td>
                    <div className="confidence-cell font-mono">
                      <span>
                        {item.confidence != null
                          ? `${(item.confidence > 1 ? item.confidence : item.confidence * 100).toFixed(1)}%`
                          : 'N/A'}
                      </span>
                    </div>
                  </td>
                  <td className="font-mono">{item.servo_angle}°</td>
                  <td className="text-secondary">{item.destination}</td>
                  <td>
                    <span
                      className={`badge ${
                        item.sorting_status === 'SORTED' || item.sorting_status === 'SUCCESS' || item.sorting_status === 'SENT'
                          ? 'badge-green'
                          : item.sorting_status === 'SIMULATED'
                          ? 'badge-orange'
                          : 'badge-red'
                      }`}
                    >
                      {item.sorting_status || 'OK'}
                    </span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <button
                      className="delete-btn"
                      onClick={() => onDelete && onDelete(item.id)}
                      title="Remove prediction from history"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
