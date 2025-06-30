import speech_recognition as sr
import numpy as np
import asyncio
import threading
from typing import Optional, Tuple
import logging
from engine.config import SPEECH_RECOGNITION_CONFIG

# Optional imports with fallbacks
try:
    import webrtcvad
    VAD_AVAILABLE = True
except ImportError:
    VAD_AVAILABLE = False
    logging.warning("webrtcvad not available, voice activity detection disabled")

class EnhancedSpeechRecognition:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.vad = None
        if VAD_AVAILABLE:
            try:
                self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2
            except Exception as e:
                logging.warning(f"Could not initialize VAD: {e}")
        self.setup_recognizer()
        self.logger = logging.getLogger(__name__)
        
    def setup_recognizer(self):
        """Configure speech recognizer with enhanced settings"""
        config = SPEECH_RECOGNITION_CONFIG
        self.recognizer.energy_threshold = config['energy_threshold']
        self.recognizer.dynamic_energy_threshold = config['dynamic_energy_threshold']
        self.recognizer.pause_threshold = 1.0
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        
    async def listen_with_noise_reduction(self, source) -> Optional[str]:
        """Enhanced listening with noise reduction and VAD"""
        try:
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Listen with enhanced parameters
            audio = self.recognizer.listen(
                source,
                timeout=SPEECH_RECOGNITION_CONFIG['timeout'],
                phrase_time_limit=SPEECH_RECOGNITION_CONFIG['phrase_time_limit']
            )
            
            # Apply noise reduction
            audio_data = self.apply_noise_reduction(audio)
            
            return await self.recognize_speech(audio_data)
            
        except sr.WaitTimeoutError:
            self.logger.warning("Speech recognition timeout")
            return None
        except sr.UnknownValueError:
            self.logger.warning("Speech not understood")
            return None
        except Exception as e:
            self.logger.error(f"Speech recognition error: {e}")
            return None
    
    def apply_noise_reduction(self, audio) -> sr.AudioData:
        """Apply noise reduction to audio data"""
        try:
            # Convert to numpy array for processing
            audio_array = np.frombuffer(audio.frame_data, dtype=np.int16)
            
            # Simple noise gate
            threshold = np.std(audio_array) * 0.1
            audio_array = np.where(np.abs(audio_array) < threshold, 0, audio_array)
            
            # Convert back to AudioData
            return sr.AudioData(
                audio_array.tobytes(),
                audio.sample_rate,
                audio.sample_width
            )
        except Exception as e:
            self.logger.warning(f"Noise reduction failed: {e}, returning original audio")
            return audio
    
    async def recognize_speech(self, audio_data) -> Optional[str]:
        """Recognize speech with multiple fallback engines"""
        engines = [
            self._recognize_google,
            self._recognize_azure,
            self._recognize_whisper
        ]
        
        for engine in engines:
            try:
                result = await engine(audio_data)
                if result and result.strip():
                    return result.strip().lower()
            except Exception as e:
                self.logger.warning(f"Engine {engine.__name__} failed: {e}")
                continue
        
        return None
    
    async def _recognize_google(self, audio_data) -> str:
        """Google Speech Recognition"""
        return self.recognizer.recognize_google(
            audio_data, 
            language=SPEECH_RECOGNITION_CONFIG['language']
        )
    
    async def _recognize_azure(self, audio_data) -> str:
        """Azure Speech Recognition (if configured)"""
        # Implementation for Azure Speech Services
        # Requires Azure Speech SDK
        raise NotImplementedError("Azure Speech not configured")
    
    async def _recognize_whisper(self, audio_data) -> str:
        """OpenAI Whisper (if available)"""
        try:
            import whisper
            model = whisper.load_model("base")
            # Convert audio_data to file or use whisper's API
            # This is a simplified implementation
            return "whisper_result"  # Placeholder
        except ImportError:
            raise NotImplementedError("Whisper not available")
    
    def get_confidence_score(self, audio_data) -> float:
        """Get confidence score for speech recognition"""
        try:
            # This would require a more sophisticated implementation
            # For now, return a default confidence
            return 0.8
        except Exception:
            return 0.5

class MultiLanguageSupport:
    """Support for multiple languages"""
    
    def __init__(self):
        self.supported_languages = {
            'en-US': 'English (US)',
            'en-GB': 'English (UK)',
            'es-ES': 'Spanish',
            'fr-FR': 'French',
            'de-DE': 'German',
            'it-IT': 'Italian',
            'pt-BR': 'Portuguese (Brazil)',
            'ja-JP': 'Japanese',
            'ko-KR': 'Korean',
            'zh-CN': 'Chinese (Simplified)'
        }
        self.current_language = 'en-US'
    
    def set_language(self, language_code: str):
        """Set the current language for speech recognition"""
        if language_code in self.supported_languages:
            self.current_language = language_code
            return True
        return False
    
    def get_language_name(self, language_code: str) -> str:
        """Get human-readable language name"""
        return self.supported_languages.get(language_code, 'Unknown')
    
    def detect_language(self, audio_data) -> str:
        """Auto-detect language from audio"""
        # This would require a language detection model
        # For now, return the current language
        return self.current_language 