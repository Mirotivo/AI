"""Main Voice Assistant Application."""

import logging
import sys
from colorama import init, Fore, Style

from config import config
from modules.llm_client import LLMClient
from modules.speech_to_text import SpeechToText
from modules.text_to_speech import TextToSpeech
from modules.text_to_speech_python import TextToSpeech as TextToSpeechPython

# Initialize colorama
init()

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VoiceAssistant:
    """Main Voice Assistant class."""
    
    def __init__(self):
        """Initialize the voice assistant."""
        self._print_header()
        config.display()
        self._initialize_components()
        print(f"{Fore.GREEN}✅ Voice Assistant initialized successfully!{Style.RESET_ALL}\n")
    
    def _print_header(self):
        """Print application header."""
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🤖  OFFLINE AI VOICE ASSISTANT  🤖{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    def _initialize_components(self):
        """Initialize all components."""
        try:
            # LLM Client
            print(f"{Fore.YELLOW}Initializing LLM Client...{Style.RESET_ALL}")
            self.llm = LLMClient(
                base_url=config.OLLAMA_URL,
                model=config.OLLAMA_MODEL,
                system_prompt=config.SYSTEM_PROMPT
            )
            print(f"{Fore.GREEN}✅ LLM Client initialized{Style.RESET_ALL}")
            
            if not self.llm.check_connection():
                print(f"{Fore.RED}⚠️  Warning: Cannot connect to Ollama at {config.OLLAMA_URL}{Style.RESET_ALL}")
            
            # Speech-to-Text (optional in TEXT_MODE)
            self.stt = self._init_speech_to_text()
            
            # Text-to-Speech
            self.tts = self._init_text_to_speech()
            
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            print(f"{Fore.RED}❌ Initialization failed: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    def _init_speech_to_text(self):
        """Initialize Speech-to-Text module."""
        if config.TEXT_MODE:
            print(f"{Fore.YELLOW}TEXT_MODE enabled - Skipping Speech-to-Text{Style.RESET_ALL}")
            return None
        
        print(f"{Fore.YELLOW}Initializing Speech-to-Text...{Style.RESET_ALL}")
        stt = SpeechToText(
            model_name=config.WHISPER_MODEL,
            device=config.WHISPER_DEVICE,
            use_vad=config.USE_VAD
        )
        print(f"{Fore.GREEN}✅ Speech-to-Text initialized{Style.RESET_ALL}")
        return stt
    
    def _init_text_to_speech(self):
        """Initialize Text-to-Speech module."""
        mode = "Python-based" if config.USE_PYTHON_PIPER else "Executable-based"
        print(f"{Fore.YELLOW}Initializing Text-to-Speech ({mode})...{Style.RESET_ALL}")
        
        TTS = TextToSpeechPython if config.USE_PYTHON_PIPER else TextToSpeech
        tts = TTS(
            piper_executable=config.PIPER_EXECUTABLE,
            voice_model_path=config.piper_voice_path
        )
        
        print(f"{Fore.GREEN}✅ Text-to-Speech initialized{Style.RESET_ALL}")
        return tts
    
    def run(self):
        """Run the voice assistant main loop."""
        try:
            self._show_instructions()
            
            while True:
                try:
                    if not self._process_interaction():
                        break
                    
                    if not self._should_continue():
                        break
                        
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
                    break
            
            print(f"\n{Fore.CYAN}👋 Goodbye!{Style.RESET_ALL}\n")
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    def _process_interaction(self):
        """Process one interaction. Returns False to exit, True to continue."""
        try:
            # Get user input
            user_input = self._get_user_input()
            
            if not user_input:
                return True
            
            if user_input == 'exit':
                return False
            
            # Generate and deliver response
            response = self.llm.generate(user_input)
            print(f"{Fore.GREEN}Assistant: {response}{Style.RESET_ALL}\n")
            
            self._speak_response(response)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing interaction: {e}")
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}\n")
            return True
    
    def _get_user_input(self):
        """Get user input (text or voice). Returns None, 'exit', or user text."""
        if config.TEXT_MODE:
            return self._get_text_input()
        else:
            return self._get_voice_input()
    
    def _get_text_input(self):
        """Get text input from user."""
        user_input = input(f"{Fore.CYAN}You: {Style.RESET_ALL}").strip()
        
        if not user_input:
            return None
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            return 'exit'
        
        if user_input.lower() == 'reset':
            self.llm.reset_conversation()
            print(f"{Fore.GREEN}✓ Conversation reset{Style.RESET_ALL}\n")
            return None
        
        return user_input
    
    def _get_voice_input(self):
        """Get voice input from user."""
        user_input = self.stt.record_and_transcribe(
            duration=config.RECORD_SECONDS,
            sample_rate=config.SAMPLE_RATE,
            channels=config.CHANNELS
        )
        
        if not user_input or not user_input.strip():
            print(f"{Fore.YELLOW}⚠️  No speech detected{Style.RESET_ALL}\n")
            return None
        
        print(f"{Fore.CYAN}You: {user_input}{Style.RESET_ALL}")
        return user_input
    
    def _speak_response(self, response):
        """Speak the response using TTS."""
        try:
            self.tts.speak(response)
        except Exception as e:
            logger.warning(f"TTS error: {e}")
            print(f"{Fore.YELLOW}⚠️  TTS unavailable{Style.RESET_ALL}")
    
    def _should_continue(self):
        """Check if should continue to next interaction."""
        if config.CONTINUOUS_MODE:
            return True
        
        if config.TEXT_MODE:
            return True
        
        # Voice mode, non-continuous: ask user
        print(f"{Fore.YELLOW}Press Enter to speak again, or 'q' to quit...{Style.RESET_ALL}")
        choice = input().strip().lower()
        return choice != 'q'
    
    def _show_instructions(self):
        """Show usage instructions."""
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}USAGE:{Style.RESET_ALL}")
        
        if config.TEXT_MODE:
            print("  • Type your message and press Enter")
            print("  • Type 'exit', 'quit', or 'bye' to exit")
            print("  • Type 'reset' to clear conversation history")
        else:
            print("  • Press Enter to start speaking")
            message = "Speak naturally, pause when done (auto-stop)" if config.USE_VAD else f"Speak clearly for {config.RECORD_SECONDS} seconds"
            print(f"  • {message}")
            print("  • Press 'q' + Enter to quit")
            print("  • Press Ctrl+C to interrupt")
        
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")


def main():
    """Main entry point."""
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}\n")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == '__main__':
    main()
