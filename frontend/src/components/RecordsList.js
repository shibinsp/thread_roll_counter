import React, { useState, useEffect } from 'react';
import { getRecords } from '../api';

const RecordsList = ({ onRecordClick, refreshTrigger }) => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRecords();
  }, [refreshTrigger]);

  const fetchRecords = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getRecords();
      setRecords(data);
    } catch (err) {
      setError('Failed to load records');
      console.error('Error fetching records:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="card">
        <h2 className="card-title">Past Records</h2>
        <div className="spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h2 className="card-title">Past Records</h2>
        <div className="alert alert-error">{error}</div>
      </div>
    );
  }

  if (records.length === 0) {
    return (
      <div className="card">
        <h2 className="card-title">Past Records</h2>
        <div className="alert alert-info">
          No records yet. Upload an image to get started!
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="card-title">Past Records ({records.length})</h2>
      <div className="records-list">
        {records.map((record) => (
          <div
            key={record.id}
            className="record-card"
            onClick={() => onRecordClick && onRecordClick(record)}
          >
            <div className="record-header">
              <div className="record-id">Record #{record.id}</div>
              <div className="record-date">{formatDate(record.created_at)}</div>
            </div>

            <div className="record-stats">
              <div className="record-stat">
                <strong>Total:</strong> {record.total_count} rolls
              </div>
              {record.user && (
                <div className="record-stat">
                  <strong>By:</strong> {record.user}
                </div>
              )}
            </div>

            {/* Color breakdown */}
            {record.color_counts && Object.keys(record.color_counts).length > 0 && (
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                {Object.entries(record.color_counts).map(([color, count]) => (
                  <div key={color} className="color-item" style={{ fontSize: '0.85rem', padding: '0.25rem 0.75rem' }}>
                    <div className={`color-badge ${color}`} style={{ width: '16px', height: '16px' }}></div>
                    <span>{color}: {count}</span>
                  </div>
                ))}
              </div>
            )}

            {record.description && (
              <div className="record-description">"{record.description}"</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecordsList;
