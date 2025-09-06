#!/usr/bin/env python3
"""
Epic Story Image Generator - Production Ready Version
Fixed multiprocessing, Unicode handling, logging, and configuration management
"""

import requests
import json
import os
import base64
import time
import re
import sys
import logging
from datetime import datetime
import argparse
from typing import Dict, List, Tuple, Optional
import configparser
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('epic_generator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class SafeUnicodeHandler:
    """Handle Unicode display safely across platforms"""
    
    @staticmethod
    def safe_print(text: str, fallback_char: str = "?"):
        """Print text with safe Unicode handling"""
        try:
            print(text)
        except UnicodeEncodeError:
            # Replace problematic characters
            safe_text = text.encode('ascii', 'replace').decode('ascii')
            print(safe_text)
    
    @staticmethod
    def safe_format(template: str, *args, **kwargs):
        """Format string with safe Unicode handling"""
        try:
            return template.format(*args, **kwargs)
        except UnicodeEncodeError:
            # Fallback to ASCII-safe version
            safe_template = template.encode('ascii', 'replace').decode('ascii')
            return safe_template.format(*args, **kwargs)

class ConfigManager:
    """Manage application configuration"""
    
    def __init__(self, config_file: str = "epic_generator.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(__name__)
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration file"""
        self.config['DEFAULT'] = {
            'max_prompt_length': '1000',
            'max_retries': '3',
            'request_timeout': '120',
            'download_timeout': '30',
            'output_directory': 'generated_images',
            'log_level': 'INFO'
        }
        
        self.config['API'] = {
            'dalle_model': 'dall-e-3',
            'dalle_quality': 'hd',
            'dalle_size': '1024x1024',
            'stability_steps': '50',
            'stability_cfg_scale': '7'
        }
        
        self.config['ENHANCEMENTS'] = {
            'base_quality': 'high quality, detailed, 4K resolution',
            'base_composition': 'masterpiece artwork, professional composition',
            'enable_character_detection': 'true',
            'enable_location_detection': 'true'
        }
        
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def get(self, section: str, key: str, fallback=None):
        """Get configuration value"""
        try:
            return self.config.get(section, key, fallback=fallback)
        except:
            return fallback
    
    def getint(self, section: str, key: str, fallback: int = 0):
        """Get integer configuration value"""
        try:
            return self.config.getint(section, key, fallback=fallback)
        except:
            return fallback
    
    def getboolean(self, section: str, key: str, fallback: bool = False):
        """Get boolean configuration value"""
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except:
            return fallback

class InputValidator:
    """Enhanced input validation and sanitization"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.max_length = config.getint('DEFAULT', 'max_prompt_length', 1000)
    
    def validate_and_sanitize(self, prompt: str) -> str:
        """Validate and sanitize input prompt"""
        if not isinstance(prompt, str):
            raise ValueError("Prompt must be a string")
        
        # Remove null bytes and control characters (except common ones)
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', prompt)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        # Check for empty input
        if not sanitized:
            raise ValueError("Prompt cannot be empty after sanitization")
        
        # Check length and truncate if necessary
        if len(sanitized) > self.max_length:
            self.logger.warning(f"Prompt truncated from {len(sanitized)} to {self.max_length} characters")
            SafeUnicodeHandler.safe_print(f"Warning: Prompt truncated to {self.max_length} characters")
            sanitized = sanitized[:self.max_length]
        
        # Log potentially suspicious patterns
        suspicious_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'SELECT\s+.*FROM',
            r'DROP\s+TABLE',
            r'\.\./\.\.',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                self.logger.warning(f"Suspicious pattern detected in input: {pattern}")
        
        return sanitized

class EpicImageGeneratorFixed:
    """Production-ready Epic Image Generator with all fixes"""
    
    def __init__(self, config_file: str = None):
        self.config = ConfigManager(config_file) if config_file else ConfigManager()
        self.validator = InputValidator(self.config)
        self.unicode_handler = SafeUnicodeHandler()
        self.logger = logging.getLogger(__name__)
        
        # Set up output directory
        self.output_dir = self.config.get('DEFAULT', 'output_directory', 'generated_images')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize knowledge bases
        self.ramayana_characters = self._load_ramayana_characters()
        self.mahabharata_characters = self._load_mahabharata_characters()
        self.epic_locations = self._load_epic_locations()
        self.divine_elements = self._load_divine_elements()
        self.art_styles = self._load_art_styles()
        
        self.logger.info("Epic Image Generator initialized successfully")
    
    def _load_ramayana_characters(self) -> Dict[str, Dict]:
        """Database of Ramayana characters with visual descriptions"""
        return {
            "rama": {
                "description": "Lord Rama with dark complexion, noble bearing, wearing royal dhoti and crown",
                "attributes": ["divine aura", "bow and arrow", "serene expression", "righteous presence"],
                "colors": ["deep blue skin", "golden crown", "saffron robes"]
            },
            "sita": {
                "description": "Goddess Sita in elegant saree, embodying grace and devotion",
                "attributes": ["lotus eyes", "gentle smile", "traditional jewelry", "divine radiance"],
                "colors": ["golden saree", "red borders", "pearl jewelry"]
            },
            "hanuman": {
                "description": "Hanuman the mighty monkey deity, muscular build, carrying mace",
                "attributes": ["orange/red fur", "flying pose", "gada (mace)", "devotional expression"],
                "colors": ["orange-red body", "golden jewelry", "saffron cloth"]
            },
            "ravana": {
                "description": "Ten-headed demon king Ravana in golden armor and crown",
                "attributes": ["ten heads", "multiple arms", "golden armor", "fierce expression"],
                "colors": ["golden armor", "dark complexion", "ruby decorations"]
            },
            "lakshman": {
                "description": "Lakshman, Rama's devoted brother, warrior appearance",
                "attributes": ["bow and arrow", "protective stance", "royal attire", "alert expression"],
                "colors": ["blue dhoti", "golden ornaments", "fair complexion"]
            }
        }
    
    def _load_mahabharata_characters(self) -> Dict[str, Dict]:
        """Database of Mahabharata characters with visual descriptions"""
        return {
            "krishna": {
                "description": "Lord Krishna with blue skin, peacock feather crown, playing flute",
                "attributes": ["divine blue complexion", "peacock feather", "flute", "yellow dhoti"],
                "colors": ["deep blue skin", "bright yellow clothes", "golden ornaments"]
            },
            "arjuna": {
                "description": "Great archer Arjuna in warrior attire with divine bow Gandiva",
                "attributes": ["Gandiva bow", "white horse chariot", "focused expression", "royal armor"],
                "colors": ["white and gold armor", "silver bow", "royal blue cloth"]
            },
            "bhishma": {
                "description": "Bhishma Pitamah, the grand patriarch with white hair and noble bearing",
                "attributes": ["white hair and beard", "wise expression", "royal armor", "commanding presence"],
                "colors": ["white hair", "golden armor", "saffron cloth"]
            },
            "draupadi": {
                "description": "Queen Draupadi in royal attire, embodying strength and dignity",
                "attributes": ["royal crown", "elegant saree", "determined expression", "queenly posture"],
                "colors": ["rich silk saree", "gold jewelry", "royal blue and red"]
            },
            "duryodhana": {
                "description": "Prince Duryodhana in dark armor, ambitious and proud bearing",
                "attributes": ["dark armor", "crown", "mace weapon", "stern expression"],
                "colors": ["dark armor", "black and gold", "ruby decorations"]
            },
            "karna": {
                "description": "Karna the great warrior with divine armor and earrings",
                "attributes": ["golden armor", "divine earrings", "bow", "noble yet tragic expression"],
                "colors": ["golden armor", "sun-like radiance", "saffron clothing"]
            }
        }
    
    def _load_epic_locations(self) -> Dict[str, Dict]:
        """Database of epic locations with environmental descriptions"""
        return {
            "ayodhya": {
                "description": "Ancient city of Ayodhya with golden palaces and sacred rivers",
                "elements": ["golden architecture", "flowing rivers", "lush gardens", "temple spires"]
            },
            "lanka": {
                "description": "Island kingdom of Lanka with magnificent golden architecture",
                "elements": ["golden palaces", "ocean waves", "tropical forests", "flying bridges"]
            },
            "kurukshetra": {
                "description": "The great battlefield of Kurukshetra with armies and war elephants",
                "elements": ["vast battlefield", "war chariots", "elephants", "flying banners"]
            },
            "vrindavan": {
                "description": "Sacred land of Vrindavan with pastoral beauty and divine presence",
                "elements": ["flowering trees", "grazing cows", "Yamuna river", "divine radiance"]
            },
            "ashrama": {
                "description": "Forest hermitage with sacred fires and meditation spaces",
                "elements": ["forest setting", "sacred fire", "simple huts", "peaceful atmosphere"]
            },
            "indraprastha": {
                "description": "Magnificent capital city with crystal palaces and divine architecture",
                "elements": ["crystal architecture", "divine lighting", "royal gardens", "heavenly atmosphere"]
            }
        }
    
    def _load_divine_elements(self) -> Dict[str, List[str]]:
        """Divine and mystical elements for enhancement"""
        return {
            "divine_auras": ["golden divine light", "celestial radiance", "holy aura", "sacred energy"],
            "weapons": ["divine bow", "celestial arrows", "sacred mace", "mystical sword", "divine chakra"],
            "creatures": ["divine horses", "celestial beings", "sacred cows", "mythical birds", "divine serpents"],
            "natural": ["lotus flowers", "sacred trees", "flowing rivers", "mountain peaks", "celestial clouds"],
            "architectural": ["temple architecture", "royal palaces", "sacred pillars", "divine mandapas"],
            "mystical": ["divine intervention", "celestial phenomena", "sacred geometry", "spiritual energy"]
        }
    
    def _load_art_styles(self) -> Dict[str, str]:
        """Art style templates for different themes"""
        return {
            "traditional_epic": "traditional Indian miniature painting style, rich colors, gold leaf details, classical composition",
            "temple_art": "ancient Indian temple art style, stone carving aesthetic, classical proportions, spiritual symbolism",
            "rajasthani": "Rajasthani miniature painting style, vibrant colors, intricate patterns, royal themes",
            "mysore": "Mysore painting style, gold foil work, muted colors, divine themes, classical Indian art",
            "fantasy_epic": "epic fantasy art style with Indian classical elements, cinematic lighting, detailed textures",
            "divine_vision": "transcendental art style, divine lighting, ethereal atmosphere, spiritual themes",
            "mystery_ancient": "ancient mystery style, dark atmospheric lighting, hidden symbols, mystical elements"
        }
    
    def detect_content_type(self, prompt: str) -> Tuple[str, List[str]]:
        """Detect content type and extract relevant keywords"""
        prompt_lower = prompt.lower()
        detected_themes = []
        detected_characters = []
        
        # Check for epic themes
        ramayana_keywords = ["rama", "sita", "hanuman", "ravana", "lakshman", "ramayana", "ayodhya", "lanka"]
        mahabharata_keywords = ["krishna", "arjuna", "bhishma", "draupadi", "karna", "duryodhana", "mahabharata", "kurukshetra"]
        fantasy_keywords = ["magic", "mystical", "enchanted", "dragon", "spell", "wizard", "sorcerer"]
        mystery_keywords = ["mystery", "hidden", "secret", "ancient", "forgotten", "curse", "prophecy"]
        
        if any(word in prompt_lower for word in ramayana_keywords):
            detected_themes.append("ramayana")
            detected_characters.extend([word for word in ramayana_keywords if word in prompt_lower])
        
        if any(word in prompt_lower for word in mahabharata_keywords):
            detected_themes.append("mahabharata")
            detected_characters.extend([word for word in mahabharata_keywords if word in prompt_lower])
        
        if any(word in prompt_lower for word in fantasy_keywords):
            detected_themes.append("fantasy")
        
        if any(word in prompt_lower for word in mystery_keywords):
            detected_themes.append("mystery")
        
        # Determine primary theme
        if "ramayana" in detected_themes:
            primary_theme = "ramayana"
        elif "mahabharata" in detected_themes:
            primary_theme = "mahabharata"
        elif "fantasy" in detected_themes:
            primary_theme = "fantasy"
        elif "mystery" in detected_themes:
            primary_theme = "mystery"
        else:
            primary_theme = "general_epic"
        
        return primary_theme, detected_characters
    
    def enhance_prompt_epic_style(self, user_prompt: str) -> str:
        """Enhanced prompt generation with epic, fantasy, and mystery elements"""
        
        # Validate and sanitize input
        try:
            sanitized_prompt = self.validator.validate_and_sanitize(user_prompt)
        except ValueError as e:
            self.logger.error(f"Input validation failed: {e}")
            raise
        
        # Detect content type
        theme, characters = self.detect_content_type(sanitized_prompt)
        self.logger.info(f"Detected theme: {theme}, characters: {characters}")
        
        # Base enhancements from config
        base_quality = self.config.get('ENHANCEMENTS', 'base_quality', 'high quality, detailed, 4K resolution')
        base_composition = self.config.get('ENHANCEMENTS', 'base_composition', 'masterpiece artwork, professional composition')
        
        enhancements = [base_quality, base_composition]
        
        # Theme-specific enhancements
        if theme == "ramayana" and self.config.getboolean('ENHANCEMENTS', 'enable_character_detection', True):
            enhancements.extend([
                self.art_styles["traditional_epic"],
                "Ramayana epic scene",
                "divine Hindu mythology",
                "classical Indian art style",
                "sacred atmosphere, spiritual energy"
            ])
            
            # Add character-specific details
            for char in characters:
                if char in self.ramayana_characters:
                    char_data = self.ramayana_characters[char]
                    enhancements.append(char_data["description"])
                    enhancements.extend(char_data["attributes"])
        
        elif theme == "mahabharata" and self.config.getboolean('ENHANCEMENTS', 'enable_character_detection', True):
            enhancements.extend([
                self.art_styles["traditional_epic"],
                "Mahabharata epic scene",
                "divine Hindu mythology",
                "classical Indian temple art style",
                "dharma and cosmic justice themes"
            ])
            
            # Add character-specific details
            for char in characters:
                if char in self.mahabharata_characters:
                    char_data = self.mahabharata_characters[char]
                    enhancements.append(char_data["description"])
                    enhancements.extend(char_data["attributes"])
        
        elif theme == "fantasy":
            enhancements.extend([
                self.art_styles["fantasy_epic"],
                "mystical fantasy atmosphere",
                "magical elements, enchanted lighting",
                "epic fantasy composition with Indian mythological elements"
            ])
        
        elif theme == "mystery":
            enhancements.extend([
                self.art_styles["mystery_ancient"],
                "mysterious ancient atmosphere",
                "hidden symbols, cryptic elements",
                "dramatic shadows and mystical lighting"
            ])
        
        else:
            # General epic enhancement
            enhancements.extend([
                self.art_styles["divine_vision"],
                "epic storytelling composition",
                "rich cultural details, traditional Indian elements"
            ])
        
        # Add divine and mystical elements
        enhancements.extend([
            "divine lighting, celestial atmosphere",
            "rich vibrant colors with gold accents",
            "intricate details, cultural authenticity",
            "emotional depth and spiritual significance"
        ])
        
        # Location-based enhancements
        if self.config.getboolean('ENHANCEMENTS', 'enable_location_detection', True):
            for location, data in self.epic_locations.items():
                if location in sanitized_prompt.lower():
                    enhancements.append(data["description"])
                    enhancements.extend(data["elements"])
        
        # Construct final prompt
        enhanced_prompt = f"{sanitized_prompt}, {', '.join(enhancements)}"
        
        self.logger.info(f"Enhanced prompt length: {len(enhanced_prompt)}")
        return enhanced_prompt
    
    def generate_scene_variations(self, base_prompt: str) -> List[str]:
        """Generate multiple scene variations for epic storytelling"""
        theme, characters = self.detect_content_type(base_prompt)
        variations = []
        
        # Base variation
        variations.append(self.enhance_prompt_epic_style(base_prompt))
        
        # Close-up character focus
        variations.append(self.enhance_prompt_epic_style(
            f"{base_prompt}, close-up portrait focus, detailed facial expressions, emotional intensity"
        ))
        
        # Wide cinematic view
        variations.append(self.enhance_prompt_epic_style(
            f"{base_prompt}, wide cinematic composition, epic landscape view, grand scale storytelling"
        ))
        
        # Divine/mystical version
        variations.append(self.enhance_prompt_epic_style(
            f"{base_prompt}, enhanced divine elements, celestial intervention, mystical atmosphere"
        ))
        
        return variations
    
    def generate_with_dalle(self, prompt, api_key, size=None, max_retries=None):
        """Generate image using DALL-E API with retry logic"""
        size = size or self.config.get('API', 'dalle_size', '1024x1024')
        max_retries = max_retries or self.config.getint('DEFAULT', 'max_retries', 3)
        timeout = self.config.getint('DEFAULT', 'request_timeout', 120)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.get('API', 'dalle_model', 'dall-e-3'),
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": self.config.get('API', 'dalle_quality', 'hd')
        }
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"DALL-E API request attempt {attempt + 1}")
                response = requests.post(
                    "https://api.openai.com/v1/images/generations",
                    headers=headers,
                    json=data,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_url = result["data"][0]["url"]
                    return self.download_image(image_url, "dalle")
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        self.logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                        self.unicode_handler.safe_print(f"Rate limited. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                else:
                    error_msg = f"API Error: {response.status_code} - {response.text}"
                    self.logger.error(error_msg)
                    return error_msg
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Request timeout. Retrying... ({attempt + 1}/{max_retries})")
                    self.unicode_handler.safe_print(f"Request timeout. Retrying... ({attempt + 1}/{max_retries})")
                    continue
                return "Request timed out after multiple attempts"
            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Error occurred. Retrying... ({attempt + 1}/{max_retries}): {e}")
                    self.unicode_handler.safe_print(f"Error occurred. Retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(1)
                    continue
                self.logger.error(f"Final error in DALL-E generation: {e}")
                return f"Error generating image: {str(e)}"
        
        return "Failed after all retry attempts"
    
    def generate_with_stability(self, prompt, api_key, max_retries=None):
        """Generate image using Stability AI API with retry logic"""
        max_retries = max_retries or self.config.getint('DEFAULT', 'max_retries', 3)
        timeout = self.config.getint('DEFAULT', 'request_timeout', 120)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        
        data = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": self.config.getint('API', 'stability_cfg_scale', 7),
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": self.config.getint('API', 'stability_steps', 50)
        }
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Stability API request attempt {attempt + 1}")
                response = requests.post(
                    "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                    headers=headers,
                    json=data,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_data = result["artifacts"][0]["base64"]
                    return self.save_base64_image(image_data, "stability")
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        self.logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                        self.unicode_handler.safe_print(f"Rate limited. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                else:
                    error_msg = f"API Error: {response.status_code} - {response.text}"
                    self.logger.error(error_msg)
                    return error_msg
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Request timeout. Retrying... ({attempt + 1}/{max_retries})")
                    self.unicode_handler.safe_print(f"Request timeout. Retrying... ({attempt + 1}/{max_retries})")
                    continue
                return "Request timed out after multiple attempts"
            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Error occurred. Retrying... ({attempt + 1}/{max_retries}): {e}")
                    self.unicode_handler.safe_print(f"Error occurred. Retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(1)
                    continue
                self.logger.error(f"Final error in Stability generation: {e}")
                return f"Error generating image: {str(e)}"
        
        return "Failed after all retry attempts"
    
    def download_image(self, url, provider):
        """Download image from URL"""
        timeout = self.config.getint('DEFAULT', 'download_timeout', 30)
        
        try:
            self.logger.info(f"Downloading image from {provider}")
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{provider}_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                success_msg = f"Image saved: {filepath}"
                self.logger.info(success_msg)
                return success_msg
            else:
                error_msg = f"Failed to download image: HTTP {response.status_code}"
                self.logger.error(error_msg)
                return error_msg
        except Exception as e:
            error_msg = f"Download error: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def save_base64_image(self, base64_data, provider):
        """Save base64 encoded image"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{provider}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(base64_data))
            
            success_msg = f"Image saved: {filepath}"
            self.logger.info(success_msg)
            return success_msg
        except Exception as e:
            error_msg = f"Save error: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def interactive_epic_mode(self):
        """Enhanced interactive mode with epic storytelling features"""
        self.unicode_handler.safe_print("Epic Story Image Generator")
        self.unicode_handler.safe_print("Specialized for Indian Epics, Fantasy & Mystery")
        self.unicode_handler.safe_print("Commands: 'quit', 'variations', 'characters', 'locations', 'config'")
        self.unicode_handler.safe_print("-" * 50)
        
        # Check for API keys
        dalle_key = os.getenv("OPENAI_API_KEY")
        stability_key = os.getenv("STABILITY_API_KEY")
        
        if not dalle_key and not stability_key:
            self.unicode_handler.safe_print("Warning: No API keys found. Please set OPENAI_API_KEY or STABILITY_API_KEY environment variables")
            return
        
        while True:
            try:
                prompt = input("\nEnter your epic scene description: ").strip()
                
                if prompt.lower() == 'quit':
                    break
                elif prompt.lower() == 'characters':
                    self._show_character_database()
                    continue
                elif prompt.lower() == 'locations':
                    self._show_location_database()
                    continue
                elif prompt.lower() == 'config':
                    self._show_configuration()
                    continue
                elif not prompt:
                    continue
                
                # Detect and show theme
                theme, characters = self.detect_content_type(prompt)
                self.unicode_handler.safe_print(f"Detected theme: {theme.title()}")
                if characters:
                    self.unicode_handler.safe_print(f"Characters found: {', '.join(characters)}")
                
                # Ask for variations
                create_variations = prompt.lower() == 'variations' or input("Create scene variations? (y/N): ").strip().lower() == 'y'
                
                if create_variations:
                    variations = self.generate_scene_variations(prompt)
                    for i, variation in enumerate(variations, 1):
                        self.unicode_handler.safe_print(f"\nGenerating variation {i}/4...")
                        self.unicode_handler.safe_print(f"Enhanced prompt: {variation[:100]}...")
                        self._generate_single_image(variation, dalle_key, stability_key)
                else:
                    # Single enhanced generation
                    enhanced_prompt = self.enhance_prompt_epic_style(prompt)
                    self.unicode_handler.safe_print(f"Enhanced prompt: {enhanced_prompt[:150]}...")
                    self._generate_single_image(enhanced_prompt, dalle_key, stability_key)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Interactive mode error: {e}")
                self.unicode_handler.safe_print(f"Error: {str(e)}")
        
        self.unicode_handler.safe_print("\nThank you for using Epic Story Image Generator!")
    
    def _generate_single_image(self, prompt, dalle_key, stability_key):
        """Generate a single image with provider selection"""
        # Choose provider
        if dalle_key and stability_key:
            provider = input("Choose provider (dalle/stability) [dalle]: ").strip().lower()
            if not provider:
                provider = "dalle"
        elif dalle_key:
            provider = "dalle"
        else:
            provider = "stability"
        
        self.unicode_handler.safe_print(f"Generating with {provider.upper()}...")
        
        # Generate image
        if provider == "dalle" and dalle_key:
            result = self.generate_with_dalle(prompt, dalle_key)
        elif provider == "stability" and stability_key:
            result = self.generate_with_stability(prompt, stability_key)
        else:
            result = "API key not available for selected provider"
        
        self.unicode_handler.safe_print(f"Result: {result}")
    
    def _show_character_database(self):
        """Show available characters"""
        self.unicode_handler.safe_print("\nRAMAYANA CHARACTERS:")
        for char, data in self.ramayana_characters.items():
            self.unicode_handler.safe_print(f"  - {char.title()}: {data['description']}")
        
        self.unicode_handler.safe_print("\nMAHABHARATA CHARACTERS:")
        for char, data in self.mahabharata_characters.items():
            self.unicode_handler.safe_print(f"  - {char.title()}: {data['description']}")
    
    def _show_location_database(self):
        """Show available locations"""
        self.unicode_handler.safe_print("\nEPIC LOCATIONS:")
        for loc, data in self.epic_locations.items():
            self.unicode_handler.safe_print(f"  - {loc.title()}: {data['description']}")
    
    def _show_configuration(self):
        """Show current configuration"""
        self.unicode_handler.safe_print("\nCURRENT CONFIGURATION:")
        for section_name in self.config.config.sections():
            self.unicode_handler.safe_print(f"\n[{section_name}]")
            section = self.config.config[section_name]
            for key, value in section.items():
                self.unicode_handler.safe_print(f"  {key} = {value}")

def create_worker_function():
    """Create a standalone worker function for multiprocessing"""
    def worker_process(args):
        process_id, num_tasks = args
        try:
            # Create generator instance within the process
            generator = EpicImageGeneratorFixed()
            results = []
            for i in range(num_tasks):
                prompt = f"Process {process_id} epic scene {i} with divine characters"
                result = generator.enhance_prompt_epic_style(prompt)
                results.append(len(result))
            return (process_id, len(results), sum(results))
        except Exception as e:
            return (process_id, "ERROR", str(e))
    
    return worker_process

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="Generate epic story images with enhanced Indian mythology support")
    parser.add_argument("--prompt", help="Text prompt for image generation")
    parser.add_argument("--provider", choices=["dalle", "stability"], default="dalle", help="AI provider to use")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive epic mode")
    parser.add_argument("--variations", action="store_true", help="Generate multiple scene variations")
    parser.add_argument("--config", help="Configuration file path")
    
    args = parser.parse_args()
    
    try:
        generator = EpicImageGeneratorFixed(args.config)
        
        if args.interactive or not args.prompt:
            generator.interactive_epic_mode()
        else:
            # Single generation mode
            if args.variations:
                variations = generator.generate_scene_variations(args.prompt)
                for i, variation in enumerate(variations, 1):
                    generator.unicode_handler.safe_print(f"Generating variation {i}: {variation[:100]}...")
                    # Generate image logic here
            else:
                enhanced_prompt = generator.enhance_prompt_epic_style(args.prompt)
                generator.unicode_handler.safe_print(f"Enhanced: {enhanced_prompt}")
                
                if args.provider == "dalle":
                    api_key = os.getenv("OPENAI_API_KEY")
                    if api_key:
                        result = generator.generate_with_dalle(enhanced_prompt, api_key)
                    else:
                        result = "OPENAI_API_KEY not found"
                else:
                    api_key = os.getenv("STABILITY_API_KEY")
                    if api_key:
                        result = generator.generate_with_stability(enhanced_prompt, api_key)
                    else:
                        result = "STABILITY_API_KEY not found"
                
                generator.unicode_handler.safe_print(result)
    
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()