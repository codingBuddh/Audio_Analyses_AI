import logging
import os
from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langsmith import Client
from dotenv import load_dotenv
from langchain_ollama.llms import OllamaLLM

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        try:
            logger.info("Initializing TranslationService...")
            
            # Configure environment variables
            langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
            langsmith_endpoint = os.getenv("LANGSMITH_ENDPOINT")
            langsmith_project = os.getenv("LANGSMITH_PROJECT")
            
            if not all([langsmith_api_key, langsmith_endpoint, langsmith_project]):
                raise ValueError("Missing required LangSmith configuration")
            
            os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
            os.environ["LANGSMITH_ENDPOINT"] = langsmith_endpoint
            os.environ["LANGSMITH_PROJECT"] = langsmith_project
            os.environ["LANGCHAIN_TRACING_V2"] = "true"

            # Initialize LangSmith client
            self.langsmith_client = Client()
            logger.info("LangSmith client initialized")
            
            # Initialize Ollama LLM
            self.llm = OllamaLLM(model="llama3.2:latest")
            logger.info("Ollama LLM initialized")
            
            # Translation prompt template
            self.translation_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert translator. Translate the following text to {target_language}.
                 Maintain the original meaning, tone, and style while ensuring natural and fluent output.
                 and must look like the actual trnslation and ad gaps as it is in the original text
                 dont write anything else other than just the translated text."""),
                ("user", "{text}")
            ])

            # Create the translation chain
            self.translation_chain = LLMChain(
                llm=self.llm,
                prompt=self.translation_prompt,
                verbose=True
            )
            logger.info("Translation service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing TranslationService: {str(e)}")
            raise

    async def translate(self, text: str, target_language: str) -> str:
        """Translate text to target language"""
        try:
            logger.info(f"Translating to {target_language}")
            response = await self.translation_chain.ainvoke(
                {
                    "text": text,
                    "target_language": target_language
                },
                config={
                    "tags": [os.getenv("LANGSMITH_PROJECT")],
                    "metadata": {
                        "operation": "translation",
                        "target_language": target_language
                    }
                }
            )
            return response["text"].strip()
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            raise

    def validate_openai_key(self, api_key: str) -> bool:
        """Validate the OpenAI API key format"""
        return api_key.startswith("sk-") and len(api_key) == 51 