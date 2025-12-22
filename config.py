"""Configuration loader for the Voice Assistant."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Model Configuration
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
    PIPER_VOICE = os.getenv('PIPER_VOICE', 'en_US-lessac-medium')
    
    # Performance Settings
    WHISPER_DEVICE = os.getenv('WHISPER_DEVICE', 'cpu')
    OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    
    # Audio Settings
    RECORD_SECONDS = int(os.getenv('RECORD_SECONDS', '5'))
    SAMPLE_RATE = int(os.getenv('SAMPLE_RATE', '16000'))
    CHANNELS = int(os.getenv('CHANNELS', '1'))
    
    # System Prompt
    SYSTEM_PROMPT = os.getenv(
        'SYSTEM_PROMPT',
        'You are a helpful AI assistant. Keep responses concise and natural.'
    )
    
    # Modes
    CONTINUOUS_MODE = os.getenv('CONTINUOUS_MODE', 'false').lower() == 'true'
    TEXT_MODE = os.getenv('TEXT_MODE', 'false').lower() == 'true'
    USE_PYTHON_PIPER = os.getenv('USE_PYTHON_PIPER', 'true').lower() == 'true'
    USE_VAD = os.getenv('USE_VAD', 'false').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Paths
    BASE_DIR = Path(__file__).parent
    PIPER_DIR = BASE_DIR / 'piper'
    # Check if running in Docker or with nested piper directory
    if (PIPER_DIR / 'piper' / 'piper.exe').exists():
        PIPER_EXECUTABLE = PIPER_DIR / 'piper' / 'piper.exe'
    elif (PIPER_DIR / 'piper' / 'piper').exists():
        PIPER_EXECUTABLE = PIPER_DIR / 'piper' / 'piper'
    elif os.name == 'nt':
        PIPER_EXECUTABLE = PIPER_DIR / 'piper.exe'
    else:
        PIPER_EXECUTABLE = PIPER_DIR / 'piper'
    PIPER_VOICES_DIR = PIPER_DIR / 'voices'
    
    # Piper voice model path
    @property
    def piper_voice_path(self):
        """Get the full path to the Piper voice model."""
        return self.PIPER_VOICES_DIR / f"{self.PIPER_VOICE}.onnx"
    
    @classmethod
    def display(cls):
        """Display current configuration."""
        print("\n" + "="*50)
        print("CONFIGURATION")
        print("="*50)
        print("\n🤖 LLM (Ollama):")
        print(f"  Model:          {cls.OLLAMA_MODEL}")
        print(f"  URL:            {cls.OLLAMA_URL}")
        print("\n🎤 Speech-to-Text (Whisper):")
        print(f"  Model:          {cls.WHISPER_MODEL}")
        print(f"  Device:         {cls.WHISPER_DEVICE}")
        print(f"  VAD:            {cls.USE_VAD}")
        print("\n🔊 Text-to-Speech (Piper):")
        print(f"  Voice:          {cls.PIPER_VOICE}")
        print(f"  Python Mode:    {cls.USE_PYTHON_PIPER}")
        print("\n⚙️  Audio Settings:")
        print(f"  Sample Rate:    {cls.SAMPLE_RATE} Hz")
        print(f"  Record Time:    {cls.RECORD_SECONDS} seconds")
        print("\n🎛️  Mode Settings:")
        print(f"  Continuous:     {cls.CONTINUOUS_MODE}")
        print(f"  Text Only:      {cls.TEXT_MODE}")
        print("\n" + "="*50 + "\n")

# Create config instance
config = Config()
