import os
import eel
import asyncio
import logging
import subprocess
from engine.enhanced_command import EnhancedCommandProcessor
from engine.config import ASSISTANT_NAME

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class PrimeAssistant:
    def __init__(self):
        self.command_processor = EnhancedCommandProcessor()
        self.logger = logging.getLogger(__name__)
        
    async def start(self):
        """Start the Prime assistant"""
        try:
            # Initialize web interface
            eel.init("www")
            
            # Setup Eel exposed functions
            self.setup_eel_functions()
            
            # Start face authentication
            await self.authenticate_user()
            
            # Start the web interface
            await self.start_web_interface()
            
        except Exception as e:
            self.logger.error(f"Error starting Prime assistant: {e}")
    
    def setup_eel_functions(self):
        """Setup Eel exposed functions for web interface"""
        
        @eel.expose
        def init():
            """Initialize the assistant"""
            try:
                # Run device setup if file exists
                if os.path.exists('device.bat'):
                    subprocess.call([r'device.bat'])
                eel.hideLoader()
                
                # Start authentication in background
                asyncio.create_task(self.authenticate_user())
                
            except Exception as e:
                self.logger.error(f"Error in init: {e}")
        
        @eel.expose
        def process_command(message=None):
            """Process voice or text command"""
            try:
                # Run async function in event loop
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(self.command_processor.process_command(message))
                return result
            except Exception as e:
                self.logger.error(f"Error processing command: {e}")
                return {'success': False, 'message': f'Error: {str(e)}'}
        
        @eel.expose
        def get_system_status():
            """Get system status and capabilities"""
            try:
                return self.command_processor.get_system_status()
            except Exception as e:
                self.logger.error(f"Error getting system status: {e}")
                return {}
        
        @eel.expose
        def speak_text(text):
            """Speak text using TTS"""
            try:
                # Run async function in event loop
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(self.command_processor.tts.speak(text))
                return {'success': True}
            except Exception as e:
                self.logger.error(f"Error speaking text: {e}")
                return {'success': False, 'message': str(e)}
    
    async def authenticate_user(self):
        """Authenticate user with face recognition"""
        try:
            eel.hideLoader()
            await self.command_processor.tts.speak("Ready for Face Authentication")
            
            success = await self.command_processor.authenticate_user()
            
            if success:
                eel.hideFaceAuth()
                await self.command_processor.tts.speak("Face Authentication Successful")
                eel.hideFaceAuthSuccess()
                await self.command_processor.tts.speak(f"Hello, Welcome Sir, I am {ASSISTANT_NAME}, How can I Help You")
                eel.hideStart()
                await self.play_start_sound()
            else:
                await self.command_processor.tts.speak("Face Authentication Failed")
                
        except Exception as e:
            self.logger.error(f"Error in authentication: {e}")
            await self.command_processor.tts.speak("Authentication error occurred")
    
    async def play_start_sound(self):
        """Play assistant start sound"""
        try:
            from playsound import playsound
            music_dir = os.path.join("www", "assets", "audio", "start_sound.mp3")
            if os.path.exists(music_dir):
                playsound(music_dir)
        except Exception as e:
            self.logger.error(f"Error playing start sound: {e}")
    
    async def start_web_interface(self):
        """Start the web interface"""
        try:
            # Open browser
            self.open_browser()
            
            # Start Eel
            eel.start('index.html', mode=None, host='localhost', block=True)
            
        except Exception as e:
            self.logger.error(f"Error starting web interface: {e}")
    
    def open_browser(self):
        """Open browser cross-platform"""
        try:
            system = os.name
            if system == 'nt':  # Windows
                os.system('start chrome.exe --app="http://localhost:8000/index.html"')
            elif system == 'posix':  # macOS/Linux
                import subprocess
                subprocess.run(['open', '-a', 'Google Chrome', 'http://localhost:8000/index.html'])
        except Exception as e:
            self.logger.error(f"Error opening browser: {e}")

def start():
    """Start the Prime assistant"""
    assistant = PrimeAssistant()
    asyncio.run(assistant.start())

if __name__ == "__main__":
    start()