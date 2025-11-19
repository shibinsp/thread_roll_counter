import React, { useState, useRef } from 'react';

const ImageUpload = ({ onImageSelect, onSubmit, loading }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [user, setUser] = useState('');
  const [description, setDescription] = useState('');
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
      if (onImageSelect) onImageSelect(file);
    }
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedFile && onSubmit) {
      onSubmit(selectedFile, user, description);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setUser('');
    setDescription('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="card">
      <h2 className="card-title">Upload Image</h2>
      <form onSubmit={handleSubmit}>
        {!previewUrl ? (
          <div
            className={`upload-area ${dragging ? 'dragging' : ''}`}
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <div className="upload-icon">📷</div>
            <p style={{ marginBottom: '0.5rem', fontSize: '1.1rem', fontWeight: '500' }}>
              Click to upload or drag and drop
            </p>
            <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>
              Supports JPG, PNG, WEBP
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleFileInputChange}
              className="file-input"
            />
          </div>
        ) : (
          <div className="image-preview">
            <img src={previewUrl} alt="Preview" />
            <button
              type="button"
              onClick={handleReset}
              className="btn btn-secondary"
              style={{ marginTop: '1rem', width: '100%' }}
            >
              Change Image
            </button>
          </div>
        )}

        {selectedFile && (
          <>
            <div className="form-group" style={{ marginTop: '1rem' }}>
              <label className="form-label">Your Name (Optional)</label>
              <input
                type="text"
                className="form-input"
                placeholder="Enter your name"
                value={user}
                onChange={(e) => setUser(e.target.value)}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Description (Optional)</label>
              <textarea
                className="form-textarea"
                placeholder="Add notes about this detection..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{ width: '100%' }}
            >
              {loading ? (
                <>
                  <span>Processing...</span>
                  <div className="spinner" style={{ display: 'inline-block', width: '20px', height: '20px', marginLeft: '10px', verticalAlign: 'middle' }}></div>
                </>
              ) : (
                'Detect Thread Rolls'
              )}
            </button>
          </>
        )}
      </form>
    </div>
  );
};

export default ImageUpload;
