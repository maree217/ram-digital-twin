import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Google Cloud & Gemini
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    google_cloud_project: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    
    # Pinecone
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "ram-knowledge-base")
    
    # Firebase
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    firebase_private_key_id: str = os.getenv("FIREBASE_PRIVATE_KEY_ID", "")
    firebase_private_key: str = os.getenv("FIREBASE_PRIVATE_KEY", "")
    firebase_client_email: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    firebase_client_id: str = os.getenv("FIREBASE_CLIENT_ID", "")
    
    # Application
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"

settings = Settings()