/* ==============================================================
   SortingAction Component
   ==============================================================
   - Shows physical sorting destination bin
   - Shows target servo angle & Arduino command status
   - Interactive Visual Servo Dial / Gauge
   ============================================================== */

import './SortingAction.css';

export default function SortingAction({ prediction }) {
  if (!prediction) {
    return (
      <div className="card sorting-card">
        <h2 className="card-title">Sorting Action</h2>
        <div className="sorting-empty-state">
          <span className="sorting-empty-icon">⚙️</span>
          <p>Servo is idle</p>
          <span className="subtext">Awaiting sorting commands</span>
        </div>
      </div>
    );
  }

  const { destination, servo_angle, sorting_status, arduino_command } = prediction;
  const angle = servo_angle ?? 90;

  // Calculate rotation degree for gauge needle (0° to 180° mapped to -90° to +90° in CSS)
  const needleRotation = angle - 90;

  return (
    <div className="card sorting-card animate-fade-in">
      <div className="card-header-flex">
        <h2 className="card-title">Sorting Action</h2>
        <span
          className={`badge ${
            sorting_status === 'SENT' || sorting_status === 'SUCCESS' || sorting_status === 'SORTED'
              ? 'badge-green'
              : sorting_status === 'SIMULATED'
              ? 'badge-orange'
              : 'badge-red'
          }`}
        >
          {sorting_status || 'PENDING'}
        </span>
      </div>

      <div className="sorting-details-grid">
        <div className="sort-info-box">
          <span className="stat-label">Destination Bin</span>
          <span className="info-value highlight-text">{destination || 'Default Bin'}</span>
        </div>

        <div className="sort-info-box">
          <span className="stat-label">Servo Angle</span>
          <span className="info-value font-mono">{angle}°</span>
        </div>
      </div>

      {/* Servo Gauge Visualization */}
      <div className="servo-gauge-wrapper">
        <div className="gauge-outer">
          <div className="gauge-ticks">
            <span className="tick-label label-0">0°</span>
            <span className="tick-label label-90">90°</span>
            <span className="tick-label label-180">180°</span>
          </div>
          <div
            className="gauge-needle"
            style={{ transform: `rotate(${needleRotation}deg)` }}
          ></div>
          <div className="gauge-center-cap"></div>
        </div>
        <div className="command-display">
          <span className="font-mono text-muted">Command: {arduino_command || `SERVO:${angle}`}</span>
        </div>
      </div>
    </div>
  );
}
