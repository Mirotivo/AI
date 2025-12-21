"""Speech-to-Text module using Whisper."""

import logging
import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper

logger = logging.getLogger(__name__)


class SpeechToText:
    """Handles speech-to-text conversion using Whisper."""
    
    def __init__(self, model_name='base', device='cpu'):
        """
        Initialize Whisper model.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on (cpu or cuda)
        """
        logger.info(f"Loading Whisper model: {model_name}")
        self.model_name = model_name
        self.device = device
        self.model = whisper.load_model(model_name, device=device)
        logger.info("Whisper model loaded successfully")
    
    def record_audio(self, duration=5, sample_rate=16000, channels=1):
        """
        Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            
        Returns:
            numpy array of audio data
        """
        logger.info(f"Recording for {duration} seconds...")
        print(f"\n🎤 Listening for {duration} seconds...")
        
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype='float32'
        )
        sd.wait()
        
        logger.info("Recording complete")
        print("✅ Recording complete")
        return audio
    
    def transcribe(self, audio_data=None, audio_file=None, language='en'):
        """
        Transcribe audio to text.
        
        Args:
            audio_data: numpy array of audio data
            audio_file: path to audio file (alternative to audio_data)
            language: Language code for transcription
            
        Returns:
            Transcribed text string
        """
        if audio_data is not None:
            # Convert audio data to proper format for Whisper
            if audio_data.ndim > 1:
                audio_data = audio_data.mean(axis=1)
            
            audio_array = audio_data.flatten().astype(np.float32)
            logger.info(f"Transcribing audio data: {len(audio_array)} samples")
            
        elif audio_file is not None:
            # Load audio file
            logger.info(f"Loading audio from file: {audio_file}")
            audio_array, sample_rate = sf.read(audio_file)
            
            if audio_array.ndim > 1:
                audio_array = audio_array.mean(axis=1)
            
            audio_array = audio_array.flatten().astype(np.float32)
        else:
            raise ValueError("Either audio_data or audio_file must be provided")
        
        print("💭 Transcribing...")
        
        # Pass numpy array directly to Whisper (no file I/O needed!)
        result = self.model.transcribe(
            audio_array,
            language=language,
            fp16=False  # Use FP32 for CPU
        )
        
        text = result['text'].strip()
        logger.info(f"Transcription: {text}")
        return text
    
    def record_and_transcribe(self, duration=5, sample_rate=16000, channels=1):
        """
        Record audio and transcribe in one call.
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            
        Returns:
            Transcribed text string
        """
        audio = self.record_audio(duration, sample_rate, channels)
        return self.transcribe(audio_data=audio)
