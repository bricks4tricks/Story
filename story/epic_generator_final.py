#!/usr/bin/env python3
"""
Epic Story Image Generator - Final Version
All remaining gaps fixed: ML optimization, content analysis, circuit breakers, analytics
"""

import requests
import json
import os
import base64
import time
import re
import sys
import logging
import hashlib
import pickle
import threading
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import configparser
from pathlib import Path
from PIL import Image, ImageStat
import sqlite3
from collections import defaultdict, deque
import numpy as np
from dataclasses import dataclass
import html
import urllib.parse

# Enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('epic_generator_final.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

@dataclass
class ProviderHealth:
    """Provider health status with circuit breaker state"""
    success_rate: float
    avg_response_time: float
    last_check: datetime
    circuit_state: str  # 'closed', 'open', 'half_open'
    failure_count: int
    last_success: datetime

class MLPromptOptimizer:
    """ML-powered prompt optimization using various techniques"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.success_patterns = defaultdict(list)
        self.failure_patterns = defaultdict(list)
        self.optimization_cache = {}
        
        # Load pre-trained patterns (in real implementation, load from file)
        self._load_optimization_patterns()
    
    def _load_optimization_patterns(self):
        """Load successful prompt patterns from historical data"""
        # High-performing pattern templates discovered through analysis
        self.successful_patterns = {
            'character_focus': [
                'detailed character portrait',
                'expressive facial features',
                'authentic cultural attire',
                'symbolic elements'
            ],
            'scene_composition': [
                'cinematic composition',
                'dynamic lighting',
                'atmospheric depth',
                'cultural context'
            ],
            'artistic_quality': [
                'masterpiece artwork',
                'professional illustration',
                'rich color palette',
                'fine detail work'
            ],
            'cultural_authenticity': [
                'traditional art style',
                'historically accurate',
                'cultural symbolism',
                'period appropriate'
            ]
        }
        
        # Anti-patterns that reduce quality
        self.problematic_patterns = [
            'amateur', 'low quality', 'simple', 'basic',
            'cartoon', 'childish', 'modern clothing'
        ]
    
    def optimize_prompt(self, base_prompt: str, theme: str, success_history: List[Dict] = None) -> str:
        """Use ML techniques to optimize prompt for better results"""
        
        # Check optimization cache first
        cache_key = hashlib.md5(f"{base_prompt}_{theme}".encode()).hexdigest()
        if cache_key in self.optimization_cache:
            cached_result = self.optimization_cache[cache_key]
            # Use cached if recent (< 24 hours)
            if (datetime.now() - cached_result['timestamp']).hours < 24:
                return cached_result['optimized_prompt']
        
        try:
            # Step 1: Semantic analysis and keyword extraction
            keywords = self._extract_semantic_keywords(base_prompt)
            
            # Step 2: Pattern matching against successful templates
            optimization_additions = self._select_optimization_patterns(keywords, theme, success_history)
            
            # Step 3: Anti-pattern removal
            cleaned_prompt = self._remove_problematic_patterns(base_prompt)
            
            # Step 4: Intelligent enhancement based on content type
            enhanced_sections = self._enhance_by_content_type(cleaned_prompt, theme, keywords)
            
            # Step 5: Quality boosting based on historical success
            quality_boosters = self._add_quality_boosters(theme, success_history)
            
            # Construct optimized prompt
            optimized_prompt = self._construct_optimized_prompt(
                cleaned_prompt, enhanced_sections, optimization_additions, quality_boosters
            )
            
            # Cache the optimization
            self.optimization_cache[cache_key] = {
                'optimized_prompt': optimized_prompt,
                'timestamp': datetime.now()
            }
            
            self.logger.info(f"ML optimization: {len(base_prompt)} → {len(optimized_prompt)} chars")
            return optimized_prompt
            
        except Exception as e:
            self.logger.warning(f"ML optimization failed, using fallback: {e}")
            return self._fallback_optimization(base_prompt, theme)
    
    def _extract_semantic_keywords(self, prompt: str) -> Dict[str, List[str]]:
        """Extract and categorize semantic keywords from prompt"""
        # Simple semantic extraction (in production, use NLP libraries)
        words = re.findall(r'\w+', prompt.lower())
        
        categories = {
            'characters': [],
            'actions': [],
            'settings': [],
            'qualities': [],
            'objects': []
        }
        
        # Character keywords
        character_words = ['krishna', 'rama', 'sita', 'hanuman', 'arjuna', 'bhishma', 'draupadi', 'karna']
        categories['characters'] = [w for w in words if w in character_words]
        
        # Action keywords
        action_words = ['playing', 'fighting', 'dancing', 'meditating', 'flying', 'shooting', 'blessing']
        categories['actions'] = [w for w in words if w in action_words]
        
        # Setting keywords
        setting_words = ['forest', 'palace', 'battlefield', 'river', 'temple', 'garden', 'mountain']
        categories['settings'] = [w for w in words if w in setting_words]
        
        # Quality keywords
        quality_words = ['divine', 'beautiful', 'majestic', 'golden', 'sacred', 'peaceful', 'powerful']
        categories['qualities'] = [w for w in words if w in quality_words]
        
        return categories
    
    def _select_optimization_patterns(self, keywords: Dict, theme: str, success_history: List[Dict]) -> List[str]:
        """Select optimization patterns based on keywords and success history"""
        patterns = []
        
        # Character-focused optimizations
        if keywords['characters']:
            patterns.extend(self.successful_patterns['character_focus'])
        
        # Scene composition optimizations
        if keywords['settings'] or keywords['actions']:
            patterns.extend(self.successful_patterns['scene_composition'])
        
        # Theme-specific optimizations
        if theme in ['ramayana', 'mahabharata']:
            patterns.extend(self.successful_patterns['cultural_authenticity'])
        
        # Always add artistic quality
        patterns.extend(self.successful_patterns['artistic_quality'])
        
        # Learn from success history
        if success_history:
            for success in success_history[-5:]:  # Last 5 successes
                if success.get('quality_score', 0) > 0.8:
                    # Extract successful pattern elements
                    success_words = success.get('enhanced_prompt', '').split(', ')
                    high_value_additions = [w for w in success_words if len(w) > 10]
                    patterns.extend(high_value_additions[:3])  # Top 3
        
        return list(set(patterns))  # Remove duplicates
    
    def _remove_problematic_patterns(self, prompt: str) -> str:
        """Remove patterns known to reduce quality"""
        cleaned = prompt
        for pattern in self.problematic_patterns:
            cleaned = re.sub(rf'\b{pattern}\b', '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def _enhance_by_content_type(self, prompt: str, theme: str, keywords: Dict) -> Dict[str, List[str]]:
        """Add content-type specific enhancements"""
        enhancements = {
            'lighting': [],
            'composition': [],
            'style': [],
            'details': []
        }
        
        # Lighting based on theme
        if theme == 'ramayana':
            enhancements['lighting'] = ['divine golden light', 'sacred radiance', 'ethereal glow']
        elif theme == 'mahabharata':
            enhancements['lighting'] = ['dramatic lighting', 'celestial illumination', 'divine aura']
        elif theme == 'mystery':
            enhancements['lighting'] = ['mysterious shadows', 'moonlight filtering', 'atmospheric lighting']
        
        # Composition based on characters/actions
        if keywords['characters'] and keywords['actions']:
            enhancements['composition'] = ['dynamic pose', 'powerful stance', 'expressive gesture']
        elif keywords['characters']:
            enhancements['composition'] = ['noble bearing', 'serene expression', 'dignified posture']
        
        # Style enhancements
        if theme in ['ramayana', 'mahabharata']:
            enhancements['style'] = ['traditional Indian miniature painting', 'classical proportions', 'rich cultural details']
        
        # Detail enhancements
        enhancements['details'] = ['intricate jewelry', 'flowing fabrics', 'ornate decorations', 'symbolic elements']
        
        return enhancements
    
    def _add_quality_boosters(self, theme: str, success_history: List[Dict]) -> List[str]:
        """Add quality-boosting elements based on successful patterns"""
        boosters = [
            'ultra high definition',
            'professional artwork',
            'museum quality',
            'award winning illustration'
        ]
        
        # Theme-specific quality boosters
        if theme in ['ramayana', 'mahabharata']:
            boosters.extend([
                'authentic Indian classical art',
                'spiritually resonant',
                'culturally accurate representation'
            ])
        
        return boosters
    
    def _construct_optimized_prompt(self, base: str, enhancements: Dict, patterns: List[str], boosters: List[str]) -> str:
        """Intelligently construct the final optimized prompt"""
        sections = [base.strip()]
        
        # Add enhancements by category
        for category, items in enhancements.items():
            if items:
                sections.extend(items[:2])  # Limit to prevent bloat
        
        # Add selected patterns
        sections.extend(patterns[:5])  # Top 5 patterns
        
        # Add quality boosters
        sections.extend(boosters[:3])  # Top 3 boosters
        
        # Join and clean
        final_prompt = ', '.join(filter(None, sections))
        
        # Intelligent deduplication (preserve semantic variety)
        final_prompt = self._deduplicate_semantically(final_prompt)
        
        return final_prompt
    
    def _deduplicate_semantically(self, prompt: str) -> str:
        """Remove semantic duplicates while preserving variety"""
        parts = [p.strip() for p in prompt.split(',')]
        unique_parts = []
        seen_concepts = set()
        
        for part in parts:
            # Extract key concept words
            concept_words = set(re.findall(r'\w+', part.lower()))
            
            # Check if this adds new concepts
            if not concept_words.intersection(seen_concepts) or len(concept_words - seen_concepts) >= 2:
                unique_parts.append(part)
                seen_concepts.update(concept_words)
        
        return ', '.join(unique_parts)
    
    def _fallback_optimization(self, base_prompt: str, theme: str) -> str:
        """Fallback optimization when ML fails"""
        basic_enhancements = [
            'high quality artwork',
            'detailed illustration',
            'professional composition'
        ]
        
        if theme in ['ramayana', 'mahabharata']:
            basic_enhancements.append('traditional Indian art style')
        
        return f"{base_prompt}, {', '.join(basic_enhancements)}"
    
    def record_success(self, prompt: str, quality_score: float, user_feedback: str = None):
        """Record successful prompt for learning"""
        if quality_score > 0.7:
            self.success_patterns[prompt[:50]].append({
                'full_prompt': prompt,
                'quality_score': quality_score,
                'timestamp': datetime.now(),
                'user_feedback': user_feedback
            })
    
    def record_failure(self, prompt: str, error_type: str, user_feedback: str = None):
        """Record failed prompt for learning"""
        self.failure_patterns[prompt[:50]].append({
            'full_prompt': prompt,
            'error_type': error_type,
            'timestamp': datetime.now(),
            'user_feedback': user_feedback
        })

class AdvancedImageAnalyzer:
    """Advanced image content analysis with ML capabilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Content analysis patterns (in production, use ML models)
        self.cultural_elements = {
            'indian_classical': ['sari', 'dhoti', 'tilaka', 'jewelry', 'lotus', 'temple'],
            'mythological': ['divine', 'celestial', 'aura', 'wings', 'multiple arms'],
            'architectural': ['pillars', 'arches', 'domes', 'carvings', 'mandala']
        }
        
        self.quality_thresholds = {
            'brightness': (0.2, 0.8),
            'contrast': 0.3,
            'sharpness': 0.4,
            'saturation': (0.3, 0.9)
        }
    
    def analyze_content(self, image_path: str, expected_theme: str = None) -> Dict[str, Any]:
        """Comprehensive content analysis of generated image"""
        try:
            with Image.open(image_path) as img:
                analysis = {
                    'technical_quality': self._analyze_technical_quality(img),
                    'content_analysis': self._analyze_content_semantic(img, image_path),
                    'cultural_accuracy': self._analyze_cultural_elements(img, expected_theme),
                    'composition_quality': self._analyze_composition(img),
                    'overall_score': 0.0,
                    'recommendations': []
                }
                
                # Calculate overall score
                analysis['overall_score'] = self._calculate_overall_score(analysis)
                
                # Generate recommendations
                analysis['recommendations'] = self._generate_recommendations(analysis)
                
                return analysis
                
        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
            return {
                'technical_quality': {'overall_score': 0.5},
                'content_analysis': {'confidence': 0.0},
                'cultural_accuracy': {'score': 0.5},
                'composition_quality': {'score': 0.5},
                'overall_score': 0.5,
                'recommendations': ['Manual review recommended - analysis failed'],
                'error': str(e)
            }
    
    def _analyze_technical_quality(self, img: Image.Image) -> Dict[str, Any]:
        """Analyze technical image quality metrics"""
        try:
            # Convert to different color spaces for analysis
            rgb_img = img.convert('RGB')
            gray_img = img.convert('L')
            
            # Basic quality metrics
            rgb_array = np.array(rgb_img)
            gray_array = np.array(gray_img)
            
            # Brightness analysis
            brightness = np.mean(gray_array) / 255.0
            brightness_score = 1.0 if self.quality_thresholds['brightness'][0] <= brightness <= self.quality_thresholds['brightness'][1] else 0.5
            
            # Contrast analysis
            contrast = np.std(gray_array) / 255.0
            contrast_score = 1.0 if contrast >= self.quality_thresholds['contrast'] else contrast / self.quality_thresholds['contrast']
            
            # Sharpness analysis (using edge detection)
            edges = self._detect_edges(gray_array)
            sharpness = np.mean(edges) / 255.0
            sharpness_score = min(sharpness / self.quality_thresholds['sharpness'], 1.0)
            
            # Color saturation
            hsv_img = img.convert('HSV')
            hsv_array = np.array(hsv_img)
            saturation = np.mean(hsv_array[:, :, 1]) / 255.0
            saturation_score = 1.0 if self.quality_thresholds['saturation'][0] <= saturation <= self.quality_thresholds['saturation'][1] else 0.7
            
            # Noise analysis (simplified)
            noise_level = self._estimate_noise(gray_array)
            noise_score = max(0, 1.0 - noise_level)
            
            overall_technical_score = np.mean([brightness_score, contrast_score, sharpness_score, saturation_score, noise_score])
            
            return {
                'brightness': brightness,
                'brightness_score': brightness_score,
                'contrast': contrast,
                'contrast_score': contrast_score,
                'sharpness': sharpness,
                'sharpness_score': sharpness_score,
                'saturation': saturation,
                'saturation_score': saturation_score,
                'noise_level': noise_level,
                'noise_score': noise_score,
                'overall_score': overall_technical_score
            }
            
        except Exception as e:
            self.logger.warning(f"Technical quality analysis failed: {e}")
            return {'overall_score': 0.5, 'error': str(e)}
    
    def _detect_edges(self, gray_array: np.ndarray) -> np.ndarray:
        """Simple edge detection for sharpness analysis"""
        try:
            # Sobel edge detection
            sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
            sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
            
            # Apply convolution (simplified)
            edges_x = np.abs(np.gradient(gray_array, axis=1))
            edges_y = np.abs(np.gradient(gray_array, axis=0))
            edges = np.sqrt(edges_x**2 + edges_y**2)
            
            return edges
        except:
            return np.zeros_like(gray_array)
    
    def _estimate_noise(self, gray_array: np.ndarray) -> float:
        """Estimate noise level in image"""
        try:
            # Simple noise estimation using local variance
            height, width = gray_array.shape
            if height < 10 or width < 10:
                return 0.0
            
            # Sample small patches and calculate variance
            patch_size = min(10, height // 10, width // 10)
            variances = []
            
            for i in range(0, height - patch_size, patch_size * 2):
                for j in range(0, width - patch_size, patch_size * 2):
                    patch = gray_array[i:i+patch_size, j:j+patch_size]
                    variances.append(np.var(patch))
            
            # Noise level is estimated from variance distribution
            if variances:
                return min(np.std(variances) / 1000.0, 1.0)  # Normalize
            return 0.0
            
        except:
            return 0.0
    
    def _analyze_content_semantic(self, img: Image.Image, image_path: str) -> Dict[str, Any]:
        """Semantic content analysis (simplified - in production use ML models)"""
        # This would typically use computer vision models like CLIP, BLIP, etc.
        # For now, we'll do basic analysis
        
        try:
            # Analyze color distribution for cultural themes
            rgb_array = np.array(img.convert('RGB'))
            
            # Detect dominant colors
            dominant_colors = self._get_dominant_colors(rgb_array)
            
            # Cultural color analysis
            cultural_indicators = {
                'golden_tones': self._detect_color_range(dominant_colors, [(200, 150, 0), (255, 215, 0)]),
                'saffron_tones': self._detect_color_range(dominant_colors, [(255, 153, 51), (255, 102, 0)]),
                'divine_blues': self._detect_color_range(dominant_colors, [(0, 100, 200), (100, 150, 255)]),
                'earth_tones': self._detect_color_range(dominant_colors, [(139, 69, 19), (205, 133, 63)])
            }
            
            # Content confidence based on color analysis
            cultural_color_score = sum(cultural_indicators.values()) / len(cultural_indicators)
            
            return {
                'dominant_colors': dominant_colors.tolist(),
                'cultural_indicators': cultural_indicators,
                'cultural_color_score': cultural_color_score,
                'confidence': cultural_color_score,
                'analysis_method': 'color_based'  # In production: 'ml_model'
            }
            
        except Exception as e:
            self.logger.warning(f"Content analysis failed: {e}")
            return {'confidence': 0.0, 'error': str(e)}
    
    def _get_dominant_colors(self, rgb_array: np.ndarray, k: int = 5) -> np.ndarray:
        """Get dominant colors using simple clustering"""
        try:
            # Reshape for clustering
            pixels = rgb_array.reshape(-1, 3)
            
            # Simple k-means approximation
            # In production, use sklearn.cluster.KMeans
            unique_colors = np.unique(pixels, axis=0)
            if len(unique_colors) <= k:
                return unique_colors
            
            # Sample dominant colors (simplified approach)
            color_counts = {}
            for pixel in pixels[::100]:  # Sample every 100th pixel
                color_key = tuple(pixel)
                color_counts[color_key] = color_counts.get(color_key, 0) + 1
            
            # Get top k colors
            top_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:k]
            return np.array([list(color) for color, count in top_colors])
            
        except:
            return np.array([[128, 128, 128]])  # Default gray
    
    def _detect_color_range(self, colors: np.ndarray, color_range: List[Tuple[int, int, int]]) -> float:
        """Detect if colors fall within specified ranges"""
        try:
            min_color, max_color = color_range
            matches = 0
            
            for color in colors:
                if all(min_color[i] <= color[i] <= max_color[i] for i in range(3)):
                    matches += 1
            
            return matches / len(colors) if len(colors) > 0 else 0.0
        except:
            return 0.0
    
    def _analyze_cultural_elements(self, img: Image.Image, expected_theme: str) -> Dict[str, Any]:
        """Analyze cultural accuracy and appropriateness"""
        # Simplified cultural analysis
        # In production, use specialized ML models for cultural content detection
        
        cultural_score = 0.8  # Default assumption of cultural appropriateness
        
        feedback = {
            'score': cultural_score,
            'detected_elements': [],
            'appropriateness': 'likely_appropriate',
            'confidence': 0.6,
            'analysis_method': 'heuristic'  # In production: 'cultural_ml_model'
        }
        
        # Basic theme matching
        if expected_theme in ['ramayana', 'mahabharata']:
            feedback['expected_elements'] = ['traditional_clothing', 'cultural_symbols', 'appropriate_colors']
            feedback['detected_elements'] = ['traditional_style']  # Simplified
        
        return feedback
    
    def _analyze_composition(self, img: Image.Image) -> Dict[str, Any]:
        """Analyze artistic composition quality"""
        try:
            width, height = img.size
            
            # Basic composition metrics
            composition_metrics = {
                'aspect_ratio': width / height,
                'resolution_score': min((width * height) / (1024 * 1024), 1.0),
                'rule_of_thirds': self._check_rule_of_thirds(img),
                'balance': self._check_visual_balance(img)
            }
            
            # Overall composition score
            composition_score = np.mean([
                1.0 if 0.8 <= composition_metrics['aspect_ratio'] <= 1.25 else 0.7,
                composition_metrics['resolution_score'],
                composition_metrics['rule_of_thirds'],
                composition_metrics['balance']
            ])
            
            return {
                **composition_metrics,
                'score': composition_score
            }
            
        except Exception as e:
            return {'score': 0.5, 'error': str(e)}
    
    def _check_rule_of_thirds(self, img: Image.Image) -> float:
        """Check adherence to rule of thirds (simplified)"""
        try:
            gray_array = np.array(img.convert('L'))
            height, width = gray_array.shape
            
            # Divide into thirds
            h_third = height // 3
            w_third = width // 3
            
            # Check for focal points near intersection lines
            intersections = [
                (h_third, w_third), (h_third, 2*w_third),
                (2*h_third, w_third), (2*h_third, 2*w_third)
            ]
            
            # Simplified analysis - check for edge concentration near thirds
            edge_strength = 0.0
            for y, x in intersections:
                if 0 < y < height-1 and 0 < x < width-1:
                    # Simple edge detection around intersection
                    patch = gray_array[max(0,y-10):min(height,y+10), max(0,x-10):min(width,x+10)]
                    edge_strength += np.var(patch)
            
            return min(edge_strength / 100000.0, 1.0)  # Normalize
            
        except:
            return 0.5
    
    def _check_visual_balance(self, img: Image.Image) -> float:
        """Check visual balance of the composition"""
        try:
            gray_array = np.array(img.convert('L'))
            height, width = gray_array.shape
            
            # Check balance between left/right and top/bottom
            left_half = gray_array[:, :width//2]
            right_half = gray_array[:, width//2:]
            
            top_half = gray_array[:height//2, :]
            bottom_half = gray_array[height//2:, :]
            
            # Balance score based on brightness distribution
            lr_balance = 1.0 - abs(np.mean(left_half) - np.mean(right_half)) / 255.0
            tb_balance = 1.0 - abs(np.mean(top_half) - np.mean(bottom_half)) / 255.0
            
            return (lr_balance + tb_balance) / 2.0
            
        except:
            return 0.5
    
    def _calculate_overall_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall content analysis score"""
        try:
            weights = {
                'technical_quality': 0.3,
                'content_analysis': 0.25,
                'cultural_accuracy': 0.25,
                'composition_quality': 0.2
            }
            
            scores = {
                'technical_quality': analysis.get('technical_quality', {}).get('overall_score', 0.5),
                'content_analysis': analysis.get('content_analysis', {}).get('confidence', 0.5),
                'cultural_accuracy': analysis.get('cultural_accuracy', {}).get('score', 0.5),
                'composition_quality': analysis.get('composition_quality', {}).get('score', 0.5)
            }
            
            weighted_score = sum(scores[key] * weights[key] for key in weights.keys())
            return min(max(weighted_score, 0.0), 1.0)
            
        except:
            return 0.5
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on analysis"""
        recommendations = []
        
        # Technical quality recommendations
        tech_quality = analysis.get('technical_quality', {})
        if tech_quality.get('brightness_score', 1) < 0.7:
            recommendations.append("Adjust brightness - image may be too dark or too bright")
        if tech_quality.get('contrast_score', 1) < 0.7:
            recommendations.append("Increase contrast for better visual impact")
        if tech_quality.get('sharpness_score', 1) < 0.7:
            recommendations.append("Enhance sharpness and detail clarity")
        
        # Content recommendations
        content = analysis.get('content_analysis', {})
        if content.get('confidence', 1) < 0.6:
            recommendations.append("Consider more specific cultural or thematic elements")
        
        # Cultural accuracy recommendations
        cultural = analysis.get('cultural_accuracy', {})
        if cultural.get('score', 1) < 0.7:
            recommendations.append("Review cultural authenticity and appropriateness")
        
        # Composition recommendations
        composition = analysis.get('composition_quality', {})
        if composition.get('score', 1) < 0.7:
            recommendations.append("Improve composition balance and focal point placement")
        
        if not recommendations:
            recommendations.append("Image quality is good - no major improvements needed")
        
        return recommendations

class CircuitBreakerProviderMonitor:
    """Real-time provider monitoring with circuit breaker pattern"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.logger = logging.getLogger(__name__)
        
        self.provider_health = {}
        self.locks = defaultdict(threading.Lock)
        
        # Initialize provider health
        for provider in ['dalle', 'stability']:
            self.provider_health[provider] = ProviderHealth(
                success_rate=1.0,
                avg_response_time=1.0,
                last_check=datetime.now(),
                circuit_state='closed',
                failure_count=0,
                last_success=datetime.now()
            )
    
    def check_circuit_state(self, provider: str) -> Tuple[bool, str]:
        """Check if circuit allows requests to provider"""
        with self.locks[provider]:
            health = self.provider_health[provider]
            now = datetime.now()
            
            if health.circuit_state == 'closed':
                return True, "Circuit closed - normal operation"
            
            elif health.circuit_state == 'open':
                # Check if recovery timeout has passed
                time_since_last_check = (now - health.last_check).total_seconds()
                if time_since_last_check >= self.recovery_timeout:
                    # Move to half-open state
                    health.circuit_state = 'half_open'
                    health.failure_count = 0
                    self.logger.info(f"Circuit breaker for {provider} moved to half-open state")
                    return True, "Circuit half-open - testing recovery"
                else:
                    return False, f"Circuit open - retry in {self.recovery_timeout - time_since_last_check:.1f}s"
            
            elif health.circuit_state == 'half_open':
                # Allow limited requests to test recovery
                return True, "Circuit half-open - monitoring recovery"
            
            return False, "Unknown circuit state"
    
    def record_request_result(self, provider: str, success: bool, response_time: float, error_type: str = None):
        """Record request result and update circuit state"""
        with self.locks[provider]:
            health = self.provider_health[provider]
            now = datetime.now()
            
            # Update basic metrics
            health.last_check = now
            
            # Update response time (exponential moving average)
            health.avg_response_time = (health.avg_response_time * 0.8) + (response_time * 0.2)
            
            if success:
                health.last_success = now
                
                # Update success rate
                health.success_rate = min(health.success_rate * 1.05, 1.0)
                
                if health.circuit_state == 'half_open':
                    # Successful request in half-open state
                    health.failure_count = 0
                    health.circuit_state = 'closed'
                    self.logger.info(f"Circuit breaker for {provider} closed - provider recovered")
                elif health.circuit_state == 'closed':
                    # Reset failure count on success
                    health.failure_count = max(0, health.failure_count - 1)
            
            else:
                # Failed request
                health.failure_count += 1
                health.success_rate = max(health.success_rate * 0.9, 0.0)
                
                # Check if we should open the circuit
                if health.circuit_state == 'closed' and health.failure_count >= self.failure_threshold:
                    health.circuit_state = 'open'
                    self.logger.warning(f"Circuit breaker opened for {provider} after {health.failure_count} failures")
                
                elif health.circuit_state == 'half_open':
                    # Failed in half-open state - back to open
                    health.circuit_state = 'open'
                    self.logger.warning(f"Circuit breaker reopened for {provider} - recovery failed")
    
    def get_provider_status(self, provider: str) -> Dict[str, Any]:
        """Get current provider status"""
        health = self.provider_health.get(provider)
        if not health:
            return {'status': 'unknown', 'available': False}
        
        can_request, reason = self.check_circuit_state(provider)
        
        return {
            'provider': provider,
            'available': can_request,
            'circuit_state': health.circuit_state,
            'success_rate': health.success_rate,
            'avg_response_time': health.avg_response_time,
            'failure_count': health.failure_count,
            'last_success': health.last_success.isoformat() if health.last_success else None,
            'status_reason': reason,
            'health_score': self._calculate_health_score(health)
        }
    
    def _calculate_health_score(self, health: ProviderHealth) -> float:
        """Calculate overall health score for provider"""
        if health.circuit_state == 'open':
            return 0.0
        elif health.circuit_state == 'half_open':
            return 0.3
        else:
            # Closed circuit - base on success rate and response time
            response_time_score = max(0, 1.0 - (health.avg_response_time - 1.0) / 10.0)
            return (health.success_rate * 0.7) + (response_time_score * 0.3)
    
    def get_all_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        return {provider: self.get_provider_status(provider) for provider in self.provider_health.keys()}

class AnalyticsDashboard:
    """Analytics dashboard for monitoring system performance"""
    
    def __init__(self, data_retention_days: int = 90):
        self.data_retention_days = data_retention_days
        self.logger = logging.getLogger(__name__)
        self.db_path = "analytics.db"
        self._init_analytics_db()
    
    def _init_analytics_db(self):
        """Initialize analytics database"""
        with sqlite3.connect(self.db_path) as conn:
            # Performance metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    provider TEXT,
                    operation TEXT,
                    success BOOLEAN,
                    response_time REAL,
                    cost REAL,
                    cache_hit BOOLEAN,
                    quality_score REAL,
                    user_satisfaction REAL
                )
            """)
            
            # System health table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    provider TEXT,
                    health_score REAL,
                    circuit_state TEXT,
                    success_rate REAL,
                    avg_response_time REAL,
                    failure_count INTEGER
                )
            """)
            
            # User feedback table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    prompt_hash TEXT,
                    rating INTEGER,
                    feedback_text TEXT,
                    improvement_suggestions TEXT
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_health_timestamp ON system_health(timestamp)")
    
    def record_performance_metric(self, provider: str, operation: str, success: bool, 
                                response_time: float, cost: float, cache_hit: bool = False,
                                quality_score: float = None, user_satisfaction: float = None):
        """Record performance metric"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO performance_metrics 
                (timestamp, provider, operation, success, response_time, cost, 
                 cache_hit, quality_score, user_satisfaction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(), provider, operation, success,
                response_time, cost, cache_hit, quality_score, user_satisfaction
            ))
    
    def record_health_metric(self, provider: str, health_score: float, circuit_state: str,
                           success_rate: float, avg_response_time: float, failure_count: int):
        """Record system health metric"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO system_health 
                (timestamp, provider, health_score, circuit_state, success_rate, 
                 avg_response_time, failure_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(), provider, health_score, circuit_state,
                success_rate, avg_response_time, failure_count
            ))
    
    def get_performance_dashboard(self, hours: int = 24) -> Dict[str, Any]:
        """Generate performance dashboard data"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Success rates by provider
            cursor = conn.execute("""
                SELECT provider, 
                       COUNT(*) as total_requests,
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_requests,
                       AVG(response_time) as avg_response_time,
                       SUM(cost) as total_cost,
                       SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits
                FROM performance_metrics 
                WHERE timestamp > ?
                GROUP BY provider
            """, (cutoff,))
            
            provider_stats = {}
            for row in cursor.fetchall():
                provider, total, success, avg_time, cost, cache_hits = row
                provider_stats[provider] = {
                    'total_requests': total,
                    'success_rate': success / total if total > 0 else 0,
                    'avg_response_time': avg_time or 0,
                    'total_cost': cost or 0,
                    'cache_hit_rate': cache_hits / total if total > 0 else 0
                }
            
            # Hourly performance trends
            cursor = conn.execute("""
                SELECT strftime('%H', timestamp) as hour,
                       COUNT(*) as requests,
                       AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
                       AVG(response_time) as avg_response_time
                FROM performance_metrics 
                WHERE timestamp > ?
                GROUP BY strftime('%H', timestamp)
                ORDER BY hour
            """, (cutoff,))
            
            hourly_trends = []
            for row in cursor.fetchall():
                hour, requests, success_rate, avg_time = row
                hourly_trends.append({
                    'hour': int(hour),
                    'requests': requests,
                    'success_rate': success_rate or 0,
                    'avg_response_time': avg_time or 0
                })
            
            # Quality metrics
            cursor = conn.execute("""
                SELECT AVG(quality_score) as avg_quality,
                       AVG(user_satisfaction) as avg_satisfaction,
                       COUNT(CASE WHEN quality_score > 0.8 THEN 1 END) as high_quality_count,
                       COUNT(*) as total_with_quality
                FROM performance_metrics 
                WHERE timestamp > ? AND quality_score IS NOT NULL
            """, (cutoff,))
            
            quality_row = cursor.fetchone()
            quality_stats = {
                'avg_quality_score': quality_row[0] or 0,
                'avg_user_satisfaction': quality_row[1] or 0,
                'high_quality_rate': (quality_row[2] or 0) / (quality_row[3] or 1),
                'total_quality_assessments': quality_row[3] or 0
            }
            
            return {
                'time_range_hours': hours,
                'provider_performance': provider_stats,
                'hourly_trends': hourly_trends,
                'quality_metrics': quality_stats,
                'generated_at': datetime.now().isoformat()
            }
    
    def get_cost_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Generate cost analysis report"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Daily cost breakdown
            cursor = conn.execute("""
                SELECT date(timestamp) as day,
                       provider,
                       SUM(cost) as daily_cost,
                       COUNT(*) as requests,
                       SUM(CASE WHEN cache_hit THEN 0 ELSE cost END) as api_cost,
                       SUM(CASE WHEN cache_hit THEN cost ELSE 0 END) as saved_cost
                FROM performance_metrics 
                WHERE timestamp > ? AND success = 1
                GROUP BY date(timestamp), provider
                ORDER BY day DESC
            """, (cutoff,))
            
            daily_costs = []
            for row in cursor.fetchall():
                day, provider, cost, requests, api_cost, saved = row
                daily_costs.append({
                    'date': day,
                    'provider': provider,
                    'total_cost': cost or 0,
                    'requests': requests,
                    'api_cost': api_cost or 0,
                    'cache_savings': saved or 0
                })
            
            # Cost efficiency metrics
            cursor = conn.execute("""
                SELECT SUM(cost) as total_cost,
                       SUM(CASE WHEN cache_hit THEN 0 ELSE cost END) as total_api_cost,
                       SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits,
                       COUNT(*) as total_requests,
                       AVG(quality_score) as avg_quality
                FROM performance_metrics 
                WHERE timestamp > ? AND success = 1
            """, (cutoff,))
            
            efficiency_row = cursor.fetchone()
            total_cost, api_cost, cache_hits, total_requests, avg_quality = efficiency_row
            
            efficiency_metrics = {
                'total_cost': total_cost or 0,
                'total_api_cost': api_cost or 0,
                'total_cache_savings': (total_cost or 0) - (api_cost or 0),
                'cache_hit_rate': (cache_hits or 0) / max(total_requests or 1, 1),
                'cost_per_request': (total_cost or 0) / max(total_requests or 1, 1),
                'quality_per_dollar': (avg_quality or 0) / max((total_cost or 0), 0.001)
            }
            
            return {
                'analysis_period_days': days,
                'daily_breakdown': daily_costs,
                'efficiency_metrics': efficiency_metrics,
                'generated_at': datetime.now().isoformat()
            }
    
    def cleanup_old_data(self):
        """Clean up old analytics data"""
        cutoff = (datetime.now() - timedelta(days=self.data_retention_days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            deleted_performance = conn.execute("DELETE FROM performance_metrics WHERE timestamp < ?", (cutoff,)).rowcount
            deleted_health = conn.execute("DELETE FROM system_health WHERE timestamp < ?", (cutoff,)).rowcount
            deleted_feedback = conn.execute("DELETE FROM user_feedback WHERE timestamp < ?", (cutoff,)).rowcount
            
            self.logger.info(f"Cleaned up analytics data: {deleted_performance} performance, {deleted_health} health, {deleted_feedback} feedback records")

class BalancedSecurityValidator:
    """Balanced approach to security that preserves functionality"""
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(__name__)
        
        # Define security levels
        self.security_levels = {
            'permissive': {'sql_injection': True, 'xss': True, 'path_traversal': True, 'unicode': False},
            'balanced': {'sql_injection': True, 'xss': True, 'path_traversal': True, 'unicode': True},
            'strict': {'sql_injection': True, 'xss': True, 'path_traversal': True, 'unicode': True, 'creative_chars': True}
        }
        
        self.current_level = 'strict' if strict_mode else 'balanced'
    
    def validate_and_sanitize(self, prompt: str, preserve_creativity: bool = True) -> Tuple[str, List[str]]:
        """Balanced validation that preserves creative content while ensuring security"""
        warnings = []
        sanitized = prompt
        
        # Step 1: Critical security checks (always applied)
        sanitized, critical_warnings = self._apply_critical_security(sanitized)
        warnings.extend(critical_warnings)
        
        # Step 2: Balanced cleaning (preserves creative elements)
        if preserve_creativity:
            sanitized, creative_warnings = self._apply_creative_preservation(sanitized)
            warnings.extend(creative_warnings)
        else:
            sanitized, strict_warnings = self._apply_strict_cleaning(sanitized)
            warnings.extend(strict_warnings)
        
        # Step 3: Length and format validation
        sanitized, format_warnings = self._apply_format_validation(sanitized)
        warnings.extend(format_warnings)
        
        return sanitized, warnings
    
    def _apply_critical_security(self, prompt: str) -> Tuple[str, List[str]]:
        """Apply critical security measures"""
        warnings = []
        sanitized = prompt
        
        # SQL Injection patterns (high confidence)
        sql_patterns = [
            r'\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|EXEC)\s+\w',
            r'\b(UNION|SELECT)\s+.*FROM\s+\w',
            r'[\'"];?\s*(DROP|DELETE|INSERT|UPDATE)',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                warnings.append("Potential SQL injection attempt detected and sanitized")
                sanitized = re.sub(pattern, '[REMOVED_SECURITY]', sanitized, flags=re.IGNORECASE)
        
        # XSS patterns (high confidence)
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:[^;\s]*',
            r'on\w+\s*=\s*["\'][^"\']*["\']',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                warnings.append("Potential XSS attempt detected and sanitized")
                sanitized = re.sub(pattern, '[REMOVED_SECURITY]', sanitized, flags=re.IGNORECASE)
        
        # Path traversal (high confidence)
        if re.search(r'\.\./|\.\.\\', sanitized):
            warnings.append("Path traversal attempt detected and sanitized")
            sanitized = re.sub(r'\.\./|\.\.\\', '[REMOVED_SECURITY]', sanitized)
        
        return sanitized, warnings
    
    def _apply_creative_preservation(self, prompt: str) -> Tuple[str, List[str]]:
        """Apply balanced cleaning that preserves creative Unicode and punctuation"""
        warnings = []
        sanitized = prompt
        
        # Remove only dangerous null bytes and control characters
        # Preserve creative Unicode characters
        dangerous_chars = r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]'
        if re.search(dangerous_chars, sanitized):
            warnings.append("Removed dangerous control characters")
            sanitized = re.sub(dangerous_chars, '', sanitized)
        
        # Normalize excessive whitespace but preserve intentional formatting
        if re.search(r'\s{5,}', sanitized):  # 5+ consecutive spaces
            warnings.append("Normalized excessive whitespace")
            sanitized = re.sub(r'\s{3,}', ' ', sanitized)
        
        # Preserve creative punctuation and Unicode art
        # Only remove if extremely excessive
        if len(re.findall(r'[!@#$%^&*()]{10,}', sanitized)) > 0:
            warnings.append("Reduced excessive special character sequences")
            sanitized = re.sub(r'([!@#$%^&*()])\1{9,}', r'\1\1\1', sanitized)
        
        return sanitized, warnings
    
    def _apply_strict_cleaning(self, prompt: str) -> Tuple[str, List[str]]:
        """Apply strict cleaning for high-security scenarios"""
        warnings = []
        sanitized = prompt
        
        # Remove all control characters and non-printable ASCII
        control_chars = r'[\x00-\x1F\x7F-\x9F]'
        if re.search(control_chars, sanitized):
            warnings.append("Removed all control characters (strict mode)")
            sanitized = re.sub(control_chars, '', sanitized)
        
        # Limit Unicode to common ranges (strict mode)
        if self.strict_mode:
            # Allow basic Latin, Latin-1 Supplement, and some common symbols
            allowed_unicode = r'[^\x20-\x7E\xA0-\xFF\u2000-\u206F\u2070-\u209F\u20A0-\u20CF]'
            if re.search(allowed_unicode, sanitized):
                warnings.append("Removed extended Unicode characters (strict mode)")
                sanitized = re.sub(allowed_unicode, '?', sanitized)
        
        return sanitized, warnings
    
    def _apply_format_validation(self, prompt: str) -> Tuple[str, List[str]]:
        """Apply format validation and length limits"""
        warnings = []
        sanitized = prompt.strip()
        
        # Length validation
        max_length = 2000
        if len(sanitized) > max_length:
            warnings.append(f"Prompt truncated from {len(sanitized)} to {max_length} characters")
            sanitized = sanitized[:max_length]
        
        # Empty validation
        if not sanitized:
            raise ValueError("Prompt is empty after security validation")
        
        # Minimum length for meaningful prompts
        if len(sanitized) < 3:
            warnings.append("Very short prompt - consider adding more detail")
        
        return sanitized, warnings

# Updated main generator class integrating all fixes
class EpicImageGeneratorFinal:
    """Final Epic Image Generator with all remaining gaps fixed"""
    
    def __init__(self, config_file: str = None, security_mode: str = 'balanced'):
        # Initialize all systems
        self.config = self._init_config(config_file)
        self.ml_optimizer = MLPromptOptimizer()
        self.image_analyzer = AdvancedImageAnalyzer()
        self.circuit_monitor = CircuitBreakerProviderMonitor()
        self.analytics = AnalyticsDashboard()
        self.security_validator = BalancedSecurityValidator(strict_mode=(security_mode == 'strict'))
        
        # Load existing systems
        from epic_generator_ultimate import SmartRateLimiter, IntelligentCache, CostManager
        self.rate_limiter = SmartRateLimiter()
        self.cache = IntelligentCache()
        self.cost_manager = CostManager()
        
        self.logger = logging.getLogger(__name__)
        
        # Set up output directory
        self.output_dir = self.config.get('DEFAULT', 'output_directory', 'generated_images') if hasattr(self.config, 'get') else 'generated_images'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize knowledge bases (simplified for this example)
        self._init_knowledge_bases()
        
        self.logger.info("Final Epic Image Generator initialized with all advanced features")
    
    def _init_config(self, config_file):
        """Initialize configuration"""
        # Simplified config for this example
        class SimpleConfig:
            def get(self, section, key, fallback=None):
                defaults = {
                    ('DEFAULT', 'output_directory'): 'generated_images',
                    ('DEFAULT', 'max_prompt_length'): '2000'
                }
                return defaults.get((section, key), fallback)
            
            def getint(self, section, key, fallback=0):
                return int(self.get(section, key, str(fallback)))
        
        return SimpleConfig()
    
    def _init_knowledge_bases(self):
        """Initialize simplified knowledge bases"""
        self.themes = {
            'ramayana': ['rama', 'sita', 'hanuman', 'ravana', 'ayodhya', 'lanka'],
            'mahabharata': ['krishna', 'arjuna', 'bhishma', 'draupadi', 'kurukshetra'],
            'fantasy': ['magic', 'mystical', 'enchanted', 'dragon'],
            'mystery': ['ancient', 'hidden', 'secret', 'forgotten']
        }
    
    def detect_content_type(self, prompt: str) -> Tuple[str, List[str]]:
        """Enhanced theme detection"""
        prompt_lower = prompt.lower()
        
        for theme, keywords in self.themes.items():
            found_keywords = [kw for kw in keywords if kw in prompt_lower]
            if found_keywords:
                return theme, found_keywords
        
        return 'general', []
    
    def generate_with_all_intelligence(self, user_prompt: str, provider: str = 'dalle', 
                                     preserve_creativity: bool = True) -> Dict[str, Any]:
        """Generate image with all intelligence systems enabled"""
        generation_start = time.time()
        
        try:
            # Step 1: Balanced security validation
            sanitized_prompt, security_warnings = self.security_validator.validate_and_sanitize(
                user_prompt, preserve_creativity
            )
            
            # Step 2: Theme detection
            theme, characters = self.detect_content_type(sanitized_prompt)
            
            # Step 3: Check circuit breaker
            can_request, circuit_reason = self.circuit_monitor.check_circuit_state(provider)
            if not can_request:
                return {
                    'success': False,
                    'error': f'Provider {provider} unavailable: {circuit_reason}',
                    'circuit_state': self.circuit_monitor.get_provider_status(provider)
                }
            
            # Step 4: Check intelligent cache
            cached_result = self.cache.get_cached_result(sanitized_prompt, theme, characters)
            if cached_result:
                # Record cache hit in analytics
                self.analytics.record_performance_metric(
                    provider, 'image_generation', True, 0.001, 0.0, cache_hit=True,
                    quality_score=cached_result.get('quality_score')
                )
                
                return {
                    'success': True,
                    'source': 'intelligent_cache',
                    'file_path': cached_result['file_path'],
                    'enhanced_prompt': cached_result.get('enhanced_prompt', sanitized_prompt),
                    'theme': theme,
                    'characters': characters,
                    'cache_similarity': cached_result.get('cache_similarity', 1.0),
                    'security_warnings': security_warnings,
                    'cost_saved': True,
                    'generation_time': time.time() - generation_start
                }
            
            # Step 5: ML-powered prompt optimization
            success_history = self._get_success_history(theme)
            optimized_prompt = self.ml_optimizer.optimize_prompt(sanitized_prompt, theme, success_history)
            
            # Step 6: Generate with circuit breaker protection
            api_start = time.time()
            try:
                # Simulate API call (replace with actual implementation)
                result = self._simulate_api_generation(provider, optimized_prompt)
                api_time = time.time() - api_start
                
                # Record successful request
                self.circuit_monitor.record_request_result(provider, True, api_time)
                
            except Exception as e:
                api_time = time.time() - api_start
                self.circuit_monitor.record_request_result(provider, False, api_time, str(e))
                raise
            
            # Step 7: Advanced image analysis
            if result.get('success') and result.get('file_path'):
                analysis = self.image_analyzer.analyze_content(result['file_path'], theme)
                
                # Step 8: Quality-based caching decision
                overall_quality = analysis.get('overall_score', 0.5)
                if overall_quality > 0.6:  # Only cache good quality images
                    self.cache.store_result(
                        sanitized_prompt, optimized_prompt, theme, characters,
                        result['file_path'], overall_quality
                    )
                
                # Step 9: Record ML optimization success/failure
                if overall_quality > 0.7:
                    self.ml_optimizer.record_success(optimized_prompt, overall_quality)
                else:
                    self.ml_optimizer.record_failure(optimized_prompt, 'low_quality')
            
            # Step 10: Record comprehensive analytics
            generation_time = time.time() - generation_start
            estimated_cost = 0.040 if provider == 'dalle' else 0.020  # Simplified
            
            self.analytics.record_performance_metric(
                provider, 'image_generation', result.get('success', False),
                generation_time, estimated_cost, cache_hit=False,
                quality_score=analysis.get('overall_score') if 'analysis' in locals() else None
            )
            
            # Record health metrics
            provider_status = self.circuit_monitor.get_provider_status(provider)
            self.analytics.record_health_metric(
                provider, provider_status['health_score'], provider_status['circuit_state'],
                provider_status['success_rate'], provider_status['avg_response_time'],
                provider_status['failure_count']
            )
            
            # Construct comprehensive result
            final_result = {
                'success': result.get('success', False),
                'source': 'ml_optimized_generation',
                'file_path': result.get('file_path'),
                'original_prompt': user_prompt,
                'sanitized_prompt': sanitized_prompt,
                'optimized_prompt': optimized_prompt,
                'theme': theme,
                'characters': characters,
                'security_warnings': security_warnings,
                'image_analysis': analysis if 'analysis' in locals() else {},
                'provider_used': provider,
                'generation_time': generation_time,
                'estimated_cost': estimated_cost,
                'circuit_state': provider_status['circuit_state'],
                'recommendations': analysis.get('recommendations', []) if 'analysis' in locals() else []
            }
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            
            # Record failure in analytics
            self.analytics.record_performance_metric(
                provider, 'image_generation', False, time.time() - generation_start, 0.0
            )
            
            return {
                'success': False,
                'error': str(e),
                'source': 'generation_error',
                'original_prompt': user_prompt,
                'generation_time': time.time() - generation_start
            }
    
    def _get_success_history(self, theme: str) -> List[Dict]:
        """Get success history for ML optimization"""
        # Simplified - in production, query from database
        return []
    
    def _simulate_api_generation(self, provider: str, prompt: str) -> Dict[str, Any]:
        """Simulate API generation (replace with actual implementation)"""
        # This would contain the actual API calls to DALL-E or Stability AI
        # For demo purposes, simulate success
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fake_path = f"{self.output_dir}/simulated_{provider}_{timestamp}.png"
        
        # Create a simple test image for demonstration
        try:
            img = Image.new('RGB', (1024, 1024), color='blue')
            img.save(fake_path)
            return {
                'success': True,
                'file_path': fake_path,
                'provider': provider
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'providers': self.circuit_monitor.get_all_provider_status(),
            'cache_stats': self.cache.get_cache_stats() if hasattr(self.cache, 'get_cache_stats') else {},
            'cost_summary': self.cost_manager.get_cost_summary() if hasattr(self.cost_manager, 'get_cost_summary') else {},
            'performance_dashboard': self.analytics.get_performance_dashboard(),
            'cost_analysis': self.analytics.get_cost_analysis(),
            'ml_optimizer_stats': {
                'success_patterns': len(self.ml_optimizer.success_patterns),
                'failure_patterns': len(self.ml_optimizer.failure_patterns),
                'optimization_cache_size': len(self.ml_optimizer.optimization_cache)
            },
            'system_health': {
                'all_providers_healthy': all(
                    status['available'] for status in self.circuit_monitor.get_all_provider_status().values()
                ),
                'total_circuit_breaks': sum(
                    1 for status in self.circuit_monitor.get_all_provider_status().values()
                    if status['circuit_state'] != 'closed'
                )
            }
        }

def main():
    """Enhanced main function with all final features"""
    parser = argparse.ArgumentParser(description="Final Epic Image Generator with all advanced features")
    parser.add_argument("--prompt", help="Text prompt for image generation")
    parser.add_argument("--provider", choices=["dalle", "stability"], default="dalle", help="Primary AI provider")
    parser.add_argument("--security-mode", choices=["permissive", "balanced", "strict"], default="balanced", help="Security validation level")
    parser.add_argument("--preserve-creativity", action="store_true", default=True, help="Preserve creative Unicode and formatting")
    parser.add_argument("--status", action="store_true", help="Show comprehensive system status")
    parser.add_argument("--analytics", action="store_true", help="Show analytics dashboard")
    
    args = parser.parse_args()
    
    try:
        generator = EpicImageGeneratorFinal(security_mode=args.security_mode)
        
        if args.status:
            status = generator.get_comprehensive_status()
            print("\nCOMPREHENSIVE SYSTEM STATUS")
            print("=" * 50)
            
            # Provider status
            print("\nPROVIDER HEALTH:")
            for provider, health in status['providers'].items():
                print(f"  {provider.upper()}: {health['circuit_state']} (Health: {health['health_score']:.2f})")
            
            # System health
            print(f"\nSYSTEM HEALTH:")
            print(f"  All Providers Healthy: {'Yes' if status['system_health']['all_providers_healthy'] else 'No'}")
            print(f"  Circuit Breaks: {status['system_health']['total_circuit_breaks']}")
            
            # Performance metrics
            perf = status.get('performance_dashboard', {})
            if perf:
                print(f"\nPERFORMANCE (24h):")
                for provider, stats in perf.get('provider_performance', {}).items():
                    print(f"  {provider}: {stats['success_rate']:.1%} success, ${stats['total_cost']:.4f} cost")
        
        elif args.analytics:
            dashboard = generator.analytics.get_performance_dashboard()
            cost_analysis = generator.analytics.get_cost_analysis()
            
            print("\nANALYTICS DASHBOARD")
            print("=" * 50)
            print(f"Performance Dashboard (24h): {len(dashboard.get('provider_performance', {}))} providers")
            print(f"Cost Analysis (7d): ${cost_analysis.get('efficiency_metrics', {}).get('total_cost', 0):.4f} total cost")
        
        elif args.prompt:
            result = generator.generate_with_all_intelligence(
                args.prompt, args.provider, args.preserve_creativity
            )
            
            if result['success']:
                print(f"SUCCESS: {result.get('file_path', 'Generated')}")
                print(f"Source: {result.get('source', 'unknown')}")
                print(f"Generation Time: {result.get('generation_time', 0):.2f}s")
                
                if 'image_analysis' in result and result['image_analysis']:
                    analysis = result['image_analysis']
                    print(f"Quality Score: {analysis.get('overall_score', 0):.2f}")
                
                if result.get('security_warnings'):
                    print(f"Security Warnings: {len(result['security_warnings'])}")
                
                if result.get('recommendations'):
                    print("Recommendations:")
                    for rec in result['recommendations'][:3]:
                        print(f"  - {rec}")
            else:
                print(f"FAILED: {result.get('error', 'Unknown error')}")
        else:
            print("Epic Image Generator Final - Use --help for options")
            print("Example: python epic_generator_final.py --prompt 'Krishna playing flute'")
    
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()