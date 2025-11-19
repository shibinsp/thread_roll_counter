import React, { useState } from 'react';
import ImageUpload from './components/ImageUpload';
import Results from './components/Results';
import RecordsList from './components/RecordsList';
import { predictImage } from './api';
import './index.css';

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleSubmit = async (file, user, description) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await predictImage(file, user, description);
      setResult(data);
      // Trigger refresh of records list
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      console.error('Prediction error:', err);
      setError(
        err.response?.data?.detail ||
        'Failed to process image. Please make sure the backend is running and the YOLO model is loaded.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRecordClick = (record) => {
    setResult(record);
    // Scroll to top to show results
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="app">
      <header className="header">
        <div className="container">
          <h1>Thread Roll Counter</h1>
          <p>AI-powered thread roll detection and counting</p>
        </div>
      </header>

      <main className="container">
        {/* Error Alert */}
        {error && (
          <div className="alert alert-error">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Success Alert */}
        {result && !loading && (
          <div className="alert alert-success">
            <strong>Success!</strong> Detected {result.total_count} thread roll{result.total_count !== 1 ? 's' : ''}
          </div>
        )}

        {/* Image Upload Section */}
        <ImageUpload
          onSubmit={handleSubmit}
          loading={loading}
        />

        {/* Results Section */}
        {result && <Results result={result} />}

        {/* Past Records Section */}
        <RecordsList
          onRecordClick={handleRecordClick}
          refreshTrigger={refreshTrigger}
        />
      </main>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h3>Thread Roll Counter</h3>
            <p>AI-powered object detection and counting system for textile manufacturing.</p>
          </div>

          <div className="footer-section">
            <h3>Features</h3>
            <ul>
              <li>Real-time Detection</li>
              <li>Color Classification</li>
              <li>Historical Records</li>
              <li>Mobile Support</li>
              <li>RESTful API</li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <p>Thread Roll Counter v1.0.0 | © 2025</p>
          <p style={{ marginTop: '0.4rem' }}>Powered by Ultralytics YOLOv11 & FastAPI</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
