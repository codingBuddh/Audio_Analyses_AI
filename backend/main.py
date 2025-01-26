from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import numpy as np
import speech_recognition as sr
from yt_dlp import YoutubeDL
from deep_translator import GoogleTranslator
from pydantic import BaseModel
import torch
import warnings
import librosa
from transformers import pipeline, AutoModelForAudioClassification, AutoFeatureExtractor
import soundfile as sf
from langchain_community.document_loaders.youtube import YoutubeLoader, TranscriptFormat
from langchain_community.document_loaders import YoutubeLoader

warnings.filterwarnings("ignore")

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_CACHE = None
FEATURE_EXTRACTOR_CACHE = None

def load_model():
    global MODEL_CACHE, FEATURE_EXTRACTOR_CACHE
    if MODEL_CACHE is None:
        cache_dir = "./model_cache"
        os.makedirs(cache_dir, exist_ok=True)
        MODEL_CACHE = AutoModelForAudioClassification.from_pretrained(
            "superb/hubert-base-superb-er",
            cache_dir=cache_dir
        )
        FEATURE_EXTRACTOR_CACHE = AutoFeatureExtractor.from_pretrained(
            "superb/hubert-base-superb-er",
            cache_dir=cache_dir
        )
    return MODEL_CACHE, FEATURE_EXTRACTOR_CACHE

def download_youtube_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename.replace('.webm', '.wav').replace('.m4a', '.wav')

def transcribe_and_translate(audio_path, target_lang='es'):
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        
    try:
        text = recognizer.recognize_google(audio_data, language='en-US')
        translation = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return text, translation
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Could not understand audio")
    except sr.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Speech recognition error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

class ProcessRequest(BaseModel):
    url: str
    target_lang: str = 'es'

    class Config:
        extra = "forbid"

@app.post("/process")
async def process_video(request: ProcessRequest):
    try:
        audio_file = download_youtube_audio(request.url)
        transcript = get_youtube_transcript(request.url)
        return {
            "transcript": transcript,
            "audio_file": audio_file
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AudioAnalyzer:
    def __init__(self, audio_path):
        self.device = 'cpu'
        if torch.backends.mps.is_available():
            self.device = 'cpu'
        elif torch.cuda.is_available():
            self.device = 'cuda'
            
        self.audio_path = audio_path
        # Use soundfile to load audio
        self.y, self.sr = sf.read(audio_path)
        # Convert to mono if stereo
        if len(self.y.shape) > 1:
            self.y = np.mean(self.y, axis=1)
        # Resample to 16000 if needed
        if self.sr != 16000:
            self.y = librosa.resample(self.y, orig_sr=self.sr, target_sr=16000)
            self.sr = 16000
        self.duration = librosa.get_duration(y=self.y, sr=self.sr)
        
        # Load the model once
        self.model, self.feature_extractor = load_model()
        self.model.to(self.device)
        
    def analyze_prosody(self):
        y_np = self.y.astype(np.float32)
        pitch = librosa.yin(y_np, fmin=50, fmax=2000, sr=self.sr)
        valid_pitch = pitch[pitch > 0]
        return {
            'pitch_variation': np.std(valid_pitch) if len(valid_pitch) > 0 else 0,
            'mean_pitch': np.mean(valid_pitch) if len(valid_pitch) > 0 else 0
        }
    
    def analyze_rhythm(self):
        tempo, beat_frames = librosa.beat.beat_track(
            y=self.y.astype(np.float32), 
            sr=self.sr,
            units='time'
        )
        return {'tempo': tempo, 'beat_count': len(beat_frames)}
    
    def analyze_speech_clarity(self):
        rms = librosa.feature.rms(y=self.y.astype(np.float32))
        return {
            'rms_mean': float(np.mean(rms)),
            'rms_variance': float(np.var(rms))
        }
    
    def analyze_emotion(self):
        try:
            inputs = self.feature_extractor(
                self.y,
                sampling_rate=self.sr,
                return_tensors="pt"
            ).to(self.device)
            with torch.no_grad():
                logits = self.model(**inputs).logits
            probs = torch.nn.functional.softmax(logits, dim=-1)
            results = [
                {"label": self.model.config.id2label[i], "score": float(score.item())}
                for i, score in enumerate(probs[0])
            ]
            return sorted(results, key=lambda x: x["score"], reverse=True)
        except Exception as e:
            print(f"Error in emotion analysis: {str(e)}")
            return []
    
    def generate_report(self):
        return {
            'prosody': self.analyze_prosody(),
            'rhythm': self.analyze_rhythm(),
            'clarity': self.analyze_speech_clarity(),
            'emotion': self.analyze_emotion()
        }

@app.post("/analyze")
async def analyze_audio(audio_path: str):
    try:
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        analyzer = AudioAnalyzer(audio_path)
        report = analyzer.generate_report()
        return report
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Audio analysis error: {str(e)}"
        )

def get_youtube_transcript(url):
    try:
        loader = YoutubeLoader.from_youtube_url(
            url,
            add_video_info=False,
            transcript_format=TranscriptFormat.CHUNKS,
            chunk_size_seconds=30
        )
        documents = loader.load()
        return [{
            "text": doc.page_content,
            "start_seconds": doc.metadata['start_seconds'],
            "start_timestamp": doc.metadata['start_timestamp']
        } for doc in documents]
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get transcript: {str(e)}"
        )

@app.post("/transcribe")
async def transcribe_video(request: ProcessRequest):
    try:
        transcript = get_youtube_transcript(request.url)
        return {
            "transcript": transcript,
            "audio_file": download_youtube_audio(request.url)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 