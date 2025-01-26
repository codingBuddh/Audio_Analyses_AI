import React, { useState } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [transcript, setTranscript] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setTranscript([]);

    try {
      const response = await fetch('http://localhost:8000/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to process video');
      }

      const data = await response.json();
      setTranscript(data.transcript);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>YouTube Transcript Extractor</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter YouTube URL"
          required
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </form>

      {error && (
        <div className="error">
          <h2>Error</h2>
          <p>{error}</p>
        </div>
      )}

      {transcript.length > 0 && (
        <div className="transcript">
          <h2>Transcript</h2>
          {transcript.map((segment, index) => (
            <div key={index} className="transcript-segment">
              <div className="timestamp">{segment.start_timestamp}</div>
              <div className="text">{segment.text}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App; 