"""IBM watsonx.ai Granite LLM client implementation.

This module provides a client for interacting with IBM's Granite models
through the watsonx.ai API. You'll implement the actual API calls here.

Key concepts:
- Use ibm-watsonx-ai SDK for model inference
- Handle authentication with IBM Cloud API key
- Implement retry logic for API failures
- Add token counting and cost tracking
"""

from typing import Any, Dict, List, Optional

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class GraniteLLMClient:
    """Client for IBM watsonx.ai Granite models.
    
    This class handles all interactions with the Granite LLM, including:
    - Authentication and session management
    - Prompt formatting and submission
    - Response parsing and error handling
    - Token usage tracking
    
    TODO: Implement the following methods:
    1. __init__: Initialize the watsonx.ai client with credentials
    2. generate: Send a prompt and get a response
    3. generate_with_context: Include retrieved context in the prompt
    4. _format_prompt: Format user query with system prompt and context
    5. _count_tokens: Estimate token usage for cost tracking
    """
    
    def __init__(self) -> None:
        """Initialize the Granite LLM client.
        
        Steps to implement:
        1. Import: from ibm_watsonx_ai.foundation_models import Model
        2. Set up credentials dict with API key and project ID
        3. Initialize the Model with:
           - model_id=settings.llm_model
           - credentials=your_credentials
           - project_id=settings.ibm_watsonx_project_id
        4. Store the model instance as self.model
        5. Log successful initialization
        
        Example structure:
            credentials = {
                "url": settings.ibm_watsonx_url,
                "apikey": settings.ibm_cloud_api_key
            }
            self.model = Model(
                model_id=settings.llm_model,
                credentials=credentials,
                project_id=settings.ibm_watsonx_project_id
            )
        """
        logger.info("Initializing Granite LLM client", model=settings.llm_model)
        
        # TODO: Implement initialization
        # self.model = ...
        
        logger.info("Granite LLM client initialized successfully")
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Generate a response from the Granite model.
        
        Args:
            prompt: The input prompt to send to the model
            max_tokens: Maximum tokens in response (uses config default if None)
            temperature: Sampling temperature (uses config default if None)
            
        Returns:
            Generated text response from the model
            
        Steps to implement:
        1. Set up generation parameters:
           - max_new_tokens: max_tokens or settings.max_tokens
           - temperature: temperature or settings.temperature
           - decoding_method: "greedy" or "sample"
        2. Call self.model.generate(prompt=prompt, params=params)
        3. Extract the generated text from the response
        4. Log token usage and response time
        5. Handle any API errors with try/except
        
        Example:
            params = {
                "max_new_tokens": max_tokens or settings.max_tokens,
                "temperature": temperature or settings.temperature,
                "decoding_method": "sample"
            }
            response = self.model.generate(prompt=prompt, params=params)
            return response["results"][0]["generated_text"]
        """
        logger.info("Generating response", prompt_length=len(prompt))
        
        # TODO: Implement generation logic
        # response = self.model.generate(...)
        
        return "TODO: Implement generation"
    
    def generate_with_context(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Generate a response using retrieved context (RAG pattern).
        
        Args:
            query: User's question
            context_chunks: List of retrieved document chunks with metadata
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Generated response incorporating the context
            
        Steps to implement:
        1. Format the context chunks into a readable string
        2. Build a prompt that includes:
           - System instructions (career advisor role)
           - The retrieved context
           - The user's query
        3. Call self.generate() with the formatted prompt
        4. Return the response
        
        Context format example:
            Context 1 (from CV):
            [content of chunk 1]
            
            Context 2 (from career guide):
            [content of chunk 2]
            
            Based on the above context, answer: {query}
        """
        logger.info(
            "Generating response with context",
            query=query,
            num_contexts=len(context_chunks)
        )
        
        # TODO: Implement context-aware generation
        # formatted_prompt = self._format_prompt(query, context_chunks)
        # return self.generate(formatted_prompt, max_tokens, temperature)
        
        return "TODO: Implement context-aware generation"
    
    def _format_prompt(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]]
    ) -> str:
        """Format the prompt with system instructions and context.
        
        Args:
            query: User's question
            context_chunks: Retrieved context chunks
            
        Returns:
            Formatted prompt string
            
        Steps to implement:
        1. Start with a system prompt defining the AI's role
        2. Add each context chunk with source metadata
        3. Add the user's query at the end
        4. Ensure clear separation between sections
        
        Prompt structure:
            You are an AI career advisor...
            
            Context:
            [contexts here]
            
            Question: {query}
            
            Answer:
        """
        # TODO: Implement prompt formatting
        return f"TODO: Format prompt for query: {query}"
    
    def _count_tokens(self, text: str) -> int:
        """Estimate token count for a text string.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
            
        Steps to implement:
        1. Use tiktoken library for accurate counting
        2. Or use a simple approximation: len(text) / 4
        3. Log token counts for monitoring
        
        Example with tiktoken:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        """
        # Simple approximation: ~4 characters per token
        return len(text) // 4

# Made with Bob
