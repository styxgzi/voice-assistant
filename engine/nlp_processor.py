import json
import re
from typing import Dict, List, Tuple, Optional
from collections import deque
import logging
from engine.config import NLP_CONFIG

# Optional spaCy import
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available, using fallback NLP processing")

class NLPProcessor:
    def __init__(self):
        self.nlp = None
        self.intents = self.load_intents()
        self.context_history = deque(maxlen=NLP_CONFIG['context_window_size'])
        self.logger = logging.getLogger(__name__)
        self.load_spacy_model()
        
    def load_spacy_model(self):
        """Load spaCy model for NLP processing"""
        if not SPACY_AVAILABLE:
            self.logger.warning("spaCy not available, using basic NLP processing")
            return
            
        try:
            self.nlp = spacy.load(NLP_CONFIG['model_name'])
            self.logger.info("spaCy model loaded successfully")
        except OSError:
            self.logger.warning(f"spaCy model {NLP_CONFIG['model_name']} not found.")
            try:
                import subprocess
                self.logger.info("Attempting to download spaCy model...")
                subprocess.run(["python", "-m", "spacy", "download", NLP_CONFIG['model_name']], 
                              check=True, capture_output=True)
                self.nlp = spacy.load(NLP_CONFIG['model_name'])
                self.logger.info("spaCy model downloaded and loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to download spaCy model: {e}")
                self.logger.warning("Using fallback NLP processing")
        except Exception as e:
            self.logger.error(f"Error loading spaCy model: {e}")
            self.logger.warning("Using fallback NLP processing")
    
    def load_intents(self) -> Dict:
        """Load intent patterns and responses"""
        return {
            'open_app': {
                'patterns': [
                    r'open\s+(\w+)',
                    r'launch\s+(\w+)',
                    r'start\s+(\w+)',
                    r'run\s+(\w+)'
                ],
                'entities': ['app_name'],
                'confidence_threshold': 0.8
            },
            'play_youtube': {
                'patterns': [
                    r'play\s+(.+?)\s+on\s+youtube',
                    r'youtube\s+(.+)',
                    r'search\s+(.+?)\s+on\s+youtube'
                ],
                'entities': ['search_term'],
                'confidence_threshold': 0.7
            },
            'send_message': {
                'patterns': [
                    r'send\s+message\s+to\s+(\w+)',
                    r'text\s+(\w+)',
                    r'message\s+(\w+)'
                ],
                'entities': ['contact_name'],
                'confidence_threshold': 0.8
            },
            'make_call': {
                'patterns': [
                    r'call\s+(\w+)',
                    r'phone\s+call\s+to\s+(\w+)',
                    r'dial\s+(\w+)'
                ],
                'entities': ['contact_name'],
                'confidence_threshold': 0.8
            },
            'get_weather': {
                'patterns': [
                    r'weather\s+(?:in\s+)?(.+)',
                    r'how\s+is\s+the\s+weather\s+(?:in\s+)?(.+)',
                    r'temperature\s+(?:in\s+)?(.+)'
                ],
                'entities': ['location'],
                'confidence_threshold': 0.7
            },
            'get_news': {
                'patterns': [
                    r'news\s+(?:about\s+)?(.+)',
                    r'latest\s+news\s+(?:about\s+)?(.+)',
                    r'what\s+is\s+happening\s+(?:with\s+)?(.+)'
                ],
                'entities': ['topic'],
                'confidence_threshold': 0.7
            },
            'set_reminder': {
                'patterns': [
                    r'remind\s+me\s+to\s+(.+?)\s+(?:at\s+)?(.+)',
                    r'set\s+reminder\s+for\s+(.+?)\s+(?:at\s+)?(.+)',
                    r'reminder\s+(.+?)\s+(?:at\s+)?(.+)'
                ],
                'entities': ['task', 'time'],
                'confidence_threshold': 0.8
            },
            'general_chat': {
                'patterns': [
                    r'how\s+are\s+you',
                    r'what\s+can\s+you\s+do',
                    r'tell\s+me\s+a\s+joke',
                    r'what\s+time\s+is\s+it'
                ],
                'entities': [],
                'confidence_threshold': 0.6
            }
        }
    
    def process_query(self, query: str) -> Dict:
        """Process user query and extract intent and entities"""
        if not query or not query.strip():
            return {'intent': 'unknown', 'confidence': 0.0, 'entities': {}}
        
        # Add to context history
        self.context_history.append(query.lower())
        
        # Process with spaCy if available, otherwise use fallback
        if self.nlp:
            doc = self.nlp(query.lower())
        else:
            doc = self.create_fallback_doc(query.lower())
        
        # Extract intent and entities
        intent_result = self.extract_intent(doc, query)
        entities = self.extract_entities(doc, intent_result['intent'])
        
        return {
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'entities': entities,
            'context': list(self.context_history),
            'original_query': query
        }
    
    def create_fallback_doc(self, text: str):
        """Create a fallback document object when spaCy is not available"""
        class FallbackDoc:
            def __init__(self, text):
                self.text = text
                self.vector_norm = 0.0
                self.ents = []
                self.noun_chunks = []
            
            def __iter__(self):
                # Create simple token objects
                words = text.split()
                for word in words:
                    yield FallbackToken(word)
        
        class FallbackToken:
            def __init__(self, text):
                self.text = text
                self.lemma_ = text.lower()
                self.pos_ = 'NOUN'  # Default
                self.is_stop = text.lower() in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
                self.is_punct = text in ['.', ',', '!', '?', ';', ':']
                self.is_alpha = text.isalpha()
        
        return FallbackDoc(text)
    
    def extract_intent(self, doc, query: str) -> Dict:
        """Extract intent from processed query"""
        best_intent = 'unknown'
        best_confidence = 0.0
        
        for intent_name, intent_data in self.intents.items():
            # Set current intent for confidence calculation
            self._current_intent = intent_name
            confidence = self.calculate_intent_confidence(doc, query, intent_data)
            if confidence > best_confidence and confidence >= intent_data['confidence_threshold']:
                best_confidence = confidence
                best_intent = intent_name
        
        return {
            'intent': best_intent,
            'confidence': best_confidence
        }
    
    def calculate_intent_confidence(self, doc, query: str, intent_data: Dict) -> float:
        """Calculate confidence score for intent matching"""
        confidence = 0.0
        
        # Pattern matching
        for pattern in intent_data['patterns']:
            if re.search(pattern, query, re.IGNORECASE):
                confidence += 0.4
        
        # Keyword matching
        keywords = self.extract_keywords(doc)
        # Get intent name from the calling function context
        intent_name = getattr(self, '_current_intent', 'unknown')
        intent_keywords = self.get_intent_keywords(intent_name)
        
        keyword_matches = len(set(keywords) & set(intent_keywords))
        if intent_keywords:
            confidence += (keyword_matches / len(intent_keywords)) * 0.3
        
        # Semantic similarity (if spaCy vectors are available)
        if hasattr(doc, 'vector_norm') and doc.vector_norm > 0:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def extract_keywords(self, doc) -> List[str]:
        """Extract important keywords from the document"""
        keywords = []
        for token in doc:
            if not token.is_stop and not token.is_punct and token.is_alpha:
                keywords.append(token.lemma_.lower())
        return keywords
    
    def get_intent_keywords(self, intent: str) -> List[str]:
        """Get keywords associated with each intent"""
        intent_keywords = {
            'open_app': ['open', 'launch', 'start', 'run', 'app', 'application'],
            'play_youtube': ['play', 'youtube', 'video', 'search', 'watch'],
            'send_message': ['send', 'message', 'text', 'sms', 'contact'],
            'make_call': ['call', 'phone', 'dial', 'ring', 'contact'],
            'get_weather': ['weather', 'temperature', 'forecast', 'climate'],
            'get_news': ['news', 'latest', 'update', 'happening', 'current'],
            'set_reminder': ['remind', 'reminder', 'alarm', 'schedule', 'time'],
            'general_chat': ['how', 'what', 'when', 'where', 'why', 'joke', 'time']
        }
        return intent_keywords.get(intent, [])
    
    def extract_entities(self, doc, intent: str) -> Dict:
        """Extract entities from the document based on intent"""
        entities = {}
        
        if intent == 'open_app':
            entities['app_name'] = self.extract_app_name(doc)
        elif intent == 'play_youtube':
            entities['search_term'] = self.extract_search_term(doc)
        elif intent == 'send_message':
            entities['contact_name'] = self.extract_contact_name(doc)
        elif intent == 'make_call':
            entities['contact_name'] = self.extract_contact_name(doc)
        elif intent == 'get_weather':
            entities['location'] = self.extract_location(doc)
        elif intent == 'get_news':
            entities['topic'] = self.extract_topic(doc)
        elif intent == 'set_reminder':
            entities['task'], entities['time'] = self.extract_reminder_details(doc)
        
        return entities
    
    def extract_app_name(self, doc) -> str:
        """Extract application name from document"""
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop:
                return token.text
        return ""
    
    def extract_search_term(self, doc) -> str:
        """Extract search term for YouTube"""
        # Look for content between 'play' and 'youtube'
        text = doc.text if hasattr(doc, 'text') else str(doc)
        match = re.search(r'play\s+(.+?)\s+on\s+youtube', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
    
    def extract_contact_name(self, doc) -> str:
        """Extract contact name from document"""
        if hasattr(doc, 'ents'):
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    return ent.text
        # Fallback to noun phrases
        if hasattr(doc, 'noun_chunks'):
            for chunk in doc.noun_chunks:
                if chunk.root.pos_ in ['NOUN', 'PROPN']:
                    return chunk.text
        return ""
    
    def extract_location(self, doc) -> str:
        """Extract location from document"""
        if hasattr(doc, 'ents'):
            for ent in doc.ents:
                if ent.label_ in ['GPE', 'LOC']:
                    return ent.text
        return ""
    
    def extract_topic(self, doc) -> str:
        """Extract news topic from document"""
        # Look for content after 'news' or 'about'
        text = doc.text if hasattr(doc, 'text') else str(doc)
        match = re.search(r'news\s+(?:about\s+)?(.+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
    
    def extract_reminder_details(self, doc) -> Tuple[str, str]:
        """Extract reminder task and time"""
        text = doc.text if hasattr(doc, 'text') else str(doc)
        match = re.search(r'remind\s+me\s+to\s+(.+?)\s+(?:at\s+)?(.+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return "", ""
    
    def get_context(self) -> List[str]:
        """Get conversation context"""
        return list(self.context_history)
    
    def clear_context(self):
        """Clear conversation context"""
        self.context_history.clear() 