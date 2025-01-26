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

    def analyze_speech_clarity(self, audio_file_path: str, transcript: str) -> Dict[str, float]:
        """Analyze speech clarity using various metrics."""
        sample_rate, data = wavfile.read(audio_file_path)
        if len(data.shape) > 1:
            data = data.mean(axis=1)  # Convert stereo to mono
            
        # Calculate zero-crossing rate
        zero_crossings = np.sum(np.abs(np.diff(np.sign(data)))) / len(data)
        
        # Calculate spectral centroid
        spectrum = np.abs(rfft(data))
        frequencies = rfftfreq(len(data), 1/sample_rate)
        spectral_centroid = np.sum(frequencies * spectrum) / np.sum(spectrum)
        
        return {
            "zero_crossing_rate": float(zero_crossings),
            "spectral_centroid": float(spectral_centroid),
            "clarity_score": float(1 - (zero_crossings / spectral_centroid))  # Example metric
        }

    def analyze_voice_quality(self, audio_file_path: str) -> Dict[str, float]:
        """Analyze voice quality using various metrics."""
        sample_rate, data = wavfile.read(audio_file_path)
        if len(data.shape) > 1:
            data = data.mean(axis=1)  # Convert stereo to mono
            
        # Calculate jitter (pitch period variations)
        peaks, _ = find_peaks(data, height=np.max(data)*0.5)
        if len(peaks) > 1:
            jitter = np.std(np.diff(peaks)) / np.mean(np.diff(peaks))
        else:
            jitter = 0.0
        
        # Calculate shimmer (amplitude variations)
        if len(peaks) > 1:
            shimmer = np.std(data[peaks]) / np.mean(data[peaks])
        else:
            shimmer = 0.0
        
        return {
            "jitter": float(jitter),
            "shimmer": float(shimmer),
            "voice_quality_score": float(1 - (jitter + shimmer))  # Example metric
        }

    def analyze_emotion(self, audio_file_path: str) -> Dict[str, float]:
        """Analyze emotional content using pitch and energy features."""
        sample_rate, data = wavfile.read(audio_file_path)
        if len(data.shape) > 1:
            data = data.mean(axis=1)  # Convert stereo to mono
            
        # Calculate pitch and energy features
        spectrum = np.abs(rfft(data))
        pitch = np.argmax(spectrum)
        energy = np.mean(data**2)
        
        # Simple emotion detection based on pitch and energy
        emotion = "neutral"
        if pitch > 300 and energy > 0.1:
            emotion = "excited"
        elif pitch < 200 and energy < 0.05:
            emotion = "calm"
        
        return {
            "detected_emotion": emotion,
            "emotional_intensity": float(energy)
        }

    def analyze_speech_patterns(self, audio_file_path: str, transcript: str) -> Dict[str, float]:
        """Analyze speech patterns including pauses and rhythm."""
        sample_rate, data = wavfile.read(audio_file_path)
        if len(data.shape) > 1:
            data = data.mean(axis=1)  # Convert stereo to mono
            
        # Detect pauses
        silence_threshold = 0.02 * np.max(data)
        silent_intervals = np.where(data < silence_threshold)[0]
        pause_durations = np.diff(silent_intervals) / sample_rate
        
        # Calculate pause metrics
        pause_count = len(pause_durations)
        avg_pause_duration = np.mean(pause_durations) if pause_count > 0 else 0.0
        
        # Calculate speech rhythm
        words = word_tokenize(transcript)
        word_rate = len(words) / (len(data) / sample_rate)
        
        return {
            "pause_count": int(pause_count),
            "average_pause_duration": float(avg_pause_duration),
            "word_rate": float(word_rate)
        }

    def generate_report(self, audio_file_path: str, transcript: str) -> Dict[str, Any]:
        """Generate a comprehensive audio analysis report."""
        try:
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found at {audio_file_path}")
            
            sample_rate, data = wavfile.read(audio_file_path)
            audio_duration = len(data) / sample_rate
            
            return {
                "audio_analysis": {
                    "duration_seconds": float(audio_duration),
                    "speech_rate_wpm": self.measure_speech_rate(transcript, audio_duration),
                    "pitch_analysis": self.analyze_pitch_and_intonation(audio_file_path),
                    "signal_quality": self.measure_signal_quality(audio_file_path),
                    "speech_clarity": self.analyze_speech_clarity(audio_file_path, transcript),
                    "voice_quality": self.analyze_voice_quality(audio_file_path),
                    "emotion_analysis": self.analyze_emotion(audio_file_path),
                    "speech_patterns": self.analyze_speech_patterns(audio_file_path, transcript)
                }
            }
        except Exception as e:
            print(f"Error in generate_report: {str(e)}")
            raise 