"""Main Voice Assistant Application."""

import logging
import sys
import time
from colorama import init, Fore, Style

from config import config
from modules.llm_client import LLMClient
from modules.speech_to_text import SpeechToText
from modules.text_to_speech import TextToSpeech
from modules.text_to_speech_python import TextToSpeech as TextToSpeechPython

# Initialize colorama for Windows
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
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🤖  OFFLINE AI VOICE ASSISTANT  🤖{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # Display configuration
        config.display()
        
        # Initialize components
        self.initialize_components()
        
        print(f"{Fore.GREEN}✅ Voice Assistant initialized successfully!{Style.RESET_ALL}\n")
    
    def initialize_components(self):
        """Initialize all components."""
        try:
            # Initialize LLM Client (always needed)
            print(f"{Fore.YELLOW}Initializing LLM Client...{Style.RESET_ALL}")
            self.llm = LLMClient(
                base_url=config.OLLAMA_URL,
                model=config.OLLAMA_MODEL,
                system_prompt=config.SYSTEM_PROMPT
            )
            print(f"{Fore.GREEN}✅ LLM Client initialized{Style.RESET_ALL}")
            
            # Check Ollama connection
            if not self.llm.check_connection():
                print(f"{Fore.RED}⚠️  Warning: Cannot connect to Ollama at {config.OLLAMA_URL}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Make sure Ollama is running!{Style.RESET_ALL}")
            
            # Initialize Speech-to-Text only if not in TEXT_MODE
            if not config.TEXT_MODE:
                print(f"{Fore.YELLOW}Initializing Speech-to-Text...{Style.RESET_ALL}")
                self.stt = SpeechToText(
                    model_name=config.WHISPER_MODEL,
                    device=config.WHISPER_DEVICE
                )
                print(f"{Fore.GREEN}✅ Speech-to-Text initialized{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}TEXT_MODE enabled - Skipping Speech-to-Text{Style.RESET_ALL}")
                self.stt = None
            
            # Initialize Text-to-Speech (Python or executable version)
            tts_mode = "Python-based" if config.USE_PYTHON_PIPER else "Executable-based"
            print(f"{Fore.YELLOW}Initializing Text-to-Speech ({tts_mode})...{Style.RESET_ALL}")
            if config.USE_PYTHON_PIPER:
                self.tts = TextToSpeechPython(
                    piper_executable=config.PIPER_EXECUTABLE,
                    voice_model_path=config.piper_voice_path
                )
            else:
                self.tts = TextToSpeech(
                    piper_executable=config.PIPER_EXECUTABLE,
                    voice_model_path=config.piper_voice_path
                )
            print(f"{Fore.GREEN}✅ Text-to-Speech initialized{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            print(f"{Fore.RED}❌ Initialization failed: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    def process_voice_input(self):
        """Process a single voice interaction."""
        try:
            # Record and transcribe
            user_input = self.stt.record_and_transcribe(
                duration=config.RECORD_SECONDS,
                sample_rate=config.SAMPLE_RATE,
                channels=config.CHANNELS
            )
            
            if not user_input or user_input.strip() == "":
                print(f"{Fore.YELLOW}⚠️  No speech detected{Style.RESET_ALL}\n")
                return None
            
            print(f"{Fore.CYAN}You: {user_input}{Style.RESET_ALL}")
            
            # Generate response
            response = self.llm.generate(user_input)
            print(f"{Fore.GREEN}Assistant: {response}{Style.RESET_ALL}\n")
            
            # Speak response
            self.tts.speak(response)
            
            return user_input
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}\n")
            return None
    
    def process_text_input(self):
        """Process a single text interaction."""
        try:
            # Get text input
            user_input = input(f"{Fore.CYAN}You: {Style.RESET_ALL}").strip()
            
            if not user_input:
                return None
            
            # Check for special commands
            if user_input.lower() in ['exit', 'quit', 'bye']:
                return 'exit'
            
            if user_input.lower() == 'reset':
                self.llm.reset_conversation()
                print(f"{Fore.GREEN}✓ Conversation history cleared{Style.RESET_ALL}\n")
                return None
            
            # Generate response
            print(f"{Fore.MAGENTA}🤔 Thinking...{Style.RESET_ALL}")
            response = self.llm.generate(user_input)
            print(f"{Fore.GREEN}Assistant: {response}{Style.RESET_ALL}")
            
            # Speak response
            if self.tts:
                print(f"{Fore.CYAN}🔊 Speaking...{Style.RESET_ALL}")
                try:
                    self.tts.speak(response)
                except Exception as e:
                    logger.warning(f"TTS error: {e}")
                    print(f"{Fore.YELLOW}⚠️  TTS error: {e}{Style.RESET_ALL}")
            print()  # Add newline after response
            
            return user_input
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Error processing text input: {e}")
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}\n")
            return None
    
    def run(self):
        """Run the voice assistant."""
        try:
            # Show usage instructions
            self.show_instructions()
            
            # Main loop
            while True:
                try:
                    if config.TEXT_MODE:
                        result = self.process_text_input()
                        if result == 'exit':
                            break
                    else:
                        result = self.process_voice_input()
                    
                    # In continuous mode, keep going
                    if not config.CONTINUOUS_MODE:
                        # Ask if user wants to continue
                        if not config.TEXT_MODE:
                            print(f"{Fore.YELLOW}Press Enter to speak again, or 'q' to quit...{Style.RESET_ALL}")
                            choice = input().strip().lower()
                            if choice == 'q':
                                break
                    else:
                        # Small delay in continuous mode
                        time.sleep(0.5)
                        
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
                    break
            
            print(f"\n{Fore.CYAN}👋 Goodbye!{Style.RESET_ALL}\n")
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    def show_instructions(self):
        """Show usage instructions."""
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}USAGE:{Style.RESET_ALL}")
        
        if config.TEXT_MODE:
            print("  • Type your message and press Enter")
            print("  • Type 'exit', 'quit', or 'bye' to exit")
            print("  • Type 'reset' to clear conversation history")
        else:
            print("  • Press Enter to start speaking")
            print(f"  • Speak clearly for {config.RECORD_SECONDS} seconds")
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
