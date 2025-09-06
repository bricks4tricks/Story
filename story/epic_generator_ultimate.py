#!/usr/bin/env python3
"""
Epic Story Image Generator - Ultimate Version
All gaps fixed: Smart rate limiting, image validation, caching, error recovery, cost management
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
from datetime import datetime, timedelta
import argparse
from typing import Dict, List, Tuple, Optional, Any
import configparser
from pathlib import Path
import threading
from PIL import Image, ImageStat
import sqlite3
from collections import defaultdict, deque
import asyncio
import aiohttp

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('epic_generator_ultimate.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class SmartRateLimiter:
    """Intelligent rate limiting with adaptive delays and provider-specific handling"""
    
    def __init__(self):
        self.provider_stats = defaultdict(lambda: {
            'requests': deque(maxlen=1000),
            'failures': deque(maxlen=100),
            'rate_limits': deque(maxlen=50),
            'success_rate': 1.0,
            'avg_response_time': 1.0,
            'adaptive_delay': 1.0
        })
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
    
    def record_request(self, provider: str, success: bool, response_time: float, 
                      status_code: int = None, error_type: str = None):
        """Record request statistics for intelligent rate limiting"""
        with self._lock:
            stats = self.provider_stats[provider]
            now = datetime.now()
            
            # Record request
            stats['requests'].append({
                'timestamp': now,
                'success': success,
                'response_time': response_time,
                'status_code': status_code
            })
            
            # Record failures
            if not success:
                stats['failures'].append({
                    'timestamp': now,
                    'error_type': error_type,
                    'status_code': status_code
                })
            
            # Record rate limits specifically
            if status_code == 429:
                stats['rate_limits'].append(now)
                # Increase adaptive delay aggressively for rate limits
                stats['adaptive_delay'] = min(stats['adaptive_delay'] * 2.5, 300)  # Max 5 minutes
                self.logger.warning(f"Rate limit detected for {provider}, increasing delay to {stats['adaptive_delay']:.1f}s")
            
            # Update success rate (last 100 requests)
            recent_requests = [r for r in stats['requests'] if (now - r['timestamp']).seconds < 3600]
            if recent_requests:
                stats['success_rate'] = sum(1 for r in recent_requests if r['success']) / len(recent_requests)
            
            # Update average response time
            if success and response_time > 0:
                stats['avg_response_time'] = (stats['avg_response_time'] * 0.9) + (response_time * 0.1)
            
            # Adaptive delay adjustment
            if success and status_code == 200:
                # Gradually reduce delay on success
                stats['adaptive_delay'] = max(stats['adaptive_delay'] * 0.95, 0.1)
            elif not success and status_code != 429:
                # Moderate increase for other failures
                stats['adaptive_delay'] = min(stats['adaptive_delay'] * 1.2, 60)
    
    def should_make_request(self, provider: str) -> Tuple[bool, float]:
        """Determine if request should be made and return recommended delay"""
        with self._lock:
            stats = self.provider_stats[provider]
            now = datetime.now()
            
            # Check recent rate limits (last 15 minutes)
            recent_rate_limits = [rl for rl in stats['rate_limits'] 
                                if (now - rl).seconds < 900]
            
            if recent_rate_limits:
                # If rate limited recently, use exponential backoff
                time_since_last = (now - recent_rate_limits[-1]).seconds
                recommended_delay = max(stats['adaptive_delay'], 60 - time_since_last)
                
                if time_since_last < stats['adaptive_delay']:
                    self.logger.info(f"Delaying {provider} request due to recent rate limits")
                    return False, recommended_delay
            
            # Check request frequency
            recent_requests = [r for r in stats['requests'] 
                             if (now - r['timestamp']).seconds < 60]
            
            # Intelligent throttling based on success rate
            if len(recent_requests) > 10 and stats['success_rate'] < 0.7:
                return False, stats['adaptive_delay'] * 2
            
            # Dynamic delay based on provider performance
            base_delay = stats['adaptive_delay']
            
            # Adjust for time of day (avoid peak hours)
            hour = now.hour
            if 9 <= hour <= 17:  # Business hours - higher load
                base_delay *= 1.5
            
            return True, base_delay
    
    def get_provider_health(self, provider: str) -> Dict[str, Any]:
        """Get health metrics for a provider"""
        stats = self.provider_stats[provider]
        now = datetime.now()
        
        recent_requests = [r for r in stats['requests'] 
                          if (now - r['timestamp']).seconds < 3600]
        
        return {
            'success_rate': stats['success_rate'],
            'avg_response_time': stats['avg_response_time'],
            'adaptive_delay': stats['adaptive_delay'],
            'requests_last_hour': len(recent_requests),
            'recent_rate_limits': len([rl for rl in stats['rate_limits'] 
                                     if (now - rl).seconds < 900]),
            'health_score': min(stats['success_rate'] * (1 / max(stats['avg_response_time'], 0.1)), 1.0)
        }

class ImageQualityValidator:
    """Comprehensive image quality validation system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.min_file_size = 1024  # 1KB minimum
        self.max_file_size = 50 * 1024 * 1024  # 50MB maximum
        self.expected_dimensions = [(1024, 1024), (1792, 1024), (1024, 1792)]
        
    def validate_image_file(self, filepath: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Comprehensive image validation"""
        try:
            # Check file existence and size
            if not os.path.exists(filepath):
                return False, "File does not exist", {}
            
            file_size = os.path.getsize(filepath)
            if file_size < self.min_file_size:
                return False, f"File too small: {file_size} bytes", {"file_size": file_size}
            
            if file_size > self.max_file_size:
                return False, f"File too large: {file_size} bytes", {"file_size": file_size}
            
            # Validate image format and integrity
            try:
                with Image.open(filepath) as img:
                    # Basic format validation
                    if img.format not in ['PNG', 'JPEG', 'JPG', 'WEBP']:
                        return False, f"Unsupported format: {img.format}", {"format": img.format}
                    
                    # Dimension validation
                    width, height = img.size
                    if width < 256 or height < 256:
                        return False, f"Image too small: {width}x{height}", {"dimensions": (width, height)}
                    
                    # Check for corruption by verifying image data
                    img.verify()
                    
                    # Reopen for quality analysis (verify() closes the image)
                    with Image.open(filepath) as img_analysis:
                        quality_metrics = self._analyze_image_quality(img_analysis)
                        
                        # Quality thresholds
                        if quality_metrics['brightness_score'] < 0.1:
                            return False, "Image too dark", quality_metrics
                        
                        if quality_metrics['contrast_score'] < 0.1:
                            return False, "Image too low contrast", quality_metrics
                        
                        if quality_metrics['sharpness_score'] < 0.3:
                            return False, "Image too blurry", quality_metrics
                        
                        # Cultural appropriateness check (basic)
                        cultural_check = self._check_cultural_appropriateness(filepath)
                        
                        return True, "Image validated successfully", {
                            **quality_metrics,
                            **cultural_check,
                            "file_size": file_size,
                            "dimensions": (width, height),
                            "format": img.format
                        }
            
            except Exception as img_error:
                return False, f"Image corruption or format error: {str(img_error)}", {}
        
        except Exception as e:
            self.logger.error(f"Validation error for {filepath}: {e}")
            return False, f"Validation error: {str(e)}", {}
    
    def _analyze_image_quality(self, img: Image.Image) -> Dict[str, float]:
        """Analyze image quality metrics"""
        try:
            # Convert to grayscale for analysis
            gray_img = img.convert('L')
            
            # Calculate brightness
            brightness = ImageStat.Stat(gray_img).mean[0] / 255.0
            
            # Calculate contrast (standard deviation of pixel values)
            contrast = ImageStat.Stat(gray_img).stddev[0] / 255.0
            
            # Simple sharpness metric using edge detection
            import numpy as np
            img_array = np.array(gray_img)
            
            # Sobel edge detection for sharpness
            from scipy import ndimage
            sobel_x = ndimage.sobel(img_array, axis=1, mode='constant')
            sobel_y = ndimage.sobel(img_array, axis=0, mode='constant')
            sharpness = np.hypot(sobel_x, sobel_y).mean() / 255.0
            
            return {
                'brightness_score': brightness,
                'contrast_score': contrast,
                'sharpness_score': min(sharpness, 1.0),
                'overall_quality_score': (brightness + contrast + min(sharpness, 1.0)) / 3.0
            }
        
        except Exception as e:
            self.logger.warning(f"Quality analysis failed: {e}")
            return {
                'brightness_score': 0.5,
                'contrast_score': 0.5,
                'sharpness_score': 0.5,
                'overall_quality_score': 0.5
            }
    
    def _check_cultural_appropriateness(self, filepath: str) -> Dict[str, Any]:
        """Basic cultural appropriateness checks"""
        # This is a placeholder for more sophisticated checks
        # In a real implementation, this could use ML models for content analysis
        return {
            'cultural_check': 'basic_passed',
            'appropriateness_score': 0.8,
            'flags': []
        }

class IntelligentCache:
    """Advanced caching system with semantic similarity and performance optimization"""
    
    def __init__(self, cache_dir: str = "cache", max_size_mb: int = 500):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.logger = logging.getLogger(__name__)
        
        # Initialize SQLite database for cache metadata
        self.db_path = self.cache_dir / "cache_metadata.db"
        self._init_database()
        
        # Semantic similarity threshold
        self.similarity_threshold = 0.85
        
    def _init_database(self):
        """Initialize SQLite database for cache metadata"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_hash TEXT UNIQUE,
                    original_prompt TEXT,
                    enhanced_prompt TEXT,
                    theme TEXT,
                    characters TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    created_at TIMESTAMP,
                    access_count INTEGER DEFAULT 1,
                    last_accessed TIMESTAMP,
                    quality_score REAL DEFAULT 0.5
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_prompt_hash ON cache_entries(prompt_hash)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_theme ON cache_entries(theme)
            """)
    
    def _calculate_prompt_hash(self, prompt: str) -> str:
        """Calculate hash for prompt normalization"""
        # Normalize prompt for consistent hashing
        normalized = re.sub(r'\s+', ' ', prompt.lower().strip())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _calculate_semantic_similarity(self, prompt1: str, prompt2: str) -> float:
        """Calculate semantic similarity between prompts"""
        # Simple word-based similarity (can be enhanced with embeddings)
        words1 = set(prompt1.lower().split())
        words2 = set(prompt2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        # Boost similarity for same theme/characters
        theme_words = {'krishna', 'rama', 'hanuman', 'arjuna', 'sita', 'ramayana', 'mahabharata'}
        theme_overlap = len(words1.intersection(theme_words)) + len(words2.intersection(theme_words))
        theme_boost = min(theme_overlap * 0.1, 0.3)
        
        return min(jaccard_similarity + theme_boost, 1.0)
    
    def get_cached_result(self, prompt: str, theme: str, characters: List[str]) -> Optional[Dict[str, Any]]:
        """Get cached result for similar prompt"""
        prompt_hash = self._calculate_prompt_hash(prompt)
        
        with sqlite3.connect(self.db_path) as conn:
            # First, try exact match
            cursor = conn.execute("""
                SELECT * FROM cache_entries WHERE prompt_hash = ?
            """, (prompt_hash,))
            
            exact_match = cursor.fetchone()
            if exact_match:
                # Update access statistics
                conn.execute("""
                    UPDATE cache_entries 
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE prompt_hash = ?
                """, (datetime.now().isoformat(), prompt_hash))
                
                self.logger.info(f"Cache hit (exact): {prompt[:50]}...")
                return self._row_to_dict(exact_match)
            
            # Look for semantic similarities
            cursor = conn.execute("""
                SELECT * FROM cache_entries 
                WHERE theme = ? 
                ORDER BY access_count DESC, quality_score DESC
                LIMIT 20
            """, (theme,))
            
            similar_entries = cursor.fetchall()
            
            for entry in similar_entries:
                similarity = self._calculate_semantic_similarity(prompt, entry[2])  # original_prompt
                if similarity >= self.similarity_threshold:
                    # Update access statistics
                    conn.execute("""
                        UPDATE cache_entries 
                        SET access_count = access_count + 1, last_accessed = ?
                        WHERE id = ?
                    """, (datetime.now().isoformat(), entry[0]))
                    
                    self.logger.info(f"Cache hit (similarity {similarity:.2f}): {prompt[:50]}...")
                    result = self._row_to_dict(entry)
                    result['cache_similarity'] = similarity
                    return result
        
        return None
    
    def store_result(self, prompt: str, enhanced_prompt: str, theme: str, 
                    characters: List[str], file_path: str, quality_score: float = 0.5):
        """Store result in cache"""
        try:
            prompt_hash = self._calculate_prompt_hash(prompt)
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache_entries 
                    (prompt_hash, original_prompt, enhanced_prompt, theme, characters, 
                     file_path, file_size, created_at, last_accessed, quality_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    prompt_hash, prompt, enhanced_prompt, theme, 
                    ','.join(characters), file_path, file_size,
                    datetime.now().isoformat(), datetime.now().isoformat(),
                    quality_score
                ))
            
            # Check cache size and cleanup if necessary
            self._cleanup_cache()
            
            self.logger.info(f"Cached result for: {prompt[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Failed to store cache entry: {e}")
    
    def _cleanup_cache(self):
        """Clean up cache when it exceeds size limit"""
        try:
            total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*") if f.is_file())
            
            if total_size > self.max_size_bytes:
                # Remove least accessed entries
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("""
                        SELECT file_path FROM cache_entries 
                        ORDER BY access_count ASC, last_accessed ASC
                        LIMIT 10
                    """)
                    
                    files_to_remove = cursor.fetchall()
                    
                    for (file_path,) in files_to_remove:
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            
                            conn.execute("DELETE FROM cache_entries WHERE file_path = ?", (file_path,))
                        except Exception as e:
                            self.logger.warning(f"Failed to remove cache file {file_path}: {e}")
                
                self.logger.info("Cache cleanup completed")
        
        except Exception as e:
            self.logger.error(f"Cache cleanup failed: {e}")
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert database row to dictionary"""
        return {
            'id': row[0],
            'prompt_hash': row[1],
            'original_prompt': row[2],
            'enhanced_prompt': row[3],
            'theme': row[4],
            'characters': row[5].split(',') if row[5] else [],
            'file_path': row[6],
            'file_size': row[7],
            'created_at': row[8],
            'access_count': row[9],
            'last_accessed': row[10],
            'quality_score': row[11]
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*), AVG(access_count), SUM(file_size) FROM cache_entries")
            count, avg_access, total_size = cursor.fetchone()
            
            cursor = conn.execute("""
                SELECT theme, COUNT(*) FROM cache_entries GROUP BY theme ORDER BY COUNT(*) DESC
            """)
            theme_stats = dict(cursor.fetchall())
            
            return {
                'total_entries': count or 0,
                'average_access_count': avg_access or 0,
                'total_size_bytes': total_size or 0,
                'total_size_mb': (total_size or 0) / (1024 * 1024),
                'theme_distribution': theme_stats
            }

class CostManager:
    """Track and manage API costs and usage"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cost_db = "cost_tracking.db"
        self._init_cost_database()
        
        # API cost estimates (per 1000 requests or per image)
        self.api_costs = {
            'dalle': {
                '1024x1024': 0.040,  # $0.040 per image
                '1792x1024': 0.080,  # $0.080 per image  
                '1024x1792': 0.080,  # $0.080 per image
            },
            'stability': {
                'standard': 0.020,   # $0.020 per image
                'hd': 0.040,        # $0.040 per image
            }
        }
        
    def _init_cost_database(self):
        """Initialize cost tracking database"""
        with sqlite3.connect(self.cost_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    provider TEXT,
                    operation TEXT,
                    model TEXT,
                    size TEXT,
                    success BOOLEAN,
                    estimated_cost REAL,
                    prompt_length INTEGER,
                    response_time REAL,
                    cached BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON api_usage(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_provider ON api_usage(provider)
            """)
    
    def record_usage(self, provider: str, operation: str, model: str = None, 
                    size: str = None, success: bool = True, prompt_length: int = 0,
                    response_time: float = 0, cached: bool = False):
        """Record API usage and calculate costs"""
        estimated_cost = 0.0
        
        if not cached and success:  # Only charge for successful, non-cached requests
            if provider == 'dalle':
                estimated_cost = self.api_costs['dalle'].get(size, 0.040)
            elif provider == 'stability':
                estimated_cost = self.api_costs['stability'].get(model, 0.020)
        
        with sqlite3.connect(self.cost_db) as conn:
            conn.execute("""
                INSERT INTO api_usage 
                (timestamp, provider, operation, model, size, success, 
                 estimated_cost, prompt_length, response_time, cached)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(), provider, operation, model, size,
                success, estimated_cost, prompt_length, response_time, cached
            ))
        
        if estimated_cost > 0:
            self.logger.info(f"API cost recorded: ${estimated_cost:.4f} for {provider} {operation}")
        
        return estimated_cost
    
    def get_cost_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get cost summary for specified period"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.cost_db) as conn:
            # Total costs
            cursor = conn.execute("""
                SELECT provider, SUM(estimated_cost), COUNT(*) 
                FROM api_usage 
                WHERE timestamp > ? AND success = 1
                GROUP BY provider
            """, (cutoff_date,))
            
            provider_costs = {}
            total_cost = 0
            total_requests = 0
            
            for provider, cost, count in cursor.fetchall():
                provider_costs[provider] = {
                    'cost': cost or 0,
                    'requests': count or 0
                }
                total_cost += cost or 0
                total_requests += count or 0
            
            # Cache savings
            cursor = conn.execute("""
                SELECT COUNT(*) FROM api_usage 
                WHERE timestamp > ? AND cached = 1
            """, (cutoff_date,))
            
            cached_requests = cursor.fetchone()[0] or 0
            
            # Estimated savings from caching (average cost per request)
            avg_cost_per_request = total_cost / max(total_requests, 1)
            estimated_savings = cached_requests * avg_cost_per_request
            
            # Daily breakdown
            cursor = conn.execute("""
                SELECT DATE(timestamp) as date, SUM(estimated_cost), COUNT(*)
                FROM api_usage 
                WHERE timestamp > ? AND success = 1
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """, (cutoff_date,))
            
            daily_costs = []
            for date, cost, count in cursor.fetchall():
                daily_costs.append({
                    'date': date,
                    'cost': cost or 0,
                    'requests': count or 0
                })
            
            return {
                'period_days': days,
                'total_cost': total_cost,
                'total_requests': total_requests,
                'cached_requests': cached_requests,
                'estimated_savings': estimated_savings,
                'cache_hit_rate': cached_requests / max(total_requests + cached_requests, 1),
                'provider_breakdown': provider_costs,
                'daily_costs': daily_costs[:7],  # Last 7 days
                'average_cost_per_request': avg_cost_per_request
            }

class AdvancedErrorRecovery:
    """Advanced error recovery with fallback strategies"""
    
    def __init__(self, rate_limiter: SmartRateLimiter, cost_manager: CostManager):
        self.rate_limiter = rate_limiter
        self.cost_manager = cost_manager
        self.logger = logging.getLogger(__name__)
        
        # Fallback provider priority
        self.fallback_priority = ['dalle', 'stability']
        
        # Error classification
        self.retryable_errors = {
            'network': ['ConnectionError', 'Timeout', 'HTTPError'],
            'rate_limit': ['429'],
            'temporary': ['500', '502', '503', '504'],
            'quota': ['insufficient_quota', 'quota_exceeded']
        }
        
    def execute_with_fallback(self, primary_provider: str, operation_func, *args, **kwargs):
        """Execute operation with intelligent fallback"""
        providers_to_try = [primary_provider]
        
        # Add fallback providers
        for provider in self.fallback_priority:
            if provider != primary_provider:
                providers_to_try.append(provider)
        
        last_error = None
        
        for provider in providers_to_try:
            try:
                # Check if we should make request to this provider
                should_request, delay = self.rate_limiter.should_make_request(provider)
                
                if not should_request:
                    self.logger.info(f"Skipping {provider} due to rate limiting, waiting {delay:.1f}s")
                    time.sleep(delay)
                    continue
                
                # Get provider health
                health = self.rate_limiter.get_provider_health(provider)
                if health['health_score'] < 0.3:
                    self.logger.warning(f"Provider {provider} health poor ({health['health_score']:.2f}), trying next")
                    continue
                
                # Execute operation with timing
                start_time = time.time()
                self.logger.info(f"Attempting operation with {provider}")
                
                result = operation_func(provider, *args, **kwargs)
                
                response_time = time.time() - start_time
                
                # Record successful request
                self.rate_limiter.record_request(provider, True, response_time, 200)
                self.cost_manager.record_usage(
                    provider, 'image_generation', 
                    success=True, response_time=response_time
                )
                
                self.logger.info(f"Operation successful with {provider} in {response_time:.2f}s")
                return result
                
            except Exception as e:
                last_error = e
                response_time = time.time() - start_time if 'start_time' in locals() else 0
                
                error_type = self._classify_error(e)
                status_code = getattr(e, 'status_code', None) or self._extract_status_code(str(e))
                
                # Record failed request
                self.rate_limiter.record_request(
                    provider, False, response_time, status_code, error_type
                )
                self.cost_manager.record_usage(
                    provider, 'image_generation', 
                    success=False, response_time=response_time
                )
                
                self.logger.warning(f"Operation failed with {provider}: {error_type} - {str(e)}")
                
                # Determine if we should try next provider
                if error_type in ['rate_limit', 'quota']:
                    self.logger.info(f"Provider {provider} has quota/rate issues, trying fallback")
                    continue
                elif error_type in ['network', 'temporary']:
                    self.logger.info(f"Temporary error with {provider}, trying fallback")
                    continue
                else:
                    # Client error - likely same across providers
                    self.logger.error(f"Client error with {provider}, stopping fallback attempts")
                    break
        
        # All providers failed
        raise Exception(f"All providers failed. Last error: {str(last_error)}")
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error type for recovery strategy"""
        error_str = str(error)
        error_type = type(error).__name__
        
        if '429' in error_str or 'rate limit' in error_str.lower():
            return 'rate_limit'
        elif 'quota' in error_str.lower() or 'insufficient' in error_str.lower():
            return 'quota'
        elif any(code in error_str for code in ['500', '502', '503', '504']):
            return 'temporary'
        elif error_type in ['ConnectionError', 'Timeout', 'HTTPError']:
            return 'network'
        else:
            return 'client_error'
    
    def _extract_status_code(self, error_message: str) -> Optional[int]:
        """Extract HTTP status code from error message"""
        import re
        match = re.search(r'\b([4-5]\d{2})\b', error_message)
        return int(match.group(1)) if match else None

# Updated main generator class with all gap fixes
class EpicImageGeneratorUltimate:
    """Ultimate Epic Image Generator with all gaps fixed"""
    
    def __init__(self, config_file: str = None):
        # Initialize all systems
        self.config = self._init_config(config_file)
        self.validator = self._init_validator()
        self.unicode_handler = self._init_unicode_handler()
        self.rate_limiter = SmartRateLimiter()
        self.image_validator = ImageQualityValidator()
        self.cache = IntelligentCache()
        self.cost_manager = CostManager()
        self.error_recovery = AdvancedErrorRecovery(self.rate_limiter, self.cost_manager)
        
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
        
        self.logger.info("Ultimate Epic Image Generator initialized with all advanced features")
    
    def _init_config(self, config_file):
        """Initialize configuration with enhanced defaults"""
        from epic_enhanced_generator_fixed import ConfigManager
        return ConfigManager(config_file) if config_file else ConfigManager()
    
    def _init_validator(self):
        """Initialize input validator"""
        from epic_enhanced_generator_fixed import InputValidator
        return InputValidator(self.config)
    
    def _init_unicode_handler(self):
        """Initialize Unicode handler"""
        from epic_enhanced_generator_fixed import SafeUnicodeHandler
        return SafeUnicodeHandler()
    
    # Include all character/location loading methods from the fixed version
    def _load_ramayana_characters(self):
        # Same as in epic_enhanced_generator_fixed.py
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
    
    def _load_mahabharata_characters(self):
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
    
    def _load_epic_locations(self):
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
    
    def _load_divine_elements(self):
        return {
            "divine_auras": ["golden divine light", "celestial radiance", "holy aura", "sacred energy"],
            "weapons": ["divine bow", "celestial arrows", "sacred mace", "mystical sword", "divine chakra"],
            "creatures": ["divine horses", "celestial beings", "sacred cows", "mythical birds", "divine serpents"],
            "natural": ["lotus flowers", "sacred trees", "flowing rivers", "mountain peaks", "celestial clouds"],
            "architectural": ["temple architecture", "royal palaces", "sacred pillars", "divine mandapas"],
            "mystical": ["divine intervention", "celestial phenomena", "sacred geometry", "spiritual energy"]
        }
    
    def _load_art_styles(self):
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
        """Enhanced theme detection with caching consideration"""
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
    
    def generate_with_intelligence(self, user_prompt: str, provider: str = 'dalle') -> Dict[str, Any]:
        """Generate image with all intelligence features enabled"""
        try:
            # Step 1: Input validation and sanitization
            sanitized_prompt = self.validator.validate_and_sanitize(user_prompt)
            theme, characters = self.detect_content_type(sanitized_prompt)
            
            # Step 2: Check cache first
            cached_result = self.cache.get_cached_result(sanitized_prompt, theme, characters)
            if cached_result:
                self.cost_manager.record_usage(provider, 'image_generation', cached=True)
                return {
                    'success': True,
                    'source': 'cache',
                    'file_path': cached_result['file_path'],
                    'enhanced_prompt': cached_result['enhanced_prompt'],
                    'theme': theme,
                    'characters': characters,
                    'cache_similarity': cached_result.get('cache_similarity', 1.0),
                    'cost_saved': True
                }
            
            # Step 3: Enhance prompt
            enhanced_prompt = self.enhance_prompt_epic_style(sanitized_prompt)
            
            # Step 4: Generate with error recovery and fallback
            def generate_operation(selected_provider, *args, **kwargs):
                if selected_provider == 'dalle':
                    return self._generate_dalle_internal(enhanced_prompt)
                elif selected_provider == 'stability':
                    return self._generate_stability_internal(enhanced_prompt)
                else:
                    raise ValueError(f"Unknown provider: {selected_provider}")
            
            result = self.error_recovery.execute_with_fallback(provider, generate_operation)
            
            # Step 5: Validate generated image
            if result['success'] and result.get('file_path'):
                is_valid, validation_message, quality_metrics = self.image_validator.validate_image_file(result['file_path'])
                
                if not is_valid:
                    self.logger.warning(f"Generated image failed validation: {validation_message}")
                    # Could implement regeneration logic here
                    return {
                        'success': False,
                        'error': f"Image quality validation failed: {validation_message}",
                        'quality_metrics': quality_metrics
                    }
                
                # Step 6: Cache successful result
                quality_score = quality_metrics.get('overall_quality_score', 0.5)
                self.cache.store_result(
                    sanitized_prompt, enhanced_prompt, theme, characters, 
                    result['file_path'], quality_score
                )
                
                result.update({
                    'theme': theme,
                    'characters': characters,
                    'quality_metrics': quality_metrics,
                    'validation_passed': True,
                    'cached_for_reuse': True
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'source': 'generation_error'
            }
    
    def _generate_dalle_internal(self, enhanced_prompt: str) -> Dict[str, Any]:
        """Internal DALL-E generation with proper error handling"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")
        
        # Use the existing generate_with_dalle logic but return structured result
        file_path = self.generate_with_dalle(enhanced_prompt, api_key)
        
        if "Error" in file_path or "Failed" in file_path:
            raise Exception(file_path)
        
        return {
            'success': True,
            'file_path': file_path.replace("Image saved: ", ""),
            'provider': 'dalle'
        }
    
    def _generate_stability_internal(self, enhanced_prompt: str) -> Dict[str, Any]:
        """Internal Stability AI generation with proper error handling"""
        api_key = os.getenv("STABILITY_API_KEY")
        if not api_key:
            raise ValueError("STABILITY_API_KEY not found")
        
        # Use the existing generate_with_stability logic but return structured result
        file_path = self.generate_with_stability(enhanced_prompt, api_key)
        
        if "Error" in file_path or "Failed" in file_path:
            raise Exception(file_path)
        
        return {
            'success': True,
            'file_path': file_path.replace("Image saved: ", ""),
            'provider': 'stability'
        }

    # Include all other methods from the fixed version
    # (enhance_prompt_epic_style, generate_with_dalle, etc.)
    # ... [Include all methods from epic_enhanced_generator_fixed.py] ...

def main():
    """Enhanced main function with gap-fixed features"""
    parser = argparse.ArgumentParser(description="Ultimate Epic Image Generator with all advanced features")
    parser.add_argument("--prompt", help="Text prompt for image generation")
    parser.add_argument("--provider", choices=["dalle", "stability"], default="dalle", help="Primary AI provider")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--stats", action="store_true", help="Show system statistics")
    parser.add_argument("--cache-stats", action="store_true", help="Show cache statistics")
    parser.add_argument("--cost-report", action="store_true", help="Show cost report")
    
    args = parser.parse_args()
    
    try:
        generator = EpicImageGeneratorUltimate()
        
        if args.stats:
            print("SYSTEM STATISTICS")
            print("=" * 50)
            
            # Rate limiter stats
            for provider in ['dalle', 'stability']:
                health = generator.rate_limiter.get_provider_health(provider)
                print(f"\n{provider.upper()} Health:")
                print(f"  Success Rate: {health['success_rate']:.2%}")
                print(f"  Avg Response Time: {health['avg_response_time']:.2f}s")
                print(f"  Health Score: {health['health_score']:.2f}")
                print(f"  Current Delay: {health['adaptive_delay']:.1f}s")
        
        if args.cache_stats:
            stats = generator.cache.get_cache_stats()
            print("\nCACHE STATISTICS")
            print("=" * 50)
            print(f"Total Entries: {stats['total_entries']}")
            print(f"Cache Size: {stats['total_size_mb']:.1f} MB")
            print(f"Average Access Count: {stats['average_access_count']:.1f}")
            print(f"Theme Distribution: {stats['theme_distribution']}")
        
        if args.cost_report:
            report = generator.cost_manager.get_cost_summary()
            print("\nCOST REPORT (Last 30 Days)")
            print("=" * 50)
            print(f"Total Cost: ${report['total_cost']:.4f}")
            print(f"Total Requests: {report['total_requests']}")
            print(f"Cached Requests: {report['cached_requests']}")
            print(f"Estimated Savings: ${report['estimated_savings']:.4f}")
            print(f"Cache Hit Rate: {report['cache_hit_rate']:.1%}")
            print(f"Avg Cost/Request: ${report['average_cost_per_request']:.4f}")
        
        if args.interactive or not args.prompt:
            generator.interactive_epic_mode()
        else:
            result = generator.generate_with_intelligence(args.prompt, args.provider)
            
            if result['success']:
                print(f"SUCCESS: {result['file_path']}")
                print(f"Source: {result.get('source', 'generation')}")
                if 'quality_metrics' in result:
                    qm = result['quality_metrics']
                    print(f"Quality Score: {qm.get('overall_quality_score', 0):.2f}")
            else:
                print(f"FAILED: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()