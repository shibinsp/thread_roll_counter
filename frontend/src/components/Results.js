import React, { useEffect, useRef } from 'react';
import { getImageUrl } from '../api';

const Results = ({ result }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (result && result.detections && result.image_filename) {
      drawDetections();
    }
  }, [result]);

  const drawDetections = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = getImageUrl(result.image_filename);

    img.onload = () => {
      // Set canvas size to match image
      canvas.width = img.width;
      canvas.height = img.height;

      // Draw image
      ctx.drawImage(img, 0, 0);

      // Draw bounding boxes with numbers
      result.detections.forEach((detection) => {
        const [x1, y1, x2, y2] = detection.bbox;
        const color = getColorForLabel(detection.color);
        const detectionId = detection.id || '?';

        // Draw rectangle
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

        // Draw ID number in top-left corner (larger, more visible)
        ctx.font = 'bold 24px Arial';
        ctx.fillStyle = '#000000';
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 4;
        const idText = `${detectionId}`;
        ctx.strokeText(idText, x1 + 5, y1 + 30);
        ctx.fillText(idText, x1 + 5, y1 + 30);

        // Draw label at bottom of box
        const label = `${detection.color}`;
        ctx.font = '14px Arial';
        const textWidth = ctx.measureText(label).width;
        ctx.fillStyle = color;
        ctx.fillRect(x1, y2 - 20, textWidth + 10, 20);

        // Draw label text
        ctx.fillStyle = '#ffffff';
        ctx.fillText(label, x1 + 5, y2 - 5);
      });
    };
  };

  const getColorForLabel = (label) => {
    const colorMap = {
      pink: '#ff69b4',
      yellow: '#ffd700',
      orange: '#ff8c00',
      orange_brown: '#d2691e',  // Chocolate/brown color
      white: '#000000',
      other: '#808080',
    };
    return colorMap[label] || '#808080';
  };

  if (!result) {
    return null;
  }

  return (
    <div className="card">
      <h2 className="card-title">Detection Results</h2>

      {/* Summary statistics */}
      <div className="results-summary">
        <div className="result-stat">
          <div className="result-stat-value">{result.total_count}</div>
          <div className="result-stat-label">Total Rolls</div>
        </div>
        {Object.entries(result.color_counts).map(([color, count]) => (
          <div key={color} className="result-stat">
            <div className="result-stat-value">{count}</div>
            <div className="result-stat-label">{color}</div>
          </div>
        ))}
      </div>

      {/* Color breakdown */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem' }}>
          Color Breakdown
        </h3>
        <div className="color-list">
          {Object.entries(result.color_counts).map(([color, count]) => (
            <div key={color} className="color-item">
              <div className={`color-badge ${color}`}></div>
              <span style={{ fontWeight: '500' }}>{color}</span>
              <span style={{ color: '#6c757d' }}>×{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Image with detections */}
      <div>
        <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem' }}>
          Detected Boxes
        </h3>
        <canvas ref={canvasRef} style={{ maxWidth: '100%', height: 'auto', border: '1px solid #dee2e6', borderRadius: '4px' }} />
      </div>

      {/* Metadata */}
      {(result.user || result.description) && (
        <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid #dee2e6' }}>
          {result.user && (
            <p style={{ marginBottom: '0.5rem' }}>
              <strong>User:</strong> {result.user}
            </p>
          )}
          {result.description && (
            <p>
              <strong>Description:</strong> {result.description}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default Results;
