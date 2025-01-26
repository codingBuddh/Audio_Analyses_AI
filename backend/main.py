from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders.youtube import YoutubeLoader, TranscriptFormat
from translation_service import TranslationService
from fastapi.responses import StreamingResponse
import json
import asyncio

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

class ProcessRequest(BaseModel):
    url: str

class TranslateRequest(BaseModel):
    transcript: list[dict]
    target_language: str

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
        transcript = get_youtube_transcript(request.url)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate")
async def translate_transcript(
    request: TranslateRequest,
    service: TranslationService = Depends(lambda: translation_service)
):
    async def generate():
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
    
    return StreamingResponse(generate(), media_type="text/event-stream") 