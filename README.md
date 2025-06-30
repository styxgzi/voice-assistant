# PRIME - Modern Voice Assistant

A modern, intelligent voice assistant built with advanced AI technologies and cross-platform compatibility.

## 🚀 Features

### Core Capabilities
- **Advanced Speech Recognition** with noise reduction and multiple language support
- **Natural Language Understanding** using spaCy and intent recognition
- **Modern Face Recognition** with deep learning and multi-user support
- **Enhanced Text-to-Speech** with multiple engine support (Azure, Coqui, pyttsx3)
- **Cross-Platform Compatibility** (Windows, macOS, Linux)
- **Secure Authentication** with encrypted face data storage

### Smart Features
- **Intent Recognition** - Understands natural language commands
- **Context Awareness** - Remembers conversation context
- **Multi-Language Support** - 10+ languages supported
- **Voice Customization** - Multiple voices and speech rates
- **Real-time Processing** - Async operations for better performance

### Command Examples
```
"Open Chrome"
"Play Despacito on YouTube"
"Send message to John"
"Call Mom"
"What's the weather in New York?"
"Set reminder to buy groceries at 6 PM"
"Tell me a joke"
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Microphone and camera for voice/face recognition
- Internet connection for speech recognition and TTS

### Quick Start
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd jarvis-main
   ```

2. **Install dependencies**
   ```bash
   python install_dependencies.py
   ```

3. **Run the assistant**
   ```bash
   python main.py
   ```

### Manual Installation
If the automatic installation fails, install dependencies manually:

```bash
# Core dependencies
pip install eel pyaudio pyautogui pvporcupine hugchat playsound

# Enhanced features
pip install SpeechRecognition webrtcvad numpy spacy face-recognition opencv-python

# Security and cross-platform
pip install cryptography pygame pyttsx3

# Optional: Advanced TTS
pip install azure-cognitiveservices-speech TTS

# Install spaCy model
python -m spacy download en_core_web_sm
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file for API keys:

```env
# Azure Speech Services (optional)
AZURE_SPEECH_KEY=your_azure_key
AZURE_SPEECH_REGION=your_azure_region

# Weather API (optional)
OPENWEATHERMAP_API_KEY=your_weather_key

# News API (optional)
NEWS_API_KEY=your_news_key

# OpenAI (optional)
OPENAI_API_KEY=your_openai_key
```

### Configuration File
Edit `engine/config.py` to customize:

```python
# Speech Recognition
SPEECH_RECOGNITION_CONFIG = {
    'language': 'en-US',
    'timeout': 10,
    'energy_threshold': 4000
}

# TTS Settings
TTS_CONFIG = {
    'engine': 'azure',  # 'azure', 'coqui', or 'default'
    'voice': 'en-US-JennyNeural',
    'rate': 1.0
}

# Feature Flags
FEATURES = {
    'weather': True,
    'news': True,
    'calendar': False,
    'email': False
}
```

## 🏗️ Architecture

### Enhanced Modules

#### 1. Enhanced Speech Recognition (`engine/enhanced_speech.py`)
- **Noise Reduction** using WebRTC VAD
- **Multiple Engines** (Google, Azure, Whisper)
- **Confidence Scoring** and fallback mechanisms
- **Multi-language Support** with auto-detection

#### 2. Natural Language Processing (`engine/nlp_processor.py`)
- **Intent Recognition** using spaCy
- **Entity Extraction** for commands
- **Context Management** for conversations
- **Pattern Matching** with confidence scoring

#### 3. Modern Face Recognition (`engine/enhanced_face_recognition.py`)
- **Deep Learning** using face_recognition library
- **Multi-user Support** with encrypted storage
- **Liveness Detection** to prevent spoofing
- **Access Statistics** and user management

#### 4. Cross-Platform Manager (`engine/cross_platform.py`)
- **OS Detection** and platform-specific handling
- **Browser Management** (Chrome, Firefox, Safari)
- **Application Launching** across platforms
- **Dependency Checking** and installation

#### 5. Enhanced TTS (`engine/enhanced_tts.py`)
- **Multiple Engines** (Azure, Coqui, pyttsx3)
- **Voice Customization** and rate control
- **Async Processing** for non-blocking speech
- **Audio Playback** with pygame

## 🔒 Security Features

- **Encrypted Face Data** using Fernet encryption
- **Secure API Key Management** with environment variables
- **Session Management** with timeout controls
- **Access Logging** and audit trails

## 🌐 Cross-Platform Support

### Windows
- Native application launching
- Chrome browser integration
- Windows-specific optimizations

### macOS
- Homebrew dependency management
- Safari/Chrome browser support
- macOS-specific paths and commands

### Linux
- Package manager integration (apt, yum)
- Firefox/Chrome browser support
- Linux-specific audio handling

## 📊 Performance Optimizations

- **Async Operations** for non-blocking processing
- **Caching** for frequently used data
- **Resource Management** with proper cleanup
- **Error Handling** with graceful fallbacks

## 🧪 Testing

Run tests to verify functionality:

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/
```

## 🐛 Troubleshooting

### Common Issues

1. **PyAudio Installation**
   ```bash
   # Windows
   pip install pipwin
   pipwin install pyaudio
   
   # macOS
   brew install portaudio
   pip install pyaudio
   
   # Linux
   sudo apt-get install portaudio19-dev python3-pyaudio
   pip install pyaudio
   ```

2. **Face Recognition Issues**
   ```bash
   # Install dlib dependencies
   pip install cmake
   pip install dlib
   pip install face-recognition
   ```

3. **spaCy Model Issues**
   ```bash
   python -m spacy download en_core_web_sm
   ```

### Debug Mode
Enable debug logging by modifying `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **spaCy** for natural language processing
- **face_recognition** for face detection
- **Azure Speech Services** for advanced TTS
- **WebRTC VAD** for voice activity detection
- **Eel** for the web interface framework

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the configuration options

---

**Prime Assistant** - Your intelligent, modern voice companion! 🎯
