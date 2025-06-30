import asyncio
import logging
from typing import Dict, Optional
from engine.enhanced_speech import EnhancedSpeechRecognition, MultiLanguageSupport
from engine.nlp_processor import NLPProcessor
from engine.enhanced_face_recognition import EnhancedFaceRecognition
from engine.cross_platform import CrossPlatformManager
from engine.enhanced_tts import EnhancedTTS
from engine.config import ASSISTANT_NAME, FEATURES

class EnhancedCommandProcessor:
    def __init__(self):
        self.speech_recognition = EnhancedSpeechRecognition()
        self.nlp_processor = NLPProcessor()
        self.face_recognition = EnhancedFaceRecognition()
        self.platform_manager = CrossPlatformManager()
        self.tts = EnhancedTTS()
        self.language_support = MultiLanguageSupport()
        self.logger = logging.getLogger(__name__)
        
        # Initialize features
        self.setup_features()
    
    def setup_features(self):
        """Setup available features based on configuration"""
        self.available_features = {
            'weather': FEATURES['weather'],
            'news': FEATURES['news'],
            'calendar': FEATURES['calendar'],
            'email': FEATURES['email'],
            'smart_home': FEATURES['smart_home']
        }
    
    async def process_command(self, query: str = None) -> Dict:
        """Main command processing function"""
        try:
            # Get speech input if not provided
            if not query:
                query = await self.listen_for_command()
                if not query:
                    return {'success': False, 'message': 'No speech detected'}
            
            # Process with NLP
            nlp_result = self.nlp_processor.process_query(query)
            
            # Execute command based on intent
            result = await self.execute_intent(nlp_result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    async def listen_for_command(self) -> Optional[str]:
        """Listen for voice command with enhanced features"""
        try:
            import speech_recognition as sr
            
            with sr.Microphone() as source:
                self.logger.info("Listening for command...")
                
                # Use enhanced speech recognition
                query = await self.speech_recognition.listen_with_noise_reduction(source)
                
                if query:
                    self.logger.info(f"Recognized: {query}")
                    return query
                else:
                    self.logger.warning("No speech recognized")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error listening for command: {e}")
            return None
    
    async def execute_intent(self, nlp_result: Dict) -> Dict:
        """Execute command based on NLP intent"""
        intent = nlp_result.get('intent', 'unknown')
        confidence = nlp_result.get('confidence', 0.0)
        entities = nlp_result.get('entities', {})
        
        self.logger.info(f"Intent: {intent}, Confidence: {confidence}")
        
        # Check confidence threshold
        if confidence < 0.5:
            return await self.handle_low_confidence(nlp_result)
        
        # Execute based on intent
        if intent == 'open_app':
            return await self.handle_open_app(entities)
        elif intent == 'play_youtube':
            return await self.handle_play_youtube(entities)
        elif intent == 'send_message':
            return await self.handle_send_message(entities)
        elif intent == 'make_call':
            return await self.handle_make_call(entities)
        elif intent == 'get_weather':
            return await self.handle_get_weather(entities)
        elif intent == 'get_news':
            return await self.handle_get_news(entities)
        elif intent == 'set_reminder':
            return await self.handle_set_reminder(entities)
        elif intent == 'general_chat':
            return await self.handle_general_chat(nlp_result)
        else:
            return await self.handle_unknown_intent(nlp_result)
    
    async def handle_open_app(self, entities: Dict) -> Dict:
        """Handle opening applications"""
        app_name = entities.get('app_name', '')
        if not app_name:
            return {'success': False, 'message': 'No application name specified'}
        
        try:
            success = self.platform_manager.open_application(app_name)
            if success:
                await self.tts.speak(f"Opening {app_name}")
                return {'success': True, 'message': f'Opened {app_name}'}
            else:
                await self.tts.speak(f"Could not open {app_name}")
                return {'success': False, 'message': f'Could not open {app_name}'}
        except Exception as e:
            self.logger.error(f"Error opening app {app_name}: {e}")
            return {'success': False, 'message': f'Error opening {app_name}'}
    
    async def handle_play_youtube(self, entities: Dict) -> Dict:
        """Handle YouTube video playback"""
        search_term = entities.get('search_term', '')
        if not search_term:
            return {'success': False, 'message': 'No search term specified'}
        
        try:
            import pywhatkit as kit
            await self.tts.speak(f"Playing {search_term} on YouTube")
            kit.playonyt(search_term)
            return {'success': True, 'message': f'Playing {search_term} on YouTube'}
        except Exception as e:
            self.logger.error(f"Error playing YouTube video: {e}")
            return {'success': False, 'message': f'Error playing video: {str(e)}'}
    
    async def handle_send_message(self, entities: Dict) -> Dict:
        """Handle sending messages"""
        contact_name = entities.get('contact_name', '')
        if not contact_name:
            return {'success': False, 'message': 'No contact name specified'}
        
        try:
            # Get message content
            await self.tts.speak("What message would you like to send?")
            message = await self.listen_for_command()
            
            if not message:
                return {'success': False, 'message': 'No message content provided'}
            
            # Send message (implement based on your messaging system)
            # This is a placeholder implementation
            await self.tts.speak(f"Message sent to {contact_name}")
            return {'success': True, 'message': f'Message sent to {contact_name}'}
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return {'success': False, 'message': f'Error sending message: {str(e)}'}
    
    async def handle_make_call(self, entities: Dict) -> Dict:
        """Handle making phone calls"""
        contact_name = entities.get('contact_name', '')
        if not contact_name:
            return {'success': False, 'message': 'No contact name specified'}
        
        try:
            # Make call (implement based on your calling system)
            # This is a placeholder implementation
            await self.tts.speak(f"Calling {contact_name}")
            return {'success': True, 'message': f'Calling {contact_name}'}
            
        except Exception as e:
            self.logger.error(f"Error making call: {e}")
            return {'success': False, 'message': f'Error making call: {str(e)}'}
    
    async def handle_get_weather(self, entities: Dict) -> Dict:
        """Handle weather requests"""
        if not self.available_features['weather']:
            return {'success': False, 'message': 'Weather feature not available'}
        
        location = entities.get('location', 'current location')
        
        try:
            # Get weather information (implement with weather API)
            weather_info = await self.get_weather_info(location)
            await self.tts.speak(weather_info)
            return {'success': True, 'message': weather_info}
            
        except Exception as e:
            self.logger.error(f"Error getting weather: {e}")
            return {'success': False, 'message': f'Error getting weather: {str(e)}'}
    
    async def handle_get_news(self, entities: Dict) -> Dict:
        """Handle news requests"""
        if not self.available_features['news']:
            return {'success': False, 'message': 'News feature not available'}
        
        topic = entities.get('topic', 'general')
        
        try:
            # Get news information (implement with news API)
            news_info = await self.get_news_info(topic)
            await self.tts.speak(news_info)
            return {'success': True, 'message': news_info}
            
        except Exception as e:
            self.logger.error(f"Error getting news: {e}")
            return {'success': False, 'message': f'Error getting news: {str(e)}'}
    
    async def handle_set_reminder(self, entities: Dict) -> Dict:
        """Handle setting reminders"""
        task = entities.get('task', '')
        time = entities.get('time', '')
        
        if not task or not time:
            return {'success': False, 'message': 'Task and time required for reminder'}
        
        try:
            # Set reminder (implement with calendar/reminder system)
            reminder_info = f"Reminder set for {task} at {time}"
            await self.tts.speak(reminder_info)
            return {'success': True, 'message': reminder_info}
            
        except Exception as e:
            self.logger.error(f"Error setting reminder: {e}")
            return {'success': False, 'message': f'Error setting reminder: {str(e)}'}
    
    async def handle_general_chat(self, nlp_result: Dict) -> Dict:
        """Handle general conversation"""
        query = nlp_result.get('original_query', '')
        
        try:
            # Use chatbot for general conversation
            response = await self.get_chatbot_response(query)
            await self.tts.speak(response)
            return {'success': True, 'message': response}
            
        except Exception as e:
            self.logger.error(f"Error in general chat: {e}")
            return {'success': False, 'message': f'Error in conversation: {str(e)}'}
    
    async def handle_low_confidence(self, nlp_result: Dict) -> Dict:
        """Handle low confidence recognition"""
        await self.tts.speak("I didn't understand that clearly. Could you please repeat?")
        return {'success': False, 'message': 'Low confidence in speech recognition'}
    
    async def handle_unknown_intent(self, nlp_result: Dict) -> Dict:
        """Handle unknown intents"""
        await self.tts.speak("I'm not sure how to help with that. Could you try rephrasing?")
        return {'success': False, 'message': 'Unknown intent'}
    
    async def get_weather_info(self, location: str) -> str:
        """Get weather information (placeholder)"""
        # Implement with OpenWeatherMap API
        return f"Weather information for {location} is not available yet"
    
    async def get_news_info(self, topic: str) -> str:
        """Get news information (placeholder)"""
        # Implement with News API
        return f"Latest news about {topic} is not available yet"
    
    async def get_chatbot_response(self, query: str) -> str:
        """Get chatbot response (placeholder)"""
        # Implement with OpenAI or other chatbot service
        return f"I understand you said: {query}. This is a placeholder response."
    
    async def authenticate_user(self) -> bool:
        """Authenticate user with face recognition"""
        try:
            success, user_name, confidence = self.face_recognition.authenticate_face()
            if success:
                await self.tts.speak(f"Welcome back, {user_name}")
                return True
            else:
                await self.tts.speak("Authentication failed")
                return False
        except Exception as e:
            self.logger.error(f"Error in authentication: {e}")
            return False
    
    def get_system_status(self) -> Dict:
        """Get system status and capabilities"""
        return {
            'assistant_name': ASSISTANT_NAME,
            'features': self.available_features,
            'platform': self.platform_manager.get_system_info(),
            'dependencies': self.platform_manager.check_dependencies(),
            'voices': self.tts.get_available_voices(),
            'current_voice': self.tts.get_current_voice(),
            'languages': self.language_support.supported_languages,
            'current_language': self.language_support.current_language
        } 