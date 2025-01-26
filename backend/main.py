from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders.youtube import YoutubeLoader, TranscriptFormat
from translation_service import TranslationService
from fastapi.responses import StreamingResponse
import json
import asyncio
import os
from audio_analysis_service import AnalyzeAudioService
from pathlib import Path
from yt_dlp import YoutubeDL
from pydub import AudioSegment

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize translation service
translation_service = TranslationService()

# Initialize audio analysis service
audio_analysis_service = AnalyzeAudioService()

# Create audio directory if it doesn't exist
audio_dir = Path("audio")
audio_dir.mkdir(exist_ok=True)

def download_audio(url: str, output_path: str) -> str:
    try:
        # Ensure the audio directory exists
        audio_dir = Path("audio")
        audio_dir.mkdir(exist_ok=True)
        
        # Create full output path
        full_output_path = str(audio_dir / output_path)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': full_output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)
            
            # The file is already saved as WAV in the audio folder
            wav_path = f"{full_output_path}.wav"
            
            return wav_path
    except Exception as e:
        print(f"Error downloading audio: {str(e)}")
        raise

class ProcessRequest(BaseModel):
    url: str

class TranslateRequest(BaseModel):
    transcript: list[dict]
    target_language: str

class AnalyzeRequest(BaseModel):
    audio_path: str
    transcript: str

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

@app.post("/process")
async def process_video(request: ProcessRequest):
    try:
        # Get transcript
        transcript = get_youtube_transcript(request.url)
        
        # Download audio
        video_id = request.url.split('=')[-1]
        audio_path = download_audio(request.url, video_id)
        
        return {
            "transcript": transcript,
            "audio_path": audio_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate")
async def translate_transcript(
    request: TranslateRequest,
    service: TranslationService = Depends(lambda: translation_service)
):
    async def generate():
        try:
            for segment in request.transcript:
                translated_text = await service.translate(segment["text"], request.target_language)
                for char in translated_text:
                    yield f"data: {json.dumps({
                        'original': segment,
                        'translated': {
                            'char': char,
                            'start_seconds': segment['start_seconds'],
                            'start_timestamp': segment['start_timestamp']
                        }
                    })}\n\n"
        finally:
            yield "data: [DONE]\n\n"  # Signal completion
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/analyze")
async def analyze_audio(request: AnalyzeRequest):
    try:
        if not os.path.exists(request.audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Create audio directory if it doesn't exist
        os.makedirs(os.path.dirname(request.audio_path), exist_ok=True)
        
        return audio_analysis_service.generate_report(
            request.audio_path,
            request.transcript
        )
    except Exception as e:
        print(f"Error in analyze_audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 