#!/usr/bin/env python3
"""
Test script for Prime Assistant
This script tests all major components to ensure they work correctly.
"""

import sys
import os
import logging
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported"""
    logger.info("Testing imports...")
    
    try:
        from engine.config import ASSISTANT_NAME, SPEECH_RECOGNITION_CONFIG
        logger.info(f"✓ Config loaded: Assistant name = {ASSISTANT_NAME}")
    except Exception as e:
        logger.error(f"✗ Config import failed: {e}")
        return False
    
    try:
        from engine.enhanced_speech import EnhancedSpeechRecognition
        logger.info("✓ Enhanced speech recognition imported")
    except Exception as e:
        logger.error(f"✗ Enhanced speech import failed: {e}")
        return False
    
    try:
        from engine.nlp_processor import NLPProcessor
        logger.info("✓ NLP processor imported")
    except Exception as e:
        logger.error(f"✗ NLP processor import failed: {e}")
        return False
    
    try:
        from engine.enhanced_face_recognition import EnhancedFaceRecognition
        logger.info("✓ Enhanced face recognition imported")
    except Exception as e:
        logger.error(f"✗ Enhanced face recognition import failed: {e}")
        return False
    
    try:
        from engine.cross_platform import CrossPlatformManager
        logger.info("✓ Cross platform manager imported")
    except Exception as e:
        logger.error(f"✗ Cross platform manager import failed: {e}")
        return False
    
    try:
        from engine.enhanced_tts import EnhancedTTS
        logger.info("✓ Enhanced TTS imported")
    except Exception as e:
        logger.error(f"✗ Enhanced TTS import failed: {e}")
        return False
    
    try:
        from engine.enhanced_command import EnhancedCommandProcessor
        logger.info("✓ Enhanced command processor imported")
    except Exception as e:
        logger.error(f"✗ Enhanced command processor import failed: {e}")
        return False
    
    return True

def test_nlp_processor():
    """Test NLP processor functionality"""
    logger.info("Testing NLP processor...")
    
    try:
        from engine.nlp_processor import NLPProcessor
        nlp = NLPProcessor()
        
        # Test intent recognition
        test_queries = [
            "open chrome",
            "play despacito on youtube",
            "send message to john",
            "what's the weather in new york",
            "how are you"
        ]
        
        for query in test_queries:
            result = nlp.process_query(query)
            logger.info(f"✓ Query: '{query}' -> Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
        
        return True
    except Exception as e:
        logger.error(f"✗ NLP processor test failed: {e}")
        return False

def test_cross_platform():
    """Test cross-platform functionality"""
    logger.info("Testing cross-platform manager...")
    
    try:
        from engine.cross_platform import CrossPlatformManager
        platform_mgr = CrossPlatformManager()
        
        # Test system info
        system_info = platform_mgr.get_system_info()
        logger.info(f"✓ System: {system_info['system']}")
        logger.info(f"✓ Platform: {system_info['platform']}")
        logger.info(f"✓ Python: {system_info['python_version']}")
        
        # Test dependency checking
        dependencies = platform_mgr.check_dependencies()
        logger.info(f"✓ Dependencies checked: {len(dependencies)} items")
        
        return True
    except Exception as e:
        logger.error(f"✗ Cross-platform test failed: {e}")
        return False

def test_tts():
    """Test TTS functionality"""
    logger.info("Testing TTS...")
    
    try:
        from engine.enhanced_tts import EnhancedTTS
        tts = EnhancedTTS()
        
        # Test voice listing
        voices = tts.get_available_voices()
        logger.info(f"✓ Available voices: {len(voices)}")
        
        # Test current voice
        current_voice = tts.get_current_voice()
        if current_voice:
            logger.info(f"✓ Current voice: {current_voice['name']}")
        
        return True
    except Exception as e:
        logger.error(f"✗ TTS test failed: {e}")
        return False

def test_face_recognition():
    """Test face recognition functionality"""
    logger.info("Testing face recognition...")
    
    try:
        from engine.enhanced_face_recognition import EnhancedFaceRecognition
        face_rec = EnhancedFaceRecognition()
        
        # Test user listing
        users = face_rec.list_users()
        logger.info(f"✓ Registered users: {len(users)}")
        
        # Test statistics
        stats = face_rec.get_user_statistics()
        logger.info(f"✓ User statistics: {len(stats)} entries")
        
        return True
    except Exception as e:
        logger.error(f"✗ Face recognition test failed: {e}")
        return False

async def test_command_processor():
    """Test command processor functionality"""
    logger.info("Testing command processor...")
    
    try:
        from engine.enhanced_command import EnhancedCommandProcessor
        cmd_processor = EnhancedCommandProcessor()
        
        # Test system status
        status = cmd_processor.get_system_status()
        logger.info(f"✓ System status retrieved: {len(status)} items")
        
        # Test command processing (without actual speech)
        test_commands = [
            "open chrome",
            "play despacito on youtube",
            "what's the weather"
        ]
        
        for cmd in test_commands:
            result = await cmd_processor.process_command(cmd)
            logger.info(f"✓ Command: '{cmd}' -> Success: {result['success']}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Command processor test failed: {e}")
        return False

def test_web_interface():
    """Test web interface files"""
    logger.info("Testing web interface...")
    
    required_files = [
        "www/index.html",
        "www/style.css",
        "www/main.js",
        "www/controller.js"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            logger.info(f"✓ {file_path} exists")
        else:
            logger.error(f"✗ {file_path} missing")
            return False
    
    return True

def main():
    """Run all tests"""
    logger.info("=" * 50)
    logger.info("PRIME ASSISTANT - COMPONENT TEST")
    logger.info("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("NLP Processor Test", test_nlp_processor),
        ("Cross-Platform Test", test_cross_platform),
        ("TTS Test", test_tts),
        ("Face Recognition Test", test_face_recognition),
        ("Web Interface Test", test_web_interface),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
    
    # Test async command processor
    logger.info(f"\n--- Command Processor Test ---")
    try:
        result = asyncio.run(test_command_processor())
        if result:
            passed += 1
            logger.info("✓ Command Processor Test PASSED")
        else:
            logger.error("✗ Command Processor Test FAILED")
    except Exception as e:
        logger.error(f"✗ Command Processor Test FAILED with exception: {e}")
    
    total += 1
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Passed: {passed}/{total}")
    logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! Prime Assistant is ready to use.")
        logger.info("Run 'python main.py' to start the assistant.")
    else:
        logger.error("❌ Some tests failed. Please check the error messages above.")
        logger.info("You may need to install missing dependencies or fix configuration issues.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 