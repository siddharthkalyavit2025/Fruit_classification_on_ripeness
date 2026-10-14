/* ==============================================================
   SystemStatus Component
   ==============================================================
   - Shows live health and status for:
     1. Camera
     2. AI Model (EfficientNetV2-S)
     3. Arduino UNO
     4. Servo Motor
   ============================================================== */

import './SystemStatus.css';

export default function SystemStatus({ statusData, cameraStatus }) {
  const isCamActive = !!cameraStatus?.active;
  const camError = cameraStatus?.error;
  const camDetails = camError
    ? camError
    : isCamActive
    ? cameraStatus?.label || 'Active (Camera)'
    : 'Camera Inactive (Off)';

  const statusItems = [
    {
      id: 'camera',
      name: 'Camera',
      details: camDetails,
      active: isCamActive,
      badge: camError ? 'ERROR' : isCamActive ? 'ONLINE' : 'OFFLINE',
    },
    {
      id: 'model',
      name: 'AI Model',
      details: statusData?.model || 'EfficientNetV2-S (Loaded)',
      active: statusData?.model_loaded ?? true,
      badge: statusData?.model_loaded ? 'READY' : 'LOADING',
    },
    {
      id: 'arduino',
      name: 'Arduino UNO',
      details: statusData?.arduino ? `Connected (${statusData?.serial_port || statusData?.arduino_port || 'COM6'})` : 'Disconnected (COM6)',
      active: statusData?.arduino ?? false,
      badge: statusData?.arduino ? 'CONNECTED' : 'OFFLINE',
    },
    {
      id: 'servo',
      name: 'Servo Motor',
      details: statusData?.servo || 'PWM Pin 9 (Ready)',
      active: statusData?.arduino ?? true,
      badge: 'READY',
    },
  ];

  return (
    <div className="card system-status-card">
      <h2 className="card-title">System Status</h2>

      <div className="status-rows">
        {statusItems.map((item) => (
          <div className="status-row-item" key={item.id}>
            <div className="status-info">
              <span className={`dot ${item.active ? 'dot-green' : 'dot-red'}`} />
              <div className="status-name-group">
                <span className="status-item-name">{item.name}</span>
                <span className="status-item-details">{item.details}</span>
              </div>
            </div>
            <span className={`badge ${item.active ? 'badge-green' : 'badge-red'}`}>
              {item.badge}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
