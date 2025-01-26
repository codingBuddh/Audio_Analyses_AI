## Getting Started

### Prerequisites

1. Python 3.8+
2. Node.js 16+
3. Ollama installed and running locally
4. llama3.2:latest model downloaded

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/youtube-translator.git
   cd youtube-translator
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   ```

4. Create a `.env` file in the backend directory:
   ```env
   LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
   LANGSMITH_API_KEY="your_langsmith_key"
   LANGSMITH_PROJECT="your_project_name"
   ```

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. Start the frontend development server:
   ```bash
   cd ../frontend
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

## Usage

1. Enter a YouTube URL in the input field
2. Click "Submit" to extract the transcript
3. Select a target language from the dropdown
4. Click "Translate" to start the translation
5. View both original and translated transcripts side by side

## Technology Stack

### Backend
- **FastAPI**: Python web framework for building APIs
- **LangChain**: Framework for working with language models
- **Ollama**: Local language model for translations
- **YouTube Transcript API**: For extracting YouTube transcripts

### Frontend
- **React**: JavaScript library for building user interfaces
- **CSS**: For styling the application
- **Fetch API**: For making HTTP requests to the backend

## Configuration

The application can be configured through the following environment variables:

- `LANGSMITH_ENDPOINT`: LangSmith API endpoint
- `LANGSMITH_API_KEY`: LangSmith API key
- `LANGSMITH_PROJECT`: LangSmith project name

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Ollama for providing the local language model
- YouTube Transcript API for easy transcript extraction
- FastAPI and React communities for their excellent documentation

### New Endpoint: Audio Analysis

**POST /analyze**

Analyzes the audio file and provides a detailed report.

**Request Body:**
```json
{
    "audio_path": "path/to/audio.wav",
    "transcript": "The full transcript text"
}
```

**Response:**
```json
{
    "audio_analysis": {
        "duration_seconds": 120.5,
        "speech_rate_wpm": 150.2,
        "pitch_analysis": {
            "average_pitch": 220.5,
            "pitch_variability": 15.2,
            "pitch_range": 100.3
        },
        "signal_quality": {
            "average_rms": 0.15,
            "noise_floor": 0.01,
            "signal_to_noise_ratio": 15.0
        }
    }
}
```
```

This updated README provides:

1. A clear overview of the project
2. Detailed installation and setup instructions
3. Usage guide
4. Technology stack information
5. Configuration details
6. Contribution guidelines
7. License information
8. Acknowledgments

It should help users understand and use the application effectively while also providing necessary information for contributors.
```

This updated README provides:

1. A clear overview of the project
2. Detailed installation and setup instructions
3. Usage guide
4. Technology stack information
5. Configuration details
6. Contribution guidelines
7. License information
8. Acknowledgments

It should help users understand and use the application effectively while also providing necessary information for contributors.