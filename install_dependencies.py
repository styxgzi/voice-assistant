import os
import subprocess
import sys
import platform
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"Python version: {sys.version}")
    return True

def install_package(package, upgrade=False):
    """Install a single package"""
    try:
        cmd = [sys.executable, "-m", "pip", "install"]
        if upgrade:
            cmd.append("--upgrade")
        cmd.append(package)
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package}: {e.stderr}")
        return False

def install_spacy_model():
    """Install spaCy English model"""
    try:
        logger.info("Installing spaCy English model...")
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                      check=True, capture_output=True)
        logger.info("spaCy model installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install spaCy model: {e}")
        return False

def install_system_dependencies():
    """Install system-specific dependencies"""
    system = platform.system().lower()
    
    if system == "windows":
        logger.info("Windows detected - no additional system dependencies needed")
    elif system == "darwin":  # macOS
        logger.info("macOS detected - checking for Homebrew...")
        try:
            subprocess.run(["brew", "--version"], check=True, capture_output=True)
            logger.info("Homebrew is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Homebrew not found. Please install it from https://brew.sh/")
    elif system == "linux":
        logger.info("Linux detected - checking for system packages...")
        try:
            # Try to install portaudio (required for pyaudio)
            subprocess.run(["sudo", "apt-get", "update"], check=True, capture_output=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "portaudio19-dev", "python3-pyaudio"], 
                          check=True, capture_output=True)
            logger.info("System dependencies installed")
        except subprocess.CalledProcessError:
            logger.warning("Could not install system dependencies automatically")

def main():
    """Main installation function"""
    logger.info("Starting Prime Assistant dependency installation...")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install system dependencies
    install_system_dependencies()
    
    # Core dependencies
    core_dependencies = [
        "eel>=0.16.0",
        "pyaudio>=0.2.11", 
        "pyautogui>=0.9.54",
        "pvporcupine>=2.2.0",
        "hugchat>=0.0.47",
        "playsound>=1.3.0"
    ]
    
    # Enhanced dependencies
    enhanced_dependencies = [
        "SpeechRecognition>=3.10.0",
        "webrtcvad>=2.0.10",
        "numpy>=1.24.0",
        "spacy>=3.7.0",
        "face-recognition>=1.3.0",
        "opencv-python>=4.8.0",
        "cryptography>=41.0.0",
        "pygame>=2.5.0",
        "pyttsx3>=2.90",
        "pywhatkit>=5.4.3",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0"
    ]
    
    # Optional advanced dependencies
    optional_dependencies = [
        "azure-cognitiveservices-speech>=1.34.0",
        "TTS>=0.22.0",
        "transformers>=4.35.0",
        "torch>=2.1.0"
    ]
    
    # Install core dependencies
    logger.info("Installing core dependencies...")
    failed_core = []
    for package in core_dependencies:
        if not install_package(package):
            failed_core.append(package)
    
    # Install enhanced dependencies
    logger.info("Installing enhanced dependencies...")
    failed_enhanced = []
    for package in enhanced_dependencies:
        if not install_package(package):
            failed_enhanced.append(package)
    
    # Install optional dependencies
    logger.info("Installing optional dependencies...")
    failed_optional = []
    for package in optional_dependencies:
        if not install_package(package):
            failed_optional.append(package)
            logger.warning(f"Optional package {package} failed to install")
    
    # Install spaCy model
    if "spacy>=3.7.0" not in failed_enhanced:
        install_spacy_model()
    
    # Report results
    logger.info("\n" + "="*50)
    logger.info("INSTALLATION SUMMARY")
    logger.info("="*50)
    
    if failed_core:
        logger.error(f"Failed core dependencies: {failed_core}")
    else:
        logger.info("✓ All core dependencies installed successfully")
    
    if failed_enhanced:
        logger.error(f"Failed enhanced dependencies: {failed_enhanced}")
    else:
        logger.info("✓ All enhanced dependencies installed successfully")
    
    if failed_optional:
        logger.warning(f"Failed optional dependencies: {failed_optional}")
        logger.info("✓ Optional dependencies are not required for basic functionality")
    
    if not failed_core and not failed_enhanced:
        logger.info("\n🎉 Prime Assistant is ready to use!")
        logger.info("Run 'python main.py' to start the assistant")
    else:
        logger.error("\n❌ Some dependencies failed to install")
        logger.error("Please check the error messages above and try again")

if __name__ == "__main__":
    main()
