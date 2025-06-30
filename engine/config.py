ASSISTANT_NAME = "prime"

# Enhanced Configuration for Modern Voice Assistant

# Speech Recognition Settings
SPEECH_RECOGNITION_CONFIG = {
    'language': 'en-US',  # Support for multiple languages
    'timeout': 10,
    'phrase_time_limit': 6,
    'ambient_noise_adjustment': True,
    'energy_threshold': 4000,
    'dynamic_energy_threshold': True
}

# Natural Language Processing
NLP_CONFIG = {
    'model_name': 'en_core_web_sm',  # spaCy model for NLP
    'intent_threshold': 0.7,
    'context_window_size': 5
}

# Face Recognition Settings
FACE_RECOGNITION_CONFIG = {
    'model_type': 'deepface',  # Modern face recognition
    'encryption_enabled': True,
    'multi_user_support': True,
    'liveness_detection': True
}

# Security Settings
SECURITY_CONFIG = {
    'encrypt_database': True,
    'encrypt_credentials': True,
    'session_timeout': 3600,  # 1 hour
    'max_login_attempts': 3
}

# Cross-Platform Settings
PLATFORM_CONFIG = {
    'auto_detect_os': True,
    'default_browser': 'auto',  # Auto-detect browser
    'path_separator': 'auto'  # Auto-detect path separator
}

# TTS Settings
TTS_CONFIG = {
    'engine': 'default',  # 'azure', 'coqui', or 'default'
    'voice': 'en-US-JennyNeural',
    'rate': 1.0,
    'volume': 1.0
}

# API Keys (should be stored in environment variables)
API_KEYS = {
    'openweathermap': None,  # Weather API
    'newsapi': None,  # News API
    'azure_speech': None,  # Azure Speech Services
    'openai': None  # OpenAI API for enhanced chat
}

# Feature Flags
FEATURES = {
    'smart_home': False,
    'calendar': False,
    'email': False,
    'weather': False,
    'news': False,
    'voice_customization': True,
    'multi_language': True
}
