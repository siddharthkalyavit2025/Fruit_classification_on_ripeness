/* ==============================================================
   AIPrediction Component
   ==============================================================
   - Displays AI Classification results from EfficientNetV2-S
   - Fruit Emoji & Name
   - Condition Badge (Fresh, Unripe, Rotten)
   - Confidence % bar
   - Predicted class tag
   ============================================================== */

import './AIPrediction.css';

export default function AIPrediction({ prediction, isAnalyzing }) {
  if (isAnalyzing) {
    return (
      <div className="card ai-prediction-card">
        <h2 className="card-title">AI Prediction</h2>
        <div className="ai-loading-container">
          <div className="ai-loader-ring"></div>
          <p className="ai-loading-text">Analyzing image using EfficientNetV2-S...</p>
        </div>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="card ai-prediction-card">
        <h2 className="card-title">AI Prediction</h2>
        <div className="ai-empty-state">
          <span className="ai-empty-icon">🤖</span>
          <p>No prediction yet</p>
          <span className="subtext">Click "Capture & Analyze" to start</span>
        </div>
      </div>
    );
  }

  const { fruit, condition, confidence, predicted_class, emoji } = prediction;

  // Condition Badge mapping
  const getConditionBadgeClass = (cond) => {
    switch (cond?.toLowerCase()) {
      case 'fresh': return 'badge-green';
      case 'unripe': return 'badge-yellow';
      case 'rotten': return 'badge-red';
      default: return 'badge-cyan';
    }
  };

  const confidencePct = confidence != null
    ? (confidence > 1 ? confidence : confidence * 100).toFixed(1)
    : '0.0';

  const getFruitLogo = (fruitName, defaultEmoji) => {
    if (defaultEmoji) return defaultEmoji;
    if (!fruitName) return '🍎';
    const name = fruitName.toLowerCase();
    if (name.includes('apple')) return '🍎';
    if (name.includes('banana')) return '🍌';
    if (name.includes('orange')) return '🍊';
    return '🍎';
  };

  const fruitLogo = getFruitLogo(fruit, emoji);

  return (
    <div className="card ai-prediction-card animate-fade-in">
      <div className="card-header-flex">
        <h2 className="card-title">AI Prediction</h2>
        <span className={`badge ${getConditionBadgeClass(condition)}`}>
          {condition?.toUpperCase()}
        </span>
      </div>

      <div className="prediction-main">
        <div className="fruit-emoji-box">
          <span className="fruit-emoji">{fruitLogo}</span>
        </div>
        <div className="fruit-details">
          <h3 className="fruit-name">{fruit}</h3>
          <span className="class-label font-mono">{predicted_class}</span>
        </div>
      </div>

      {/* Metric details */}
      <div className="confidence-section">
        <div className="confidence-header">
          <span className="stat-label">Model Confidence</span>
          <span className="confidence-val font-mono">{confidencePct}%</span>
        </div>
        <div className="progress-bar">
          <div
            className="progress-bar-fill cyan"
            style={{ width: `${confidencePct}%` }}
          />
        </div>
      </div>
    </div>
  );
}
