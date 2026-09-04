/* ==============================================================
   Sidebar Component
   ==============================================================
   Left sidebar matching Figma design:
   - FruitSort branding
   - System Online badge
   - CPU / MEM / GPU bars (from real backend data)
   ============================================================== */

import { useState, useEffect } from 'react';
import { getSystemInfo } from '../services/api';
import './Sidebar.css';

export default function Sidebar() {
  const [systemInfo, setSystemInfo] = useState({
    cpu_percent: 0,
    memory_percent: 0,
    gpu_percent: null,
    gpu_available: false,
  });

  useEffect(() => {
    // Poll system info every 5 seconds
    const fetchInfo = async () => {
      try {
        const data = await getSystemInfo();
        setSystemInfo(data);
      } catch {
        // Silently fail — sidebar stats are non-critical
      }
    };

    fetchInfo();
    const interval = setInterval(fetchInfo, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <aside className="sidebar">
      {/* Branding */}
      <div className="sidebar-brand">
        <span className="brand-icon">🍑</span>
        <span className="brand-text">FruitSort</span>
      </div>

      {/* System Online Badge */}
      <div className="system-badge">
        <span className="dot dot-green"></span>
        <span>System Online</span>
      </div>

      {/* System Resources */}
      <div className="resource-meters">
        <ResourceMeter
          label="CPU"
          value={systemInfo.cpu_percent}
          color="var(--green)"
        />
        <ResourceMeter
          label="MEM"
          value={systemInfo.memory_percent}
          color="var(--blue)"
        />
        <ResourceMeter
          label="GPU"
          value={systemInfo.gpu_percent ?? (systemInfo.gpu_available ? 0 : null)}
          color="var(--purple)"
          unavailable={!systemInfo.gpu_available}
        />
      </div>
    </aside>
  );
}

function ResourceMeter({ label, value, color, unavailable = false }) {
  const displayValue = unavailable ? 'N/A' : `${Math.round(value ?? 0)}%`;
  const barWidth = unavailable ? 0 : (value ?? 0);

  return (
    <div className="resource-meter">
      <div className="resource-header">
        <span className="resource-label">{label}</span>
        <span className="resource-value">{displayValue}</span>
      </div>
      <div className="progress-bar" style={{ height: '3px' }}>
        <div
          className="progress-bar-fill"
          style={{
            width: `${barWidth}%`,
            background: color,
          }}
        />
      </div>
    </div>
  );
}
