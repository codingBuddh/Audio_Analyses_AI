import numpy as np
from scipy.io import wavfile
from scipy.signal import find_peaks
from scipy.fft import rfft, rfftfreq
import nltk
from nltk.tokenize import word_tokenize
from typing import Dict, Any
import os

# Download NLTK data
nltk.download('punkt')

class AnalyzeAudioService:
    def __init__(self):
        self.sample_rate = 22050  # Default sample rate for analysis

    def calculate_word_accuracy_rate(self, recognized_text: str, reference_text: str) -> float:
        """Calculate Word Accuracy Rate (WAR)."""
        recognized_words = word_tokenize(recognized_text.lower())
        reference_words = word_tokenize(reference_text.lower())

        total_words = len(reference_words)
        if total_words == 0:
            return 0.0

        correct_count = sum(1 for rw, tw in zip(recognized_words, reference_words) if rw == tw)
        return (correct_count / total_words) * 100

    def measure_speech_rate(self, recognized_text: str, audio_duration: float) -> float:
        """Estimate speech rate in Words Per Minute (WPM)."""
        words = word_tokenize(recognized_text)
        return (len(words) / audio_duration) * 60 if audio_duration > 0 else 0.0

    def analyze_pitch_and_intonation(self, audio_file_path: str) -> Dict[str, float]:
        """Analyze pitch (F0) and basic intonation using FFT."""
        sample_rate, data = wavfile.read(audio_file_path)
        if len(data.shape) > 1:
            data = data.mean(axis=1)  # Convert stereo to mono
            
        # Apply FFT
        N = len(data)
        yf = rfft(data)
        xf = rfftfreq(N, 1 / sample_rate)
        
        # Find dominant frequencies
        peaks, _ = find_peaks(np.abs(yf), height=np.max(np.abs(yf)) * 0.1)
        if len(peaks) == 0:
            return {
                "average_pitch": 0.0,
                "pitch_variability": 0.0,
                "pitch_range": 0.0
            }
            
        dominant_frequencies = xf[peaks]
        
        return {
            "average_pitch": float(np.mean(dominant_frequencies)),
            "pitch_variability": float(np.std(dominant_frequencies)),
            "pitch_range": float(np.max(dominant_frequencies) - np.min(dominant_frequencies))
        }

    def measure_signal_quality(self, audio_file_path: str) -> Dict[str, float]:
        """Measure signal quality by estimating SNR using RMS."""
        sample_rate, data = wavfile.read(audio_file_path)
        if len(data.shape) > 1:
            data = data.mean(axis=1)  # Convert stereo to mono
            
        rms = np.sqrt(np.mean(data**2))
        sorted_data = np.sort(np.abs(data))
        cutoff = int(0.1 * len(sorted_data))
        if cutoff == 0:
            cutoff = 1
        noise_floor = np.mean(sorted_data[:cutoff])
        
        if noise_floor == 0:
            noise_floor = 1e-10  # avoid division by zero

        signal_noise_ratio = rms / noise_floor
        
        return {
            "average_rms": float(rms),
            "noise_floor": float(noise_floor),
            "signal_to_noise_ratio": float(signal_noise_ratio)
        }

    def generate_report(self, audio_file_path: str, transcript: str) -> Dict[str, Any]:
        """Generate a comprehensive audio analysis report."""
        try:
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found at {audio_file_path}")
            
            sample_rate, data = wavfile.read(audio_file_path)
            audio_duration = len(data) / sample_rate
            
            pitch_info = self.analyze_pitch_and_intonation(audio_file_path)
            signal_info = self.measure_signal_quality(audio_file_path)

            return {
                "audio_analysis": {
                    "duration_seconds": float(audio_duration),
                    "speech_rate_wpm": self.measure_speech_rate(transcript, audio_duration),
                    "pitch_analysis": pitch_info,
                    "signal_quality": signal_info
                }
            }
        except Exception as e:
            print(f"Error in generate_report: {str(e)}")
            raise 