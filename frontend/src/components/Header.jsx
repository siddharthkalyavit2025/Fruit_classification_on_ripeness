/* ==============================================================
   Header Component
   ==============================================================
   Top header matching Figma design:
   - Dashboard title
   - Live Arduino connection badge with toggle control
   ============================================================== */

import { connectArduino, disconnectArduino } from '../services/api';
import './Header.css';

export default function Header({ arduinoConnected, serialPort = 'COM6', onStatusChange }) {
  const handleToggleConnection = async () => {
    try {
      if (arduinoConnected) {
        await disconnectArduino();
      } else {
        await connectArduino(serialPort);
      }
      if (onStatusChange) onStatusChange();
    } catch (err) {
      console.error('Error toggling Arduino connection:', err);
    }
  };

  const portName = serialPort || 'COM6';

  return (
    <header className="main-header">
      <div className="header-title-container">
        <h1 className="header-title">Smart Fruit Sorting Dashboard</h1>
        <p className="header-subtitle">Real-time Computer Vision & Automated Hardware Control</p>
      </div>

      <div className="header-actions">
        <button
          className={`arduino-badge ${arduinoConnected ? 'connected' : 'disconnected'}`}
          onClick={handleToggleConnection}
          title="Click to toggle Arduino connection"
        >
          <span className={`dot ${arduinoConnected ? 'dot-green' : 'dot-red'}`} />
          <span className="badge-text">
            {arduinoConnected ? `Arduino Connected (${portName})` : `Arduino Disconnected (${portName})`}
          </span>
        </button>
      </div>
    </header>
  );
}
