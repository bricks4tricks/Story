#!/usr/bin/env python3
"""
AI Image Generator Script
Generates images based on user text prompts using various AI APIs
"""

import requests
import json
import os
import base64
import time
from datetime import datetime
import argparse

class ImageGenerator:
    def __init__(self):
        self.output_dir = "generated_images"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def enhance_prompt(self, user_prompt):
        """Enhance user prompt with artistic details"""
        # Validate prompt length
        if len(user_prompt) > 1000:
            user_prompt = user_prompt[:1000]
            print("⚠️  Prompt truncated to 1000 characters")
        
        if not user_prompt.strip():
            raise ValueError("Prompt cannot be empty")
        enhancements = [
            "high quality, detailed, 4K resolution",
            "beautiful lighting, professional composition",
            "vibrant colors, artistic masterpiece"
        ]
        
        # Add style suggestions based on content
        if any(word in user_prompt.lower() for word in ["krishna", "rama", "hindu", "indian", "mythology"]):
            enhancements.append("traditional Indian art style")
        elif "landscape" in user_prompt.lower():
            enhancements.append("scenic landscape photography style")
        elif "portrait" in user_prompt.lower():
            enhancements.append("professional portrait style")
        
        enhanced = f"{user_prompt}, {', '.join(enhancements)}"
        return enhanced
    
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
                elif response.status_code == 429:  # Rate limit
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
                elif response.status_code == 429:  # Rate limit
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
    
    def interactive_mode(self):
        """Interactive prompt mode"""
        print("🎨 AI Image Generator")
        print("Type 'quit' to exit\n")
        
        # Check for API keys
        dalle_key = os.getenv("OPENAI_API_KEY")
        stability_key = os.getenv("STABILITY_API_KEY")
        
        if not dalle_key and not stability_key:
            print("⚠️  No API keys found. Please set OPENAI_API_KEY or STABILITY_API_KEY environment variables")
            return
        
        while True:
            try:
                prompt = input("Enter your image description: ").strip()
                
                if prompt.lower() == 'quit':
                    break
                
                if not prompt:
                    continue
                
                # Enhance the prompt
                enhanced_prompt = self.enhance_prompt(prompt)
                print(f"Enhanced prompt: {enhanced_prompt}")
                
                # Choose provider
                if dalle_key and stability_key:
                    provider = input("Choose provider (dalle/stability) [dalle]: ").strip().lower()
                    if not provider:
                        provider = "dalle"
                elif dalle_key:
                    provider = "dalle"
                else:
                    provider = "stability"
                
                print(f"Generating image with {provider.upper()}...")
                
                # Generate image
                if provider == "dalle" and dalle_key:
                    result = self.generate_with_dalle(enhanced_prompt, dalle_key)
                elif provider == "stability" and stability_key:
                    result = self.generate_with_stability(enhanced_prompt, stability_key)
                else:
                    result = "API key not available for selected provider"
                
                print(f"Result: {result}\n")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {str(e)}\n")
        
        print("Thanks for using AI Image Generator!")

def main():
    parser = argparse.ArgumentParser(description="Generate images from text prompts")
    parser.add_argument("--prompt", help="Text prompt for image generation")
    parser.add_argument("--provider", choices=["dalle", "stability"], default="dalle", help="AI provider to use")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    generator = ImageGenerator()
    
    if args.interactive or not args.prompt:
        generator.interactive_mode()
    else:
        # Single generation mode
        enhanced_prompt = generator.enhance_prompt(args.prompt)
        print(f"Generating: {enhanced_prompt}")
        
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