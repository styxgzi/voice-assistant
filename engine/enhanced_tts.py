import pyttsx3
import asyncio
import logging
from typing import Optional, Dict, List
import os
from engine.config import TTS_CONFIG

class EnhancedTTS:
    def __init__(self):
        self.engine = None
        self.logger = logging.getLogger(__name__)
        self.setup_tts_engine()
        self.voice_cache = {}
        
    def setup_tts_engine(self):
        """Setup TTS engine based on configuration"""
        try:
            if TTS_CONFIG['engine'] == 'azure':
                self.setup_azure_tts()
            elif TTS_CONFIG['engine'] == 'coqui':
                self.setup_coqui_tts()
            else:
                self.setup_default_tts()
        except Exception as e:
            self.logger.error(f"Error setting up TTS engine: {e}")
            self.setup_default_tts()
    
    def setup_default_tts(self):
        """Setup default pyttsx3 TTS engine"""
        try:
            self.engine = pyttsx3.init()
            self.configure_default_voice()
            self.logger.info("Default TTS engine initialized")
        except Exception as e:
            self.logger.error(f"Error initializing default TTS: {e}")
    
    def setup_azure_tts(self):
        """Setup Azure Speech Services TTS"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            # Check if Azure key is configured
            azure_key = os.getenv('AZURE_SPEECH_KEY')
            azure_region = os.getenv('AZURE_SPEECH_REGION')
            
            if azure_key and azure_region:
                self.azure_speech_config = speechsdk.SpeechConfig(
                    subscription=azure_key, 
                    region=azure_region
                )
                self.azure_speech_config.speech_synthesis_voice_name = TTS_CONFIG['voice']
                self.engine = 'azure'
                self.logger.info("Azure TTS engine initialized")
            else:
                self.logger.warning("Azure credentials not found, falling back to default TTS")
                self.setup_default_tts()
                
        except ImportError:
            self.logger.warning("Azure Speech SDK not installed, falling back to default TTS")
            self.setup_default_tts()
        except Exception as e:
            self.logger.error(f"Error setting up Azure TTS: {e}")
            self.setup_default_tts()
    
    def setup_coqui_tts(self):
        """Setup Coqui TTS engine"""
        try:
            from TTS.api import TTS
            
            # Initialize Coqui TTS
            self.coqui_tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            self.engine = 'coqui'
            self.logger.info("Coqui TTS engine initialized")
            
        except ImportError:
            self.logger.warning("Coqui TTS not installed, falling back to default TTS")
            self.setup_default_tts()
        except Exception as e:
            self.logger.error(f"Error setting up Coqui TTS: {e}")
            self.setup_default_tts()
    
    def configure_default_voice(self):
        """Configure default TTS voice settings"""
        if self.engine and hasattr(self.engine, 'setProperty'):
            # Set voice properties
            self.engine.setProperty('rate', int(TTS_CONFIG['rate'] * 200))  # Convert to WPM
            self.engine.setProperty('volume', TTS_CONFIG['volume'])
            
            # Set voice
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to find a preferred voice
                preferred_voice = self.find_preferred_voice(voices)
                if preferred_voice:
                    self.engine.setProperty('voice', preferred_voice.id)
    
    def find_preferred_voice(self, voices) -> Optional[object]:
        """Find preferred voice from available voices"""
        preferred_voices = [
            'en-US-JennyNeural',
            'en-US-GuyNeural', 
            'en-GB-SoniaNeural',
            'en-GB-RyanNeural',
            r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0',
            r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'
        ]
        
        for voice in voices:
            for preferred in preferred_voices:
                if preferred.lower() in voice.id.lower():
                    return voice
        
        # Return first available voice
        return voices[0] if voices else None
    
    async def speak(self, text: str, voice: Optional[str] = None, rate: Optional[float] = None) -> bool:
        """Speak text with specified voice and rate"""
        if not text or not text.strip():
            return False
        
        try:
            if self.engine == 'azure':
                return await self.speak_azure(text, voice, rate)
            elif self.engine == 'coqui':
                return await self.speak_coqui(text, voice, rate)
            else:
                return await self.speak_default(text, voice, rate)
        except Exception as e:
            self.logger.error(f"Error in TTS: {e}")
            return False
    
    async def speak_default(self, text: str, voice: Optional[str] = None, rate: Optional[float] = None) -> bool:
        """Speak using default TTS engine"""
        try:
            if voice:
                self.set_voice(voice)
            if rate:
                self.set_rate(rate)
            
            # Run TTS in thread to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.engine.say, text)
            await loop.run_in_executor(None, self.engine.runAndWait)
            
            return True
        except Exception as e:
            self.logger.error(f"Error in default TTS: {e}")
            return False
    
    async def speak_azure(self, text: str, voice: Optional[str] = None, rate: Optional[float] = None) -> bool:
        """Speak using Azure TTS"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            # Configure voice and rate
            if voice:
                self.azure_speech_config.speech_synthesis_voice_name = voice
            if rate:
                self.azure_speech_config.speech_synthesis_speaking_rate = rate
            
            # Create synthesizer
            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.azure_speech_config)
            
            # Synthesize speech
            result = speech_synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return True
            else:
                self.logger.error(f"Azure TTS failed: {result.reason}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in Azure TTS: {e}")
            return False
    
    async def speak_coqui(self, text: str, voice: Optional[str] = None, rate: Optional[float] = None) -> bool:
        """Speak using Coqui TTS"""
        try:
            # Coqui TTS doesn't support voice switching in the same way
            # but we can adjust speed
            speed = rate if rate else 1.0
            
            # Generate speech
            output_path = "temp_speech.wav"
            self.coqui_tts.tts_to_file(text=text, file_path=output_path, speed=speed)
            
            # Play the generated audio
            await self.play_audio_file(output_path)
            
            # Clean up
            if os.path.exists(output_path):
                os.remove(output_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in Coqui TTS: {e}")
            return False
    
    async def play_audio_file(self, file_path: str) -> bool:
        """Play audio file asynchronously"""
        try:
            import pygame
            
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            
            pygame.mixer.quit()
            return True
            
        except ImportError:
            self.logger.warning("Pygame not available for audio playback")
            return False
        except Exception as e:
            self.logger.error(f"Error playing audio file: {e}")
            return False
    
    def set_voice(self, voice_name: str) -> bool:
        """Set TTS voice"""
        try:
            if self.engine and hasattr(self.engine, 'setProperty'):
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if voice_name.lower() in voice.name.lower() or voice_name.lower() in voice.id.lower():
                        self.engine.setProperty('voice', voice.id)
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Error setting voice: {e}")
            return False
    
    def set_rate(self, rate: float) -> bool:
        """Set TTS rate (words per minute)"""
        try:
            if self.engine and hasattr(self.engine, 'setProperty'):
                # Convert rate to WPM (typical range: 150-200 WPM)
                wpm = int(rate * 200)
                self.engine.setProperty('rate', wpm)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error setting rate: {e}")
            return False
    
    def set_volume(self, volume: float) -> bool:
        """Set TTS volume (0.0 to 1.0)"""
        try:
            if self.engine and hasattr(self.engine, 'setProperty'):
                self.engine.setProperty('volume', volume)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error setting volume: {e}")
            return False
    
    def get_available_voices(self) -> List[Dict]:
        """Get list of available voices"""
        voices = []
        
        try:
            if self.engine and hasattr(self.engine, 'getProperty'):
                engine_voices = self.engine.getProperty('voices')
                for voice in engine_voices:
                    voices.append({
                        'id': voice.id,
                        'name': voice.name,
                        'languages': getattr(voice, 'languages', []),
                        'gender': getattr(voice, 'gender', 'Unknown')
                    })
        except Exception as e:
            self.logger.error(f"Error getting voices: {e}")
        
        return voices
    
    def get_current_voice(self) -> Optional[Dict]:
        """Get current voice information"""
        try:
            if self.engine and hasattr(self.engine, 'getProperty'):
                voice_id = self.engine.getProperty('voice')
                voices = self.engine.getProperty('voices')
                
                for voice in voices:
                    if voice.id == voice_id:
                        return {
                            'id': voice.id,
                            'name': voice.name,
                            'languages': getattr(voice, 'languages', []),
                            'gender': getattr(voice, 'gender', 'Unknown')
                        }
        except Exception as e:
            self.logger.error(f"Error getting current voice: {e}")
        
        return None
    
    def stop_speaking(self) -> bool:
        """Stop current speech"""
        try:
            if self.engine and hasattr(self.engine, 'stop'):
                self.engine.stop()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error stopping speech: {e}")
            return False 