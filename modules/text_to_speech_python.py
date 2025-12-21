"""Text-to-Speech module using Piper Python library."""

import logging
import numpy as np
import sounddevice as sd
from pathlib import Path
from piper.voice import PiperVoice

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Handles text-to-speech conversion using Piper Python library."""
    
    def __init__(self, piper_executable=None, voice_model_path=None):
        """
        Initialize Piper TTS with Python library.
        
        Args:
            piper_executable: Not used (kept for compatibility)
            voice_model_path: Path to voice model (.onnx file)
        """
        self.voice_model_path = Path(voice_model_path)
        
        if not self.voice_model_path.exists():
            raise FileNotFoundError(f"Voice model not found: {self.voice_model_path}")
        
        logger.info(f"Loading Piper voice model: {self.voice_model_path}")
        self.voice = PiperVoice.load(str(self.voice_model_path))
        self.sample_rate = self.voice.config.sample_rate
        logger.info(f"Piper voice loaded successfully: {self.voice_model_path.stem}, Sample rate: {self.sample_rate} Hz")
    
    def synthesize(self, text, output_file=None):
        """
        Convert text to speech.
        
        Args:
            text: Text to convert to speech
            output_file: Path to save audio file (optional)
            
        Returns:
            Audio data as numpy array
        """
        logger.info(f"Synthesizing: {text[:50]}...")
        print("🗣️ Generating speech...")
        
        # Extract audio bytes from AudioChunk objects
        audio_bytes_list = []
        for audio_chunk in self.voice.synthesize(text):
            audio_bytes_list.append(audio_chunk.audio_int16_bytes)
        
        # Combine all PCM data
        if audio_bytes_list:
            all_pcm = b''.join(audio_bytes_list)
            audio_array = np.frombuffer(all_pcm, dtype=np.int16).astype(np.float32)
            audio_array = audio_array / 32768.0  # Normalize to [-1, 1]
        else:
            audio_array = np.array([], dtype=np.float32)
            logger.warning("No audio data generated!")
        
        # Save to file if requested
        if output_file and len(audio_array) > 0:
            import soundfile as sf
            sf.write(output_file, audio_array, self.sample_rate)
            logger.info(f"Audio saved to: {output_file}")
        
        logger.info(f"✅ Audio generated: {len(audio_array)} samples")
        return audio_array
    
    def speak(self, text, cleanup=True):
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to speak
            cleanup: Not used (kept for compatibility)
        """
        audio_data = self.synthesize(text)
        
        if len(audio_data) == 0:
            logger.warning("No audio to play")
            return
        
        print("🔊 Speaking...")
        try:
            sd.play(audio_data, self.sample_rate)
            sd.wait()
            logger.info("✅ Playback complete")
        except Exception as e:
            logger.warning(f"Audio playback unavailable: {e}")
            print(f"⚠️  Audio device not available")
    
    def save_speech(self, text, output_path):
        """
        Convert text to speech and save to file.
        
        Args:
            text: Text to convert
            output_path: Path to save audio file
            
        Returns:
            Path to saved audio file
        """
        self.synthesize(text, output_file=output_path)
        return output_path
