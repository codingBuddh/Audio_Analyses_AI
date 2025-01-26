import React, { useState } from 'react';

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [originalTranscript, setOriginalTranscript] = useState([]);
  const [translatedTranscript, setTranslatedTranscript] = useState([]);
  const [targetLanguage, setTargetLanguage] = useState('es');
  const [analysisReport, setAnalysisReport] = useState(null);
  const [audioFilePath, setAudioFilePath] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setOriginalTranscript([]);
    setTranslatedTranscript([]);
    setAnalysisReport(null);
    setAudioFilePath('');

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
      setAudioFilePath(data.audio_path);
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
        if (done) {
          setLoading(false);
          return;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        
        // Check for completion signal
        if (lines.some(line => line.includes('[DONE]'))) {
          setLoading(false);
          return;
        }
        
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

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);

    try {
      if (!audioFilePath) {
        throw new Error('Audio file path is not available');
      }

      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          audio_path: audioFilePath,
          transcript: originalTranscript.map(segment => segment.text).join(' ')
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setAnalysisReport(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-text font-lato flex flex-col">
      {/* Header */}
      <header className="bg-surface p-6 border-b border-surface/50">
        <h1 className="text-2xl font-bold text-primary">Audio Analyser</h1>
      </header>

      {/* Main Content */}
      <main className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          {/* URL Input Form */}
          <form onSubmit={handleSubmit} className="mb-8">
            <div className="flex gap-4">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter YouTube URL"
                required
                disabled={loading}
                className="flex-1 px-6 py-3 rounded-lg bg-surface text-text placeholder:text-secondary focus:ring-2 focus:ring-primary outline-none transition-all"
              />
              <button
                type="submit"
                disabled={loading}
                className="px-8 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Processing...' : 'Submit'}
              </button>
            </div>
          </form>

          {/* Error Display */}
          {error && (
            <div className="bg-red-500/10 text-red-400 p-4 rounded-lg mb-8">
              <h2 className="font-bold">Error</h2>
              <p>{error}</p>
            </div>
          )}

          {/* Transcripts Section */}
          {originalTranscript.length > 0 && (
            <div className={`${translatedTranscript.length > 0 ? 'grid grid-cols-1 md:grid-cols-2 gap-8' : 'max-w-2xl mx-auto'} mb-8`}>
              {/* Original Transcript */}
              <div className="bg-surface p-6 rounded-xl">
                <h2 className="text-xl font-semibold mb-4 text-primary">Original Transcript</h2>
                <div className="space-y-4 max-h-[500px] overflow-y-auto pr-4">
                  {originalTranscript.map((segment, index) => (
                    <div key={index} className="bg-background p-4 rounded-lg">
                      <div className="text-secondary text-sm mb-2">{segment.start_timestamp}</div>
                      <div className="text-text">{segment.text}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Translated Transcript */}
              {translatedTranscript.length > 0 && (
                <div className="bg-surface p-6 rounded-xl">
                  <h2 className="text-xl font-semibold mb-4 text-accent">Translated Text</h2>
                  <div className="space-y-4 max-h-[500px] overflow-y-auto pr-4">
                    {translatedTranscript.map((segment, index) => (
                      <div key={index} className="bg-background p-4 rounded-lg">
                        <div className="text-secondary text-sm mb-2">{segment.start_timestamp}</div>
                        <div className="text-text">{segment.text}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Controls Section */}
          {originalTranscript.length > 0 && (
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <select 
                value={targetLanguage} 
                onChange={(e) => setTargetLanguage(e.target.value)}
                disabled={loading}
                className="px-6 py-3 bg-surface text-text rounded-lg focus:ring-2 focus:ring-primary outline-none"
              >
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="zh-cn">Chinese</option>
              </select>
              <button 
                onClick={handleTranslate} 
                disabled={loading}
                className="px-8 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Translating...' : 'Translate'}
              </button>
              <button 
                onClick={handleAnalyze} 
                disabled={loading}
                className="px-8 py-3 bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Analyzing...' : 'Analyze Audio'}
              </button>
            </div>
          )}

          {/* Analysis Report */}
          {analysisReport && (
            <div className="bg-surface p-6 rounded-xl">
              <h2 className="text-xl font-semibold mb-4 text-primary">Audio Analysis Report</h2>
              <pre className="bg-background p-4 rounded-lg text-sm overflow-x-auto">
                {JSON.stringify(analysisReport, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-surface p-4 border-t border-surface/50 text-center text-secondary">
        <p>V1 of AudioAnalyser</p>
      </footer>
    </div>
  );
}

export default App; 