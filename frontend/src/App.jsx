/* ==============================================================
   Smart Fruit Sorting Dashboard — App.jsx
   ==============================================================
   Main Dashboard Layout:
   - Sidebar on the left
   - Main content area:
     - Header (Title + Arduino Status)
     - Top Grid: LiveCamera, AIPrediction, SortingAction
     - Middle Grid: SystemStatus, Statistics
     - Bottom Row: RecentPredictions History Table
   ============================================================== */

import { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import LiveCamera from './components/LiveCamera';
import AIPrediction from './components/AIPrediction';
import SortingAction from './components/SortingAction';
import SystemStatus from './components/SystemStatus';
import Statistics from './components/Statistics';
import RecentPredictions from './components/RecentPredictions';

import {
  predictImage,
  getRecentPredictions,
  deletePrediction,
  getStats,
  getStatus,
} from './services/api';

import './App.css';

export default function App() {
  const [latestPrediction, setLatestPrediction] = useState(null);
  const [predictionsHistory, setPredictionsHistory] = useState([]);
  const [statusData, setStatusData] = useState(null);
  const [statsData, setStatsData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [cameraStatus, setCameraStatus] = useState({
    active: false,
    label: 'Camera Inactive (Off)',
    error: null,
  });

  // Fetch system status
  const fetchStatus = useCallback(async () => {
    try {
      const data = await getStatus();
      setStatusData(data);
    } catch (err) {
      console.warn('Status fetch error:', err);
    }
  }, []);

  // Fetch statistics
  const fetchStats = useCallback(async () => {
    try {
      const data = await getStats();
      setStatsData(data);
    } catch (err) {
      console.warn('Stats fetch error:', err);
    }
  }, []);

  // Fetch recent predictions history
  const fetchHistory = useCallback(async () => {
    try {
      const data = await getRecentPredictions(15);
      if (data && data.predictions) {
        setPredictionsHistory(data.predictions);
        if (data.predictions.length > 0 && !latestPrediction) {
          setLatestPrediction(data.predictions[0]);
        }
      }
    } catch (err) {
      console.warn('History fetch error:', err);
    }
  }, [latestPrediction]);

  // Initial load and periodic polling
  useEffect(() => {
    fetchStatus();
    fetchStats();
    fetchHistory();

    const statusInterval = setInterval(fetchStatus, 3000);
    const statsInterval = setInterval(fetchStats, 5000);

    return () => {
      clearInterval(statusInterval);
      clearInterval(statsInterval);
    };
  }, [fetchStatus, fetchStats, fetchHistory]);

  // Handle capture & analyze from camera feed
  const handleAnalyzeFrame = async (imageBlob) => {
    setIsAnalyzing(true);
    try {
      const result = await predictImage(imageBlob);
      setLatestPrediction(result);
      // Refresh history and stats after successful analysis
      await Promise.all([fetchHistory(), fetchStats()]);
    } catch (err) {
      console.error('Prediction failed:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDeletePrediction = async (predictionId) => {
    try {
      await deletePrediction(predictionId);
      await Promise.all([fetchHistory(), fetchStats()]);
    } catch (err) {
      console.error('Failed to delete prediction:', err);
    }
  };

  return (
    <div className="app-container">
      {/* Left Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="main-viewport">
        {/* Header */}
        <Header
          arduinoConnected={statusData?.arduino ?? false}
          serialPort={statusData?.serial_port || 'COM6'}
          onStatusChange={fetchStatus}
        />

        {/* Dashboard Content Container */}
        <main className="dashboard-content">
          {/* Top Row: Camera, AI Prediction, Sorting Action */}
          <div className="dashboard-grid grid-3-cols">
            <LiveCamera
              onAnalyze={handleAnalyzeFrame}
              isAnalyzing={isAnalyzing}
              onCameraStatusChange={setCameraStatus}
            />
            <AIPrediction
              prediction={latestPrediction}
              isAnalyzing={isAnalyzing}
            />
            <SortingAction prediction={latestPrediction} />
          </div>

          {/* Middle Row: System Status, Statistics */}
          <div className="dashboard-grid grid-2-cols">
            <SystemStatus
              statusData={statusData}
              cameraStatus={cameraStatus}
            />
            <Statistics stats={statsData} />
          </div>

          {/* Bottom Row: Recent Predictions History */}
          <div className="dashboard-row">
            <RecentPredictions
              predictions={predictionsHistory}
              onDelete={handleDeletePrediction}
            />
          </div>
        </main>
      </div>
    </div>
  );
}
