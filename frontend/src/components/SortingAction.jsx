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
          <p>Servo is Idle (0° Home)</p>
          <span className="subtext">Awaiting sorting commands</span>
        </div>
      </div>
    );
  }

  const { destination, servo_angle, current_servo_angle, sorting_status, arduino_command } = prediction;
  const targetAngle = servo_angle ?? 0;
  const currentAngle = current_servo_angle ?? 0;

  // Calculate rotation degree for gauge needle (-90° to +90° mapped from 0° to 180°)
  const needleRotation = currentAngle - 90;

  const isComplete = sorting_status === 'COMPLETED' || sorting_status === 'SORTED' || sorting_status === 'SUCCESS';
  const isFailed = sorting_status === 'FAILED' || sorting_status === 'ARDUINO_ERROR';

  return (
    <div className="card sorting-card animate-fade-in">
      <div className="card-header-flex">
        <h2 className="card-title">Sorting Action</h2>
        <span
          className={`badge ${
            isComplete
              ? 'badge-green'
              : sorting_status === 'SIMULATED'
              ? 'badge-orange'
              : isFailed
              ? 'badge-red'
              : 'badge-blue'
          }`}
        >
          {isComplete ? 'SORTING COMPLETE ✓' : sorting_status || 'PENDING'}
        </span>
      </div>

      <div className="sorting-details-grid">
        <div className="sort-info-box">
          <span className="stat-label">Destination Bin</span>
          <span className="info-value highlight-text">{destination || 'Default Bin'}</span>
        </div>

        <div className="sort-info-box">
          <span className="stat-label">Target / Home Angle</span>
          <span className="info-value font-mono">{targetAngle}° ➔ 0°</span>
        </div>
      </div>

      {/* Servo Gauge Visualization */}
      <div className="servo-gauge-wrapper">
        <div className="gauge-outer">
          <div className="gauge-ticks">
            <span className="tick-label label-0">0° (Home)</span>
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
          <span className="font-mono text-muted">
            Cmd: {arduino_command || `SERVO:${targetAngle}`} | Pos: {currentAngle}° (Home)
          </span>
        </div>
      </div>
    </div>
  );
}
