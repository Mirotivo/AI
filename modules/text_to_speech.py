"""Text-to-Speech module using Piper executable."""

import logging
import os
import subprocess
import tempfile
from pathlib import Path
import sounddevice as sd
import soundfile as sf

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Handles text-to-speech conversion using Piper executable."""
    
    def __init__(self, piper_executable, voice_model_path):
        """
        Initialize Piper TTS.
        
        Args:
            piper_executable: Path to Piper executable
            voice_model_path: Path to voice model (.onnx file)
        """
        self.piper_executable = Path(piper_executable)
        self.voice_model_path = Path(voice_model_path)
        
        if not self.piper_executable.exists():
            raise FileNotFoundError(f"Piper executable not found: {self.piper_executable}")
        if not self.voice_model_path.exists():
            raise FileNotFoundError(f"Voice model not found: {self.voice_model_path}")
        
        logger.info(f"Initialized TTS with voice: {self.voice_model_path.stem}")
    
    def synthesize(self, text, output_file=None):
        """
        Convert text to speech.
        
        Args:
            text: Text to convert to speech
            output_file: Path to save audio file (optional)
            
        Returns:
            Path to generated audio file
        """
        if output_file is None:
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            output_file = temp_file.name
            temp_file.close()
        
        logger.info(f"Synthesizing: {text[:50]}...")
        print("🗣️ Generating speech...")
        
        # Build Piper command
        cmd = [
            str(self.piper_executable),
            '--model', str(self.voice_model_path),
            '--output_file', output_file
        ]
        
        # Run Piper with text as input
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        stdout, stderr = process.communicate(input=text)
        
        if process.returncode != 0:
            logger.error(f"Piper error: {stderr}")
            raise RuntimeError(f"Piper failed: {stderr}")
        
        logger.info(f"Audio generated: {output_file}")
        return output_file
    
    def speak(self, text, cleanup=True):
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to speak
            cleanup: Whether to delete the audio file after playing
        """
        audio_file = self.synthesize(text)
        
        print("🔊 Speaking...")
        try:
            data, samplerate = sf.read(audio_file)
            sd.play(data, samplerate)
            sd.wait()
            logger.info("✅ Playback complete")
        except Exception as e:
            logger.warning(f"Audio playback unavailable: {e}")
            print(f"⚠️  Audio device not available")
        
        # Cleanup temp file
        if cleanup:
            try:
                os.unlink(audio_file)
            except Exception as e:
                logger.warning(f"Could not delete temp file: {e}")
    
    def save_speech(self, text, output_path):
        """
        Convert text to speech and save to file.
        
        Args:
            text: Text to convert
            output_path: Path to save audio file
            
        Returns:
            Path to saved audio file
        """
        return self.synthesize(text, output_file=output_path)
