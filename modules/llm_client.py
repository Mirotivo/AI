"""LLM Client module for Ollama integration."""

import json
import logging
import requests

logger = logging.getLogger(__name__)


class LLMClient:
    """Handles communication with Ollama LLM server."""
    
    def __init__(self, base_url='http://localhost:11434', model='llama3.2:3b', system_prompt=None):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Base URL for Ollama API
            model: Model name to use
            system_prompt: System prompt for the assistant
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.system_prompt = system_prompt or "You are a helpful AI assistant. Keep responses concise and natural."
        self.conversation_history = []
        logger.info(f"Initialized LLM client with model: {model}")
    
    def check_connection(self):
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Cannot connect to Ollama: {e}")
            return False
    
    def list_models(self):
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def generate(self, prompt, stream=False):
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User prompt/question
            stream: Whether to stream the response
            
        Returns:
            Generated text response
        """
        logger.info(f"Generating response for: {prompt}")
        print("🤔 Thinking...")
        
        # Build messages with system prompt and history
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": stream
                },
                timeout=120
            )
            response.raise_for_status()
            
            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if 'message' in data:
                            content = data['message'].get('content', '')
                            full_response += content
                            print(content, end='', flush=True)
                print()  # New line after streaming
                result = full_response
            else:
                # Handle non-streaming response
                data = response.json()
                result = data.get('message', {}).get('content', '').strip()
            
            logger.info(f"Response: {result[:100]}...")
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": result})
            
            # Keep only last 10 messages to prevent context overflow
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Request to Ollama timed out")
            return "I'm sorry, I'm taking too long to respond. Please try again."
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I encountered an error: {str(e)}"
    
    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")
        print("🔄 Conversation reset")
    
    def set_system_prompt(self, prompt):
        """Update system prompt."""
        self.system_prompt = prompt
        logger.info(f"System prompt updated: {prompt}")
