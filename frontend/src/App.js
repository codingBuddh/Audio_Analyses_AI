import React, { useState } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [originalTranscript, setOriginalTranscript] = useState([]);
  const [translatedTranscript, setTranslatedTranscript] = useState([]);
  const [targetLanguage, setTargetLanguage] = useState('es');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setOriginalTranscript([]);
    setTranslatedTranscript([]);

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
      setOriginalTranscript(data.transcript);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTranslate = async () => {
    setLoading(true);
    setError(null);
    setTranslatedTranscript([]);

    try {
      const response = await fetch('http://localhost:8000/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transcript: originalTranscript,
          target_language: targetLanguage
        }),
      });

      if (!response.ok) {
        throw new Error('Translation failed');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      const processChunk = async () => {
        const { done, value } = await reader.read();
        if (done) return;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        
        // Process all complete messages
        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].replace('data: ', '');
          if (line.trim() === '') continue;
          
          const data = JSON.parse(line);
          setTranslatedTranscript(prev => {
            const lastSegment = prev[prev.length - 1];
            if (lastSegment && lastSegment.start_seconds === data.translated.start_seconds) {
              return [
                ...prev.slice(0, -1),
                {
                  ...lastSegment,
                  text: lastSegment.text + data.translated.char
                }
              ];
            } else {
              return [
                ...prev,
                {
                  text: data.translated.char,
                  start_seconds: data.translated.start_seconds,
                  start_timestamp: data.translated.start_timestamp
                }
              ];
            }
          });
        }
        
        // Keep incomplete message in buffer
        buffer = lines[lines.length - 1];
        
        // Process next chunk immediately
        processChunk();
      };

      // Start processing chunks
      processChunk();
    } catch (error) {
      setError(error.message);
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

      {originalTranscript.length > 0 && (
        <div className="transcript-container">
          <div className="transcript-box">
            <h2>Original Transcript</h2>
            {originalTranscript.map((segment, index) => (
              <div key={index} className="transcript-segment">
                <div className="timestamp">{segment.start_timestamp}</div>
                <div className="text">{segment.text}</div>
              </div>
            ))}
          </div>

          {translatedTranscript.length > 0 && (
            <div className="transcript-box">
              <h2>Translated Text</h2>
              {translatedTranscript.map((segment, index) => (
                <div key={index} className="transcript-segment">
                  <div className="timestamp">{segment.start_timestamp}</div>
                  <div className="text">{segment.text}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {originalTranscript.length > 0 && (
        <div className="translation-controls">
          <select 
            value={targetLanguage} 
            onChange={(e) => setTargetLanguage(e.target.value)}
            disabled={loading}
          >
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="zh-cn">Chinese</option>
          </select>
          <button onClick={handleTranslate} disabled={loading}>
            {loading ? 'Translating...' : 'Translate'}
          </button>
        </div>
      )}
    </div>
  );
}

export default App; 