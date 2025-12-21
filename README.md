# 🤖 Offline AI Voice Assistant

A fully offline voice assistant powered by Whisper (speech-to-text), Llama 3.2 (AI), and Piper (text-to-speech). Everything runs locally on your computer with complete privacy.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🎤 **Voice Input** - Speak naturally to your AI assistant
- 🧠 **Intelligent Responses** - Powered by Llama 3.2 language model
- 🔊 **Natural Speech Output** - High-quality text-to-speech
- 🔒 **100% Offline** - No internet required, complete privacy
- ⚡ **Pure Python Pipeline** - Optimized for speed (120-250ms faster)
- 💬 **Text Mode** - Type your questions when in quiet environments
- 🌍 **Multi-language Support** - Whisper supports 90+ languages

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** - [Download here](https://www.python.org/downloads/)
2. **Ollama** - [Download here](https://ollama.ai)
3. **Git** (optional) - For cloning the repository

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/mirotivo/AI.git
cd AI

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Ollama and download the model
# Download Ollama from https://ollama.ai
ollama pull llama3.2:3b

# 4. Set up Piper voice model (auto-downloads on first run)
# Or manually download from: https://github.com/OHF-Voice/piper1-gpl/releases

# 5. Copy and configure environment file
copy .env.example .env
# Edit .env to customize settings

# 6. Run the assistant
python voice_assistant.py
```

### First Run

```bash
python voice_assistant.py
```

The assistant will:
- ✅ Load Whisper model (one-time, ~140MB)
- ✅ Connect to Ollama
- ✅ Load Piper voice model (one-time, ~60MB)
- ✅ Ready to chat!

---

## ⚙️ Configuration

Edit `.env` file to customize:

```bash
# === Models ===
OLLAMA_MODEL=llama3.2:3b          # AI model (llama3.2:3b, llama3.2:1b, mistral, etc.)
WHISPER_MODEL=base                 # Speech recognition (tiny, base, small, medium, large)
PIPER_VOICE=en_US-lessac-medium   # Voice model

# === Performance ===
WHISPER_DEVICE=cpu                 # Use 'cuda' for GPU acceleration
OLLAMA_URL=http://localhost:11434 # Ollama server URL

# === Audio Settings ===
RECORD_SECONDS=5                   # Recording duration
SAMPLE_RATE=16000                  # Audio sample rate
CHANNELS=1                         # Mono audio

# === Modes ===
TEXT_MODE=false                    # false = voice input, true = keyboard input
CONTINUOUS_MODE=false              # Auto-continue without confirmation
USE_PYTHON_PIPER=true             # Use Python library (faster) vs executable

# === System ===
SYSTEM_PROMPT=You are a helpful AI assistant. Keep responses concise and natural.
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR
```

---

## 🎯 Usage

### Voice Mode (Default)

```
$ python voice_assistant.py

🤖 Voice Assistant Started
• Press Enter to start speaking
• Speak clearly for 5 seconds
• Press 'q' + Enter to quit

[Press Enter]
🎤 Listening...
You: What's the weather like today?
🤔 Thinking...
Assistant: I don't have access to real-time weather data...
🔊 Speaking...
```

### Text Mode

Set `TEXT_MODE=true` in `.env`:

```
$ python voice_assistant.py

🤖 Voice Assistant Started (Text Mode)
• Type your message and press Enter
• Type 'exit' or 'quit' to exit
• Type 'reset' to clear history

You: Hello
🤔 Thinking...
Assistant: Hello! How can I help you today?

You: _
```

---

## 📦 Dependencies

### Core Components

| Component | Purpose | Size | Installation |
|-----------|---------|------|--------------|
| **Whisper** | Speech-to-text AI | ~140MB | `pip install openai-whisper` |
| **Ollama** | LLM server | ~2GB | [ollama.ai](https://ollama.ai) |
| **Piper** | Text-to-speech | ~60MB | Auto-downloads voice models |
| **Python 3.8+** | Runtime | ~100MB | [python.org](https://python.org) |

### Python Packages

```bash
pip install -r requirements.txt
```

Includes:
- `openai-whisper` - Speech recognition
- `sounddevice` - Audio playback
- `soundfile` - Audio file handling
- `piper-tts` - Text-to-speech (Python library)
- `requests` - API communication
- `python-dotenv` - Configuration
- `colorama` - Terminal colors
- `numpy` - Audio processing

### Optional Tools

- **FFmpeg** - Audio format conversion (auto-installed with Whisper on Windows)
- **CUDA Toolkit** - GPU acceleration (for `WHISPER_DEVICE=cuda`)

---

## 🏗️ Architecture

```
┌─────────────┐
│   You Speak │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   Whisper AI    │  Speech → Text
│  (Python lib)   │
└──────┬──────────┘
       │ "What is AI?"
       ▼
┌─────────────────┐
│     Ollama      │  Generate Response
│  Llama 3.2 3B   │
└──────┬──────────┘
       │ "AI stands for..."
       ▼
┌─────────────────┐
│   Piper TTS     │  Text → Speech
│  (Python lib)   │
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│  You Hear   │
└─────────────┘
```

### Pure Python Pipeline

All components use Python libraries (no subprocess overhead):
- ✅ **Whisper**: Direct numpy array processing
- ✅ **Piper**: Python library with AudioChunk handling
- ✅ **Ollama**: Python requests library

**Performance gain**: 120-250ms faster per interaction!

---

## 📁 Project Structure

```
AI/
├── voice_assistant.py              # Main application
├── config.py                       # Configuration loader
├── .env                            # Your settings
├── .env.example                    # Template
├── requirements.txt                # Python dependencies
│
├── modules/                        # Core modules
│   ├── __init__.py
│   ├── speech_to_text.py          # Whisper integration (Python)
│   ├── llm_client.py               # Ollama client
│   ├── text_to_speech.py          # Piper (executable version)
│   └── text_to_speech_python.py   # Piper (Python library)
│
└── piper/                          # Piper TTS files
    ├── piper.exe                   # Executable (Windows)
    └── voices/                     # Voice models (.onnx files)
        └── en_US-lessac-medium.onnx
```

---


## 🎤 Available Whisper Models

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `tiny` | ~40MB | Fastest | 🌟🌟 | Quick testing |
| `base` | ~140MB | Fast | 🌟🌟🌟 | Default, balanced |
| `small` | ~460MB | Medium | 🌟🌟🌟🌟 | Better accuracy |
| `medium` | ~1.5GB | Slow | 🌟🌟🌟🌟🌟 | High accuracy |
| `large` | ~2.9GB | Slowest | 🌟🌟🌟🌟🌟 | Best accuracy |

**Recommendation**: Start with `base` for best balance.

---

## 🗣️ Available Piper Voices

### English Voices

| Voice | Quality | Speed | Gender | Accent |
|-------|---------|-------|--------|--------|
| `en_US-lessac-medium` | High | Medium | Male | American |
| `en_US-amy-medium` | High | Medium | Female | American |
| `en_GB-alan-medium` | High | Medium | Male | British |
| `en_GB-jenny_dioco-medium` | High | Medium | Female | British |

[Download more voices](https://github.com/OHF-Voice/piper1-gpl/blob/main/VOICES.md)

### Adding New Voices

```bash
# 1. Download .onnx and .json files from Piper releases
# 2. Copy to piper/voices/
# 3. Update .env
PIPER_VOICE=en_GB-alan-medium
```

---

## 🤖 Available Ollama Models

| Model | Size | Speed | Use Case |
|-------|------|-------|----------|
| `llama3.2:1b` | ~1.3GB | Fastest | Quick responses |
| `llama3.2:3b` | ~2GB | Fast | Default, balanced |
| `llama3.1:8b` | ~4.7GB | Medium | Better reasoning |
| `mistral:7b` | ~4.1GB | Medium | Creative writing |
| `codellama:7b` | ~3.8GB | Medium | Code assistance |

```bash
# Download a model
ollama pull llama3.2:3b

# List installed models
ollama list

# Remove a model
ollama rm model_name
```

---

## 🌍 Multi-language Support

Whisper supports 90+ languages. Just speak in your language!

### Example Configuration

```bash
# For Spanish
PIPER_VOICE=es_ES-carlfm-x_low
# Speak in Spanish, get Spanish responses

# For French  
PIPER_VOICE=fr_FR-siwis-medium
# Speak in French, get French responses

# For German
PIPER_VOICE=de_DE-thorsten-medium
# Speak in German, get German responses
```

[See all supported languages](https://github.com/OHF-Voice/piper1-gpl/blob/main/VOICES.md)

---

## 💡 Tips & Best Practices

### For Best Voice Recognition
- Speak clearly and at normal pace
- Use a good quality microphone
- Reduce background noise
- Increase `RECORD_SECONDS` for longer questions

### For Better AI Responses
- Be specific in your questions
- Provide context when needed
- Use the `SYSTEM_PROMPT` to set behavior
- Use larger models for complex queries

### For Faster Performance
- Use `tiny` or `base` Whisper models
- Use smaller Ollama models (1b, 3b)
- Enable `USE_PYTHON_PIPER=true`
- Consider GPU acceleration

### For Privacy
- All data stays on your computer
- No internet connection needed
- Models run locally
- No data sent to cloud services

---

## 🔒 Privacy & Security

### Data Privacy
- ✅ **100% Offline** - No internet required after setup
- ✅ **No Cloud Services** - All processing on your PC
- ✅ **No Telemetry** - No usage data collected
- ✅ **Complete Control** - You own all your data

### What Data is Stored?
- **Locally**: Conversation history (in memory, cleared on restart)
- **Not Stored**: Audio recordings (processed then discarded)
- **Models**: Downloaded once, stored locally

---

## 📊 System Requirements

### Minimum
- **CPU**: Dual-core 2.0 GHz
- **RAM**: 4GB
- **Storage**: 5GB free space
- **OS**: Windows 10+, macOS 10.15+, Linux

### Recommended
- **CPU**: Quad-core 3.0 GHz+
- **RAM**: 8GB+
- **Storage**: 10GB+ SSD
- **GPU**: NVIDIA GPU with CUDA (optional, for acceleration)

### Storage Breakdown
| Component | Size |
|-----------|------|
| Python + packages | ~500MB |
| Whisper base model | ~140MB |
| Ollama + Llama 3.2 | ~2GB |
| Piper + voice | ~80MB |
| **Total** | **~3GB** |

---

## 🛠️ Development

### Running Tests

```bash
# Test microphone
python -c "from modules.speech_to_text import SpeechToText; stt = SpeechToText(); stt.record_audio()"

# Test Ollama
python -c "from modules.llm_client import LLMClient; client = LLMClient(); print(client.generate('Hello'))"

# Test TTS
python -c "from modules.text_to_speech_python import TextToSpeech; tts = TextToSpeech(voice_model_path='piper/voices/en_US-lessac-medium.onnx'); tts.speak('Hello')"
```

### Code Structure

```python
# Main application
voice_assistant.py
  ├── VoiceAssistant.__init__()      # Initialize components
  ├── VoiceAssistant.run()            # Main loop
  ├── process_voice_input()           # Handle voice mode
  └── process_text_input()            # Handle text mode

# Configuration
config.py
  └── Config class                    # Load settings from .env

# Modules
modules/
  ├── speech_to_text.py               # Whisper wrapper
  │   ├── record_audio()              # Capture audio
  │   └── transcribe()                # Speech → text
  │
  ├── llm_client.py                   # Ollama client
  │   ├── generate()                  # Get AI response
  │   └── reset_conversation()        # Clear history
  │
  └── text_to_speech_python.py       # Piper wrapper
      ├── synthesize()                # Text → audio
      └── speak()                     # Generate + play
```

---

## 🚧 Known Limitations

- **Response Time**: 2-5 seconds per interaction (depends on model size)
- **Model Size**: Larger models require more RAM/storage
- **Language Mixing**: Piper voices are language-specific
- **Real-time Data**: No access to current events/weather
- **Complex Reasoning**: Limited by model capabilities

---

## 🗺️ Roadmap

- [ ] Add wake word detection ("Hey Assistant")
- [ ] Support for streaming responses
- [ ] Multi-turn conversation improvements
- [ ] Custom voice training
- [ ] Web interface
- [ ] Mobile app version
- [ ] Plugin system for extensions

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/mirotivo/AI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mirotivo/AI/discussions)

---

## 🙏 Acknowledgments

This project stands on the shoulders of giants. Special thanks to:

### Core Technologies

- **[OpenAI Whisper](https://github.com/openai/whisper)** - Open-source speech recognition
  - GitHub: https://github.com/openai/whisper
  - PyPI: `pip install openai-whisper`
  - License: MIT

- **[Ollama](https://github.com/ollama/ollama)** - Run large language models locally
  - GitHub: https://github.com/ollama/ollama
  - Website: https://ollama.ai
  - License: MIT

- **[Piper TTS](https://github.com/OHF-Voice/piper1-gpl)** - Fast, local text-to-speech
  - GitHub: https://github.com/OHF-Voice/piper1-gpl
  - PyPI: `pip install piper-tts`
  - License: GPL

- **[Meta Llama](https://llama.meta.com/)** - Open-source language models
  - Website: https://llama.meta.com/
  - Models: llama3.2:1b, llama3.2:3b, llama3.1:8b

### Why These Projects?

All chosen for being:
- ✅ **Open Source** - Free to use and modify
- ✅ **Offline Capable** - No internet required
- ✅ **High Quality** - Production-ready
- ✅ **Well Maintained** - Active development
- ✅ **Python Compatible** - Easy integration

**Note**: While we use Python packages from PyPI (`pip install`), the source code lives on GitHub. Check the links above to explore, contribute, or learn more!

---

## 📚 Additional Resources

- [Whisper Documentation](https://github.com/openai/whisper)
- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Piper Documentation](https://github.com/OHF-Voice/piper1-gpl)
- [Python Speech Processing](https://realpython.com/python-speech-recognition/)

---

**Made with ❤️ for offline AI enthusiasts**

*Last updated: December 2025*
