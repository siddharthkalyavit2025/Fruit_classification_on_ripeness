/* ==============================================================
   LiveCamera Component
   ==============================================================
   - Browser webcam stream using getUserMedia
   - Multi-camera device enumeration & selection (iVCam & built-in)
   - Auto-detection of iVCam phone camera
   - Local file upload (Upload Image from system)
   - Start / Stop camera controls with clean track teardown
   - Capture frame from the active camera & send to prediction API
   - Scanning overlay and live status indicators
   ============================================================== */

import { useState, useRef, useEffect, useCallback } from 'react';
import './LiveCamera.css';

export default function LiveCamera({ onAnalyze, isAnalyzing, onCameraStatusChange }) {
  const [cameraActive, setCameraActive] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [uploadedPreview, setUploadedPreview] = useState(null);
  const [devices, setDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState('');

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const fileInputRef = useRef(null);
  const selectedDeviceIdRef = useRef(selectedDeviceId);

  // Keep ref synchronized with state
  useEffect(() => {
    selectedDeviceIdRef.current = selectedDeviceId;
  }, [selectedDeviceId]);

  // Stop active camera stream tracks
  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.onended = null;
        track.stop();
      });
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);

    if (onCameraStatusChange) {
      onCameraStatusChange({
        active: false,
        label: 'Camera Inactive (Off)',
        error: null,
      });
    }
  }, [onCameraStatusChange]);

  // Enumerate video input devices and identify iVCam
  const updateDeviceList = useCallback(async (requestPermission = false) => {
    if (!navigator.mediaDevices?.enumerateDevices) {
      setErrorMsg('Media devices API not supported in this browser.');
      return [];
    }

    try {
      let devList = await navigator.mediaDevices.enumerateDevices();
      let videoDevs = devList.filter((d) => d.kind === 'videoinput');

      // If device labels are blank and permission request requested, trigger a quick permission prompt
      const hasLabels = videoDevs.some((d) => d.label && d.label.trim().length > 0);
      if (!hasLabels && requestPermission) {
        try {
          const tempStream = await navigator.mediaDevices.getUserMedia({ video: true });
          tempStream.getTracks().forEach((t) => t.stop());
          devList = await navigator.mediaDevices.enumerateDevices();
          videoDevs = devList.filter((d) => d.kind === 'videoinput');
        } catch (permErr) {
          console.warn('Camera permission request skipped or dismissed:', permErr);
        }
      }

      setDevices(videoDevs);

      // Select iVCam or first device if not yet selected or if current selection became invalid
      setSelectedDeviceId((currentId) => {
        if (currentId && videoDevs.some((d) => d.deviceId === currentId)) {
          return currentId;
        }

        // Search for iVCam device label
        const ivcamDevice = videoDevs.find((d) =>
          d.label.toLowerCase().includes('ivcam')
        );
        if (ivcamDevice) {
          return ivcamDevice.deviceId;
        }

        return videoDevs[0]?.deviceId || '';
      });

      return videoDevs;
    } catch (err) {
      console.warn('Error enumerating camera devices:', err);
      return [];
    }
  }, []);

  // Start camera using the chosen device
  const startCamera = async (overrideDeviceId) => {
    setErrorMsg(null);
    setUploadedPreview(null);

    const targetDeviceId = overrideDeviceId !== undefined ? overrideDeviceId : selectedDeviceIdRef.current;

    // Stop existing stream first to release camera hardware
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.onended = null;
        track.stop();
      });
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    const constraints = {
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        ...(targetDeviceId
          ? { deviceId: { exact: targetDeviceId } }
          : { facingMode: 'environment' }),
      },
    };

    try {
      let stream;
      try {
        stream = await navigator.mediaDevices.getUserMedia(constraints);
      } catch (exactErr) {
        // Fallback to ideal constraint if exact match over-constrained
        console.warn('Exact deviceId constraint failed, retrying with ideal constraint:', exactErr);
        if (targetDeviceId) {
          stream = await navigator.mediaDevices.getUserMedia({
            video: {
              deviceId: { ideal: targetDeviceId },
              width: { ideal: 1280 },
              height: { ideal: 720 },
            },
          });
        } else {
          throw exactErr;
        }
      }

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        try {
          await videoRef.current.play();
        } catch (playErr) {
          console.warn('Video play attempt warning:', playErr);
        }
      }

      setCameraActive(true);

      // Now that camera permission is granted, re-enumerate devices to guarantee labels are populated
      const freshDevs = await updateDeviceList(false);

      const activeTrack = stream.getVideoTracks()[0];
      const activeSettings = activeTrack?.getSettings();
      const activeDeviceId = activeSettings?.deviceId || targetDeviceId;

      if (activeDeviceId && activeDeviceId !== selectedDeviceIdRef.current) {
        setSelectedDeviceId(activeDeviceId);
      }

      const activeLabel =
        activeTrack?.label ||
        freshDevs.find((d) => d.deviceId === activeDeviceId)?.label ||
        'Active Camera';

      if (onCameraStatusChange) {
        onCameraStatusChange({
          active: true,
          label: activeLabel,
          error: null,
        });
      }

      // Handle unexpected camera disconnection (e.g., iVCam disconnected on phone)
      if (activeTrack) {
        activeTrack.onended = () => {
          console.warn('Camera track ended unexpectedly.');
          stopCamera();
          const disconnectMsg = 'Camera disconnected or stream lost.';
          setErrorMsg(disconnectMsg);
          if (onCameraStatusChange) {
            onCameraStatusChange({
              active: false,
              label: 'Disconnected',
              error: disconnectMsg,
            });
          }
        };
      }
    } catch (err) {
      console.error('Camera access error:', err);
      let friendlyError = 'Failed to access camera.';
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        friendlyError = 'Camera access was blocked by browser. Please grant camera permission.';
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        friendlyError = 'Selected camera not found. Check if iVCam is connected.';
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        friendlyError = 'Camera is currently in use by another application or iVCam client is not active.';
      } else if (err.name === 'OverconstrainedError') {
        friendlyError = 'Selected camera does not satisfy requested resolution.';
      } else {
        friendlyError = `Camera error: ${err.message || err.name}`;
      }

      setErrorMsg(friendlyError);
      setCameraActive(false);

      if (onCameraStatusChange) {
        onCameraStatusChange({
          active: false,
          label: 'Error',
          error: friendlyError,
        });
      }
    }
  };

  // Handle switching camera from dropdown
  const handleCameraChange = async (e) => {
    const newDeviceId = e.target.value;
    setSelectedDeviceId(newDeviceId);

    if (cameraActive) {
      // Seamlessly switch to new camera
      await startCamera(newDeviceId);
    }
  };

  // Capture frame from active camera stream
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

  // Local file upload
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

  // Initial enumeration and device change listener
  useEffect(() => {
    updateDeviceList(false);

    const handleDeviceChange = () => {
      updateDeviceList(false);
    };

    if (navigator.mediaDevices?.addEventListener) {
      navigator.mediaDevices.addEventListener('devicechange', handleDeviceChange);
    }

    return () => {
      if (navigator.mediaDevices?.removeEventListener) {
        navigator.mediaDevices.removeEventListener('devicechange', handleDeviceChange);
      }
      stopCamera();
    };
  }, [updateDeviceList, stopCamera]);

  const selectedDevice = devices.find((d) => d.deviceId === selectedDeviceId);
  const isSelectedIvc = selectedDevice?.label?.toLowerCase().includes('ivcam');

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
              <span className="dot dot-green"></span> {isSelectedIvc ? 'iVCam LIVE' : 'LIVE FEED'}
            </span>
          ) : errorMsg ? (
            <span className="badge badge-red" title={errorMsg}>
              <span className="dot dot-red"></span> ERROR
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

      {/* Camera Device Selector Dropdown */}
      <div className="camera-select-bar">
        <label htmlFor="camera-device-select" className="camera-select-label">
          <span className="cam-select-icon">📹</span> Camera:
        </label>
        <select
          id="camera-device-select"
          className="camera-dropdown"
          value={selectedDeviceId}
          onChange={handleCameraChange}
          disabled={isAnalyzing}
          aria-label="Select Camera Device"
        >
          {devices.length === 0 ? (
            <option value="">Default / System Camera</option>
          ) : (
            devices.map((device, idx) => {
              const isIvc = device.label.toLowerCase().includes('ivcam');
              return (
                <option key={device.deviceId || idx} value={device.deviceId}>
                  {device.label || `Camera ${idx + 1}`}
                  {isIvc ? ' ★ (iVCam)' : ''}
                </option>
              );
            })
          )}
        </select>
        <button
          type="button"
          className="btn-refresh-devices"
          onClick={() => updateDeviceList(true)}
          title="Refresh camera devices and permissions"
          disabled={isAnalyzing}
        >
          🔄
        </button>
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
            <p className="placeholder-text">{errorMsg || 'Camera is turned off'}</p>
            {errorMsg && (
              <p className="placeholder-subtext">
                Tip: If using iVCam, verify the iVCam Windows app is running and your phone is connected.
              </p>
            )}
            <button className="btn btn-secondary" onClick={() => startCamera()}>
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
          <button className="btn btn-secondary" onClick={() => startCamera()} disabled={isAnalyzing}>
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

