/* ==============================================================
   LiveCamera Component
   ==============================================================
   - Browser webcam stream using getUserMedia
   - Local file upload (Upload Image from system)
   - Start / Stop camera controls
   - Capture frame & send to prediction backend API
   - Scanning overlay and status indicator
   ============================================================== */

import { useState, useRef, useEffect } from 'react';
import './LiveCamera.css';

export default function LiveCamera({ onAnalyze, isAnalyzing }) {
  const [cameraActive, setCameraActive] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [uploadedPreview, setUploadedPreview] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const fileInputRef = useRef(null);

  const startCamera = async () => {
    setErrorMsg(null);
    setUploadedPreview(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'environment' }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setCameraActive(true);
    } catch (err) {
      console.error('Camera access error:', err);
      setErrorMsg('Camera access denied or device not found.');
      setCameraActive(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  };

  useEffect(() => {
    // Camera starts in off state by default
    return () => {
      stopCamera();
    };
  }, []);

  const handleCapture = () => {
    if (!videoRef.current || !cameraActive || isAnalyzing) return;

    const video = videoRef.current;
    const canvas = canvasRef.current || document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        if (blob && onAnalyze) {
          onAnalyze(blob);
        }
      },
      'image/jpeg',
      0.9
    );
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    stopCamera();
    const previewUrl = URL.createObjectURL(file);
    setUploadedPreview(previewUrl);

    if (onAnalyze) {
      onAnalyze(file);
    }
  };

  return (
    <div className="card camera-card">
      <div className="card-header-flex">
        <h2 className="card-title">Camera & Image Input</h2>
        <div className="camera-status">
          {isAnalyzing ? (
            <span className="badge badge-purple animate-pulse">
              <span className="dot dot-cyan"></span> ANALYZING...
            </span>
          ) : cameraActive ? (
            <span className="badge badge-green">
              <span className="dot dot-green"></span> LIVE FEED
            </span>
          ) : uploadedPreview ? (
            <span className="badge badge-cyan">
              <span className="dot dot-cyan"></span> FILE UPLOADED
            </span>
          ) : (
            <span className="badge badge-red">
              <span className="dot dot-red"></span> STANDBY
            </span>
          )}
        </div>
      </div>

      {/* Video / Preview Container */}
      <div className="video-wrapper">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className={`video-element ${cameraActive ? 'active' : ''}`}
        />

        {uploadedPreview && !cameraActive && (
          <img src={uploadedPreview} alt="Uploaded fruit" className="uploaded-preview-img" />
        )}

        {!cameraActive && !uploadedPreview && (
          <div className="video-placeholder">
            <span className="cam-icon">📹</span>
            <p>{errorMsg || 'Camera is turned off'}</p>
            <button className="btn btn-secondary" onClick={startCamera}>
              Turn On Camera
            </button>
          </div>
        )}

        {/* Scanning & Targeting Overlay */}
        {(cameraActive || uploadedPreview) && (
          <div className="camera-overlay">
            <div className={`scan-line ${isAnalyzing ? 'scanning' : ''}`}></div>
            <div className="viewfinder-box">
              <div className="corner top-left"></div>
              <div className="corner top-right"></div>
              <div className="corner bottom-left"></div>
              <div className="corner bottom-right"></div>
            </div>
          </div>
        )}
      </div>

      <canvas ref={canvasRef} style={{ display: 'none' }} />
      <input
        type="file"
        ref={fileInputRef}
        accept="image/*"
        style={{ display: 'none' }}
        onChange={handleFileUpload}
      />

      {/* Controls */}
      <div className="camera-controls">
        {cameraActive ? (
          <button className="btn btn-secondary" onClick={stopCamera} disabled={isAnalyzing}>
            Stop Cam
          </button>
        ) : (
          <button className="btn btn-secondary" onClick={startCamera} disabled={isAnalyzing}>
            Start Cam
          </button>
        )}

        <button
          className="btn btn-secondary upload-btn"
          onClick={() => fileInputRef.current?.click()}
          disabled={isAnalyzing}
          title="Upload image file from computer"
        >
          📁 Upload Image
        </button>

        {cameraActive && (
          <button
            className="btn btn-primary capture-btn"
            onClick={handleCapture}
            disabled={!cameraActive || isAnalyzing}
          >
            {isAnalyzing ? (
              <>
                <span className="spinner"></span> Processing...
              </>
            ) : (
              <>
                🔍 Analyze
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}
