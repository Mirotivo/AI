"""Speech-to-Text module using Faster Whisper."""

import logging
import queue
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
import torch
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class SpeechToText:
    """Handles speech-to-text conversion using Faster Whisper."""

    def __init__(self, model_name='base', device='cpu', use_vad=False):
        """
        Initialize Whisper model.

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on (cpu or cuda)
            use_vad: Enable Voice Activity Detection
        """
        logger.info(f"Loading Faster Whisper model: {model_name}")
        self.model_name = model_name
        self.device = device
        # faster-whisper uses different device specification
        compute_type = "int8" if device == "cpu" else "float16"
        self.model = WhisperModel(
            model_name, device=device, compute_type=compute_type
        )
        logger.info("Faster Whisper model loaded successfully")

        # Initialize VAD if enabled
        self.use_vad = use_vad
        self.vad_model = None
        if use_vad:
            logger.info("Loading Silero VAD model...")
            self.vad_model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            self.get_speech_timestamps = utils[0]
            logger.info("Silero VAD model loaded successfully")
    
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
        if self.use_vad:
            return self.record_with_vad(sample_rate, channels, max_duration=30)
        
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
    
    def record_with_vad(self, sample_rate=16000, channels=1, max_duration=30):
        """
        Record audio with Silero VAD - stops when you stop speaking.
        
        Args:
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            max_duration: Maximum recording duration in seconds
            
        Returns:
            numpy array of audio data
        """
        logger.info("Recording with Silero VAD...")
        print(f"\n🎤 Listening... (speak naturally, pause when done)")
        
        all_audio = []
        silence_chunks = 0
        silence_threshold = 30  # ~1 second of silence at 512 samples/chunk
        speech_detected = False
        min_speech_chunks = 5  # Minimum chunks before we start counting silence
        speech_chunks = 0
        
        # Silero VAD requires exactly 512 samples for 16kHz
        samples_per_chunk = 512
        # Use a queue to handle audio chunks from the stream
        audio_queue = queue.Queue()
        
        def audio_callback(indata, frames, time_info, status):
            """Callback for audio stream."""
            if status:
                logger.warning(f"Audio callback status: {status}")
            # Put a copy of the audio data in the queue
            audio_queue.put(indata.copy())
        
        # Start recording with input stream
        start_time = time.time()
        
        try:
            with sd.InputStream(
                samplerate=sample_rate,
                channels=channels,
                dtype='float32',
                blocksize=samples_per_chunk,
                callback=audio_callback
            ):
                while (time.time() - start_time) < max_duration:
                    try:
                        # Get chunk from queue with timeout
                        chunk = audio_queue.get(timeout=1.0)
                        all_audio.append(chunk)
                        
                        # Convert chunk to proper format for Silero VAD
                        chunk_array = chunk.flatten().astype(np.float32)
                        
                        # Ensure we have exactly 512 samples
                        if len(chunk_array) != samples_per_chunk:
                            # Pad or trim to exact size
                            if len(chunk_array) < samples_per_chunk:
                                chunk_array = np.pad(
                                    chunk_array, 
                                    (0, samples_per_chunk - len(chunk_array)),
                                    mode='constant'
                                )
                            else:
                                chunk_array = chunk_array[:samples_per_chunk]
                        
                        chunk_tensor = torch.from_numpy(chunk_array)
                        
                        # Detect speech using Silero VAD
                        speech_prob = self.vad_model(
                            chunk_tensor, sample_rate
                        ).item()
                        # Speech detection with better threshold
                        if speech_prob > 0.5:  # Higher confidence threshold
                            speech_detected = True
                            speech_chunks += 1
                            silence_chunks = 0
                            # Print less frequently for cleaner output
                            if speech_chunks % 5 == 0:
                                print("🟢", end="", flush=True)
                        elif (speech_detected and
                              speech_chunks >= min_speech_chunks):
                            # Only start counting silence after minimum speech
                            silence_chunks += 1
                            # Print less frequently for cleaner output
                            if silence_chunks % 5 == 0:
                                print("⚪", end="", flush=True)
                            
                            if silence_chunks >= silence_threshold:
                                print()  # New line before the log message
                                logger.info(
                                    "Silence detected after speech, stopping..."
                                )
                                break
                        else:
                            # Waiting for speech to start
                            # Print very infrequently when waiting
                            if len(all_audio) % 20 == 0:
                                print("⚫", end="", flush=True)
                        
                    except queue.Empty:
                        logger.warning("Audio queue timeout")
                        break
                    except Exception as e:
                        logger.error(f"VAD error: {e}")
                        print()
                        break
        
        except Exception as e:
            logger.error(f"Recording stream error: {e}")
            print(f"\n❌ Recording error: {e}")
        
        print()
        
        # Combine all chunks
        if all_audio:
            audio = np.concatenate(all_audio, axis=0)
            duration = len(audio) / sample_rate
            logger.info(f"Recording complete: {duration:.1f} seconds")
            print(f"✅ Recorded {duration:.1f} seconds")
            return audio
        else:
            logger.warning("No audio recorded")
            return np.array([])
    
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
        
        # faster-whisper returns segments and info
        segments, info = self.model.transcribe(
            audio_array,
            language=language
        )
        
        # Combine all segments into full text
        text = " ".join([segment.text for segment in segments]).strip()
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
