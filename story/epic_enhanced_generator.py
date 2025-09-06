#!/usr/bin/env python3
"""
Epic Story Image Generator
Specialized for Indian Epics, Fantasy, and Mystery themes
Enhanced prompt generation for Ramayana, Mahabharata, and mythological scenes
"""

import requests
import json
import os
import base64
import time
import re
from datetime import datetime
import argparse
from typing import Dict, List, Tuple, Optional

class EpicImageGenerator:
    def __init__(self):
        self.output_dir = "generated_images"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize knowledge bases
        self.ramayana_characters = self._load_ramayana_characters()
        self.mahabharata_characters = self._load_mahabharata_characters()
        self.epic_locations = self._load_epic_locations()
        self.divine_elements = self._load_divine_elements()
        self.art_styles = self._load_art_styles()
        
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
        
        # Validate prompt length
        if len(user_prompt) > 1000:
            user_prompt = user_prompt[:1000]
            print("Warning: Prompt truncated to 1000 characters")
        
        if not user_prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # Detect content type
        theme, characters = self.detect_content_type(user_prompt)
        
        # Base enhancements
        enhancements = [
            "high quality, detailed, 4K resolution",
            "masterpiece artwork, professional composition"
        ]
        
        # Theme-specific enhancements
        if theme == "ramayana":
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
        
        elif theme == "mahabharata":
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
        for location, data in self.epic_locations.items():
            if location in user_prompt.lower():
                enhancements.append(data["description"])
                enhancements.extend(data["elements"])
        
        # Construct final prompt
        enhanced_prompt = f"{user_prompt}, {', '.join(enhancements)}"
        
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
    
    # [Previous API methods remain the same: generate_with_dalle, generate_with_stability, etc.]
    def generate_with_dalle(self, prompt, api_key, size="1024x1024", max_retries=3):
        """Generate image using DALL-E API with retry logic"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": "hd"
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://api.openai.com/v1/images/generations",
                    headers=headers,
                    json=data,
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_url = result["data"][0]["url"]
                    return self.download_image(image_url, "dalle")
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"Rate limited. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                else:
                    return f"Error: {response.status_code} - {response.text}"
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"Request timeout. Retrying... ({attempt + 1}/{max_retries})")
                    continue
                return "Request timed out after multiple attempts"
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Error occurred. Retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(1)
                    continue
                return f"Error generating image: {str(e)}"
        
        return "Failed after all retry attempts"
    
    def generate_with_stability(self, prompt, api_key, max_retries=3):
        """Generate image using Stability AI API with retry logic"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        
        data = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 50
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                    headers=headers,
                    json=data,
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_data = result["artifacts"][0]["base64"]
                    return self.save_base64_image(image_data, "stability")
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"Rate limited. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                else:
                    return f"Error: {response.status_code} - {response.text}"
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"Request timeout. Retrying... ({attempt + 1}/{max_retries})")
                    continue
                return "Request timed out after multiple attempts"
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Error occurred. Retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(1)
                    continue
                return f"Error generating image: {str(e)}"
        
        return "Failed after all retry attempts"
    
    def download_image(self, url, provider):
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{provider}_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                return f"Image saved: {filepath}"
            else:
                return "Failed to download image"
        except Exception as e:
            return f"Download error: {str(e)}"
    
    def save_base64_image(self, base64_data, provider):
        """Save base64 encoded image"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{provider}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(base64_data))
            
            return f"Image saved: {filepath}"
        except Exception as e:
            return f"Save error: {str(e)}"
    
    def interactive_epic_mode(self):
        """Enhanced interactive mode with epic storytelling features"""
        print("Epic Story Image Generator")
        print("Specialized for Indian Epics, Fantasy & Mystery")
        print("Commands: 'quit', 'variations', 'characters', 'locations'")
        print("-" * 50)
        
        # Check for API keys
        dalle_key = os.getenv("OPENAI_API_KEY")
        stability_key = os.getenv("STABILITY_API_KEY")
        
        if not dalle_key and not stability_key:
            print("Warning: No API keys found. Please set OPENAI_API_KEY or STABILITY_API_KEY environment variables")
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
                elif not prompt:
                    continue
                
                # Detect and show theme
                theme, characters = self.detect_content_type(prompt)
                print(f"Detected theme: {theme.title()}")
                if characters:
                    print(f"Characters found: {', '.join(characters)}")
                
                # Ask for variations
                create_variations = prompt.lower() == 'variations' or input("Create scene variations? (y/N): ").strip().lower() == 'y'
                
                if create_variations:
                    variations = self.generate_scene_variations(prompt)
                    for i, variation in enumerate(variations, 1):
                        print(f"\nGenerating variation {i}/4...")
                        print(f"Enhanced prompt: {variation[:100]}...")
                        self._generate_single_image(variation, dalle_key, stability_key)
                else:
                    # Single enhanced generation
                    enhanced_prompt = self.enhance_prompt_epic_style(prompt)
                    print(f"Enhanced prompt: {enhanced_prompt[:150]}...")
                    self._generate_single_image(enhanced_prompt, dalle_key, stability_key)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {str(e)}")
        
        print("\nThank you for using Epic Story Image Generator!")
    
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
        
        print(f"Generating with {provider.upper()}...")
        
        # Generate image
        if provider == "dalle" and dalle_key:
            result = self.generate_with_dalle(prompt, dalle_key)
        elif provider == "stability" and stability_key:
            result = self.generate_with_stability(prompt, stability_key)
        else:
            result = "API key not available for selected provider"
        
        print(f"Result: {result}")
    
    def _show_character_database(self):
        """Show available characters"""
        print("\nRAMAYANA CHARACTERS:")
        for char, data in self.ramayana_characters.items():
            print(f"  - {char.title()}: {data['description']}")
        
        print("\nMAHABHARATA CHARACTERS:")
        for char, data in self.mahabharata_characters.items():
            print(f"  - {char.title()}: {data['description']}")
    
    def _show_location_database(self):
        """Show available locations"""
        print("\nEPIC LOCATIONS:")
        for loc, data in self.epic_locations.items():
            print(f"  - {loc.title()}: {data['description']}")

def main():
    parser = argparse.ArgumentParser(description="Generate epic story images with enhanced Indian mythology support")
    parser.add_argument("--prompt", help="Text prompt for image generation")
    parser.add_argument("--provider", choices=["dalle", "stability"], default="dalle", help="AI provider to use")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive epic mode")
    parser.add_argument("--variations", action="store_true", help="Generate multiple scene variations")
    
    args = parser.parse_args()
    
    generator = EpicImageGenerator()
    
    if args.interactive or not args.prompt:
        generator.interactive_epic_mode()
    else:
        # Single generation mode
        if args.variations:
            variations = generator.generate_scene_variations(args.prompt)
            for i, variation in enumerate(variations, 1):
                print(f"Generating variation {i}: {variation[:100]}...")
                # Generate image logic here
        else:
            enhanced_prompt = generator.enhance_prompt_epic_style(args.prompt)
            print(f"Enhanced: {enhanced_prompt}")
            
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
            
            print(result)

if __name__ == "__main__":
    main()