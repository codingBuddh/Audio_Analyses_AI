import React from 'react';
import { Pie, Bar, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const getEmotionLabel = (intensity) => {
  if (intensity > 1000000) return 'Very High';
  if (intensity > 100000) return 'High';
  if (intensity > 10000) return 'Medium';
  if (intensity > 1000) return 'Low';
  return 'Very Low';
};

const AudioAnalysisVisualization = ({ analysis }) => {
  // Common chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.dataset.label || '';
            const value = context.raw || 0;
            return `${label}: ${value}`;
          }
        }
      }
    }
  };

  // Pitch Analysis Data
  const pitchData = {
    labels: ['Average Pitch', 'Pitch Variability', 'Pitch Range'],
    datasets: [
      {
        label: 'Pitch Analysis',
        data: [
          analysis.pitch_analysis.average_pitch,
          analysis.pitch_analysis.pitch_variability,
          analysis.pitch_analysis.pitch_range
        ],
        backgroundColor: [
          'rgba(255, 99, 132, 0.2)',
          'rgba(54, 162, 235, 0.2)',
          'rgba(75, 192, 192, 0.2)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)'
        ],
        borderWidth: 1,
      },
    ],
  };

  // Signal Quality Data
  const signalQualityData = {
    labels: ['Average RMS', 'Noise Floor', 'SNR'],
    datasets: [
      {
        label: 'Signal Quality',
        data: [
          analysis.signal_quality.average_rms,
          analysis.signal_quality.noise_floor,
          analysis.signal_quality.signal_to_noise_ratio
        ],
        backgroundColor: 'rgba(255, 159, 64, 0.2)',
        borderColor: 'rgba(255, 159, 64, 1)',
        borderWidth: 1,
      },
    ],
  };

  // Voice Quality Data
  const voiceQualityData = {
    labels: ['Jitter', 'Shimmer', 'Quality Score'],
    datasets: [
      {
        label: 'Voice Quality',
        data: [
          analysis.voice_quality.jitter,
          analysis.voice_quality.shimmer,
          Math.abs(analysis.voice_quality.voice_quality_score)
        ],
        backgroundColor: [
          'rgba(255, 99, 132, 0.2)',
          'rgba(54, 162, 235, 0.2)',
          'rgba(75, 192, 192, 0.2)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)'
        ],
        borderWidth: 1,
      },
    ],
  };

  // Speech Patterns Data
  const speechPatternsData = {
    labels: ['Pause Count', 'Avg Pause Duration', 'Word Rate'],
    datasets: [
      {
        label: 'Speech Patterns',
        data: [
          analysis.speech_patterns.pause_count,
          analysis.speech_patterns.average_pause_duration,
          analysis.speech_patterns.word_rate
        ],
        backgroundColor: 'rgba(153, 102, 255, 0.2)',
        borderColor: 'rgba(153, 102, 255, 1)',
        borderWidth: 1,
      },
    ],
  };

  // Emotion Analysis Data
  const emotionData = {
    labels: ['Emotional Intensity'],
    datasets: [
      {
        label: 'Emotion Analysis',
        data: [analysis.emotion_analysis.emotional_intensity],
        backgroundColor: 'rgba(255, 206, 86, 0.2)',
        borderColor: 'rgba(255, 206, 86, 1)',
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Pitch Analysis */}
      <div className="bg-surface p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4 text-primary">Pitch Analysis</h3>
        <div className="h-96">
          <Bar data={pitchData} options={chartOptions} />
        </div>
        <div className="mt-4 space-y-2">
          <p>Average Pitch: {analysis.pitch_analysis.average_pitch.toFixed(2)} Hz</p>
          <p>Pitch Variability: {analysis.pitch_analysis.pitch_variability.toFixed(2)}</p>
          <p>Pitch Range: {analysis.pitch_analysis.pitch_range.toFixed(2)} Hz</p>
        </div>
      </div>

      {/* Signal Quality */}
      <div className="bg-surface p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4 text-primary">Signal Quality</h3>
        <div className="h-96">
          <Line data={signalQualityData} options={chartOptions} />
        </div>
        <div className="mt-4 space-y-2">
          <p>Average RMS: {analysis.signal_quality.average_rms.toFixed(2)}</p>
          <p>Noise Floor: {analysis.signal_quality.noise_floor.toFixed(2)}</p>
          <p>SNR: {analysis.signal_quality.signal_to_noise_ratio.toFixed(2)} dB</p>
        </div>
      </div>

      {/* Voice Quality */}
      <div className="bg-surface p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4 text-primary">Voice Quality</h3>
        <div className="h-96">
          <Pie data={voiceQualityData} options={chartOptions} />
        </div>
        <div className="mt-4 space-y-2">
          <p>Jitter: {analysis.voice_quality.jitter}</p>
          <p>Shimmer: {analysis.voice_quality.shimmer}</p>
          <p>Quality Score: {analysis.voice_quality.voice_quality_score}</p>
        </div>
      </div>

      {/* Speech Patterns */}
      <div className="bg-surface p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4 text-primary">Speech Patterns</h3>
        <div className="h-96">
          <Bar data={speechPatternsData} options={chartOptions} />
        </div>
        <div className="mt-4 space-y-2">
          <p>Pause Count: {analysis.speech_patterns.pause_count}</p>
          <p>Avg Pause Duration: {analysis.speech_patterns.average_pause_duration}s</p>
          <p>Word Rate: {analysis.speech_patterns.word_rate} words/s</p>
        </div>
      </div>

      {/* Emotion Analysis */}
      <div className="bg-surface p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4 text-primary">Emotion Analysis</h3>
        <div className="h-96">
          <Pie data={emotionData} options={chartOptions} />
        </div>
        <div className="mt-4 space-y-2">
          <p>Detected Emotion: {analysis.emotion_analysis.detected_emotion}</p>
          <p>Emotional Intensity: {getEmotionLabel(analysis.emotion_analysis.emotional_intensity)}</p>
          <p>Intensity Value: {analysis.emotion_analysis.emotional_intensity.toFixed(2)}</p>
        </div>
      </div>
    </div>
  );
};

export default AudioAnalysisVisualization; 