"""Configuration management using Pydantic settings."""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class VectorStoreType(str, Enum):
    """Supported vector store types."""
    
    FAISS = "faiss"
    MILVUS = "milvus"
    CHROMA = "chroma"


class Environment(str, Enum):
    """Application environment."""
    
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # IBM watsonx.ai Configuration
    ibm_cloud_api_key: str = Field(..., description="IBM Cloud API key")
    ibm_watsonx_project_id: str = Field(..., description="watsonx.ai project ID")
    ibm_watsonx_url: str = Field(
        default="https://us-south.ml.cloud.ibm.com",
        description="watsonx.ai service URL"
    )
    llm_model: str = Field(
        default="ibm/granite-3-8b-instruct",
        description="IBM Granite model to use"
    )
    embedding_model: str = Field(
        default="ibm/slate-125m-english-rtrvr",
        description="IBM embedding model"
    )
    
    # IBM Cloud Object Storage (optional)
    ibm_cos_endpoint: Optional[str] = Field(
        default=None,
        description="IBM COS endpoint URL"
    )
    ibm_cos_api_key: Optional[str] = Field(
        default=None,
        description="IBM COS API key"
    )
    ibm_cos_instance_id: Optional[str] = Field(
        default=None,
        description="IBM COS instance ID"
    )
    ibm_cos_bucket_name: Optional[str] = Field(
        default="career-advisor-data",
        description="IBM COS bucket name"
    )
    max_tokens: int = Field(default=4096, description="Max tokens for LLM response")
    temperature: float = Field(default=0.7, description="LLM temperature")
    
    # Vector Store Configuration
    vector_store_type: VectorStoreType = Field(
        default=VectorStoreType.FAISS,
        description="Vector store backend"
    )
    milvus_host: str = Field(default="localhost", description="Milvus host")
    milvus_port: int = Field(default=19530, description="Milvus port")
    vector_dimension: int = Field(
        default=1536,
        description="Embedding vector dimension"
    )
    
    # Application Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment"
    )
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    
    # Search Configuration
    top_k_results: int = Field(default=5, description="Number of results to retrieve")
    similarity_threshold: float = Field(
        default=0.7,
        description="Minimum similarity score"
    )
    
    # Web Search (optional)
    serper_api_key: Optional[str] = Field(
        default=None,
        description="Serper API key for web search"
    )
    
    # Paths
    @property
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent
    
    @property
    def data_dir(self) -> Path:
        """Get data directory."""
        return self.project_root / "data"
    
    @property
    def raw_data_dir(self) -> Path:
        """Get raw data directory."""
        return self.data_dir / "raw"
    
    @property
    def processed_data_dir(self) -> Path:
        """Get processed data directory."""
        return self.data_dir / "processed"
    
    @property
    def vectors_dir(self) -> Path:
        """Get vectors directory."""
        return self.data_dir / "vectors"
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        for directory in [
            self.raw_data_dir,
            self.processed_data_dir,
            self.vectors_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

