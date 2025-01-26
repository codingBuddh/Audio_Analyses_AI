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

<edited_file>
README.md

<edits_to_file>
<human_edit>
```diff:README.md
  # YouTube Audio Transcription and Translation
  
- This project provides a web interface to download YouTube audio, transcribe it, and translate the transcription.
+ This project provides a web interface to download YouTube audio, extract its transcript, and translate the transcription using a local Ollama language model.
  
  ## Features
  
- - YouTube transcript extraction with timestamps
- - Chunked transcript display (30-second segments)
- - Improved audio analysis workflow
+ - **YouTube Transcript Extraction**: Automatically extracts transcripts from YouTube videos with timestamps
+ - **Real-time Translation**: Translates the transcript into multiple languages using a local Ollama model
+ - **Streaming Translation**: Displays translated text character by character for a smooth experience
+ - **Bilingual View**: Shows both original and translated transcripts side by side
+ - **Language Selection**: Supports translation to multiple languages (Spanish, French, German, Chinese)
  
  ## Project Structure
  
+ ```
+ youtube-translator/
+ ├── backend/
+ │   ├── main.py                # FastAPI server with endpoints
+ │   ├── translation_service.py # Translation service using Ollama
+ │   ├── requirements.txt       # Python dependencies
+ │   └── .env                  # Environment variables
+ ├── frontend/
+ │   ├── public/
+ │   ├── src/
+ │   │   ├── App.js            # Main React component
+ │   │   ├── App.css           # Styling
+ │   └── package.json          # Frontend dependencies
+ └── README.md                  # Project documentation
+ ```
  
  ## Getting Started
  
+ ### Prerequisites
+ 
+ 1. Python 3.8+
+ 2. Node.js 16+
+ 3. Ollama installed and running locally
+ 4. llama3.2:latest model downloaded
+ 
+ ### Installation
+ 
+ 1. Clone the repository:
+    ```bash
+    git clone https://github.com/yourusername/youtube-translator.git
+    cd youtube-translator
+    ```
+ 
+ 2. Set up the backend:
+    ```bash
+    cd backend
+    python -m venv venv
+    source venv/bin/activate  # On Windows: venv\Scripts\activate
+    pip install -r requirements.txt
+    ```
+ 
+ 3. Set up the frontend:
+    ```bash
+    cd ../frontend
+    npm install
+    ```
+ 
+ 4. Create a `.env` file in the backend directory:
+    ```env
+    LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
+    LANGSMITH_API_KEY="your_langsmith_key"
+    LANGSMITH_PROJECT="your_project_name"
+    ```
+ 
+ ### Running the Application
+ 
+ 1. Start the backend server:
+    ```bash
+    cd backend
+    uvicorn main:app --reload
+    ```
+ 
+ 2. Start the frontend development server:
+    ```bash
+    cd ../frontend
+    npm start
+    ```
+ 
+ 3. Open your browser and navigate to `http://localhost:3000`
  
  ## Usage
  
+ 1. Enter a YouTube URL in the input field
+ 2. Click "Submit" to extract the transcript
+ 3. Select a target language from the dropdown
+ 4. Click "Translate" to start the translation
+ 5. View both original and translated transcripts side by side
  
  ## Technology Stack
  
+ ### Backend
+ - **FastAPI**: Python web framework for building APIs
+ - **LangChain**: Framework for working with language models
+ - **Ollama**: Local language model for translations
+ - **YouTube Transcript API**: For extracting YouTube transcripts
+ 
+ ### Frontend
+ - **React**: JavaScript library for building user interfaces
+ - **CSS**: For styling the application
+ - **Fetch API**: For making HTTP requests to the backend
  
  ## Configuration
  
+ The application can be configured through the following environment variables:
+ 
+ - `LANGSMITH_ENDPOINT`: LangSmith API endpoint
+ - `LANGSMITH_API_KEY`: LangSmith API key
+ - `LANGSMITH_PROJECT`: LangSmith project name
  
  ## Contributing
  
+ Contributions are welcome! Please follow these steps:
+ 
+ 1. Fork the repository
+ 2. Create a new branch (`git checkout -b feature/YourFeature`)
+ 3. Commit your changes (`git commit -m 'Add some feature'`)
+ 4. Push to the branch (`git push origin feature`)