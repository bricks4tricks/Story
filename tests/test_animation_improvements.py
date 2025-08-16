import pytest
from flask import Flask
from bs4 import BeautifulSoup
import os
import re

@pytest.fixture
def client():
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_animation_css_file_exists():
    """Test that animations CSS file exists"""
    css_path = 'static/css/animations.css'
    assert os.path.exists(css_path), f"Animations CSS file not found at {css_path}"
    
    # Check file is not empty
    file_size = os.path.getsize(css_path)
    assert file_size > 100, "Animations CSS file appears to be empty or too small"

def test_animation_keyframes_defined():
    """Test that all animation keyframes are properly defined"""
    css_path = 'static/css/animations.css'
    
    with open(css_path, 'r') as f:
        content = f.read()
        
        # Check for keyframe definitions
        keyframes = ['slideDown', 'fadeIn', 'slideUp', 'scaleIn', 'pulse', 'loading']
        for keyframe in keyframes:
            assert f'@keyframes {keyframe}' in content, f"Keyframe '{keyframe}' not defined"
        
        # Check keyframe content
        assert 'from {' in content or '0% {' in content, "Keyframe start states not defined"
        assert 'to {' in content or '100% {' in content, "Keyframe end states not defined"

def test_animation_classes_defined():
    """Test that animation classes are defined in CSS"""
    css_path = 'static/css/animations.css'
    
    with open(css_path, 'r') as f:
        content = f.read()
        
        # Check for animation classes
        animation_classes = ['.slide-down', '.fade-in', '.animate-on-scroll', 
                           '.hover-lift', '.button-press', '.pulse-glow', '.loading-skeleton']
        
        for anim_class in animation_classes:
            assert anim_class in content, f"Animation class '{anim_class}' not defined"

def test_hover_lift_animation_properties():
    """Test hover-lift animation has correct properties"""
    css_path = 'static/css/animations.css'
    
    with open(css_path, 'r') as f:
        content = f.read()
        
        # Check hover-lift class
        assert '.hover-lift' in content, "Hover-lift class not found"
        assert 'transition: transform' in content, "Transform transition not found for hover-lift"
        assert '.hover-lift:hover' in content, "Hover state for hover-lift not found"
        assert 'translateY(-5px)' in content, "Hover lift translation not found"
        assert 'box-shadow' in content, "Box shadow for hover effect not found"

def test_button_press_animation():
    """Test button press animation properties"""
    css_path = 'static/css/animations.css'
    
    with open(css_path, 'r') as f:
        content = f.read()
        
        # Check button-press class
        assert '.button-press' in content, "Button-press class not found"
        assert 'transition: all 0.2s' in content or 'transition: all' in content, "Button transition not found"
        assert '.button-press:active' in content, "Button active state not found"
        assert 'scale(0.95)' in content, "Button press scale not found"

def test_pulse_glow_animation():
    """Test pulse glow animation for CTAs"""
    css_path = 'static/css/animations.css'
    
    with open(css_path, 'r') as f:
        content = f.read()
        
        # Check pulse-glow class
        assert '.pulse-glow' in content, "Pulse-glow class not found"
        assert 'animation: pulse' in content, "Pulse animation not applied"
        assert '2s infinite' in content, "Pulse animation duration/iteration not found"
        
        # Check pulse keyframe
        assert '@keyframes pulse' in content, "Pulse keyframe not defined"
        assert 'box-shadow' in content, "Box shadow in pulse animation not found"
        assert 'rgba(253, 224, 71' in content, "Yellow glow color not found"

def test_loading_skeleton_animation():
    """Test loading skeleton animation for lazy loading"""
    css_path = 'static/css/animations.css'
    
    with open(css_path, 'r') as f:
        content = f.read()
        
        # Check loading skeleton class
        assert '.loading-skeleton' in content, "Loading skeleton class not found"
        assert 'background: linear-gradient' in content, "Loading gradient not found"
        assert 'animation: loading' in content, "Loading animation not applied"
        
        # Check loading keyframe
        assert '@keyframes loading' in content, "Loading keyframe not defined"
        assert 'background-position' in content, "Background position animation not found"

def test_smooth_scroll_class():
    """Test smooth scroll class is defined"""
    css_path = 'static/css/animations.css'
    
    with open(css_path, 'r') as f:
        content = f.read()
        
        assert '.smooth-scroll' in content or 'scroll-behavior: smooth' in content, "Smooth scroll not defined"

def test_animation_on_scroll_properties():
    """Test animate-on-scroll class properties"""
    css_path = 'static/css/animations.css'
    
    with open(css_path, 'r') as f:
        content = f.read()
        
        # Check initial state
        assert '.animate-on-scroll' in content, "Animate-on-scroll class not found"
        assert 'opacity: 0' in content, "Initial opacity not set for scroll animation"
        assert 'translateY(20px)' in content, "Initial transform not set for scroll animation"
        assert 'transition: all' in content, "Transition not set for scroll animation"
        
        # Check animated state
        assert '.animate-on-scroll.animated' in content, "Animated state class not found"
        assert 'opacity: 1' in content, "Final opacity not set"
        assert 'translateY(0)' in content, "Final transform not set"

def test_animation_durations():
    """Test that animations have appropriate durations"""
    css_path = 'static/css/animations.css'
    
    with open(css_path, 'r') as f:
        content = f.read()
        
        # Check for various duration values
        duration_patterns = [
            r'0\.\d+s',  # Decimal seconds
            r'\d+ms',     # Milliseconds
            r'ease',      # Easing functions
            r'ease-out',
        ]
        
        for pattern in duration_patterns:
            matches = re.findall(pattern, content)
            assert len(matches) > 0, f"No animation durations matching pattern '{pattern}' found"
        
        # Check that some form of timing/duration exists
        assert 's' in content or 'ms' in content, "Animation durations should be defined"
        assert 'transition' in content or 'animation' in content, "Transitions or animations should be defined"

def test_tailwind_config_animations():
    """Test that Tailwind config includes custom animations"""
    config_path = 'tailwind.config.js'
    assert os.path.exists(config_path), "Tailwind config file not found"
    
    with open(config_path, 'r') as f:
        content = f.read()
        
        # Check for animation extensions
        assert 'animation:' in content or 'animation: {' in content, "Animation config not found"
        assert 'keyframes:' in content or 'keyframes: {' in content, "Keyframes config not found"
        
        # Check for specific animations
        animations = ['fade-in', 'slide-down', 'slide-up', 'scale-in', 'pulse-glow']
        for anim in animations:
            assert anim in content, f"Animation '{anim}' not found in Tailwind config"

def test_animations_applied_to_elements(client):
    """Test that animation classes are applied to HTML elements"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for pulse-glow on CTA button
    cta_buttons = soup.find_all('a', class_='pulse-glow')
    assert len(cta_buttons) > 0, "No elements with pulse-glow animation found"
    
    # Check for button-press on buttons
    button_press_elements = soup.find_all(class_='button-press')
    assert len(button_press_elements) > 0, "No elements with button-press class found"
    
    # Check for animate-on-scroll
    scroll_animated = soup.find_all(class_='animate-on-scroll')
    assert len(scroll_animated) > 0, "No elements with animate-on-scroll found"
    
    # Check for hover-lift on cards
    hover_lift_elements = soup.find_all(class_='hover-lift')
    assert len(hover_lift_elements) > 0, "No elements with hover-lift found"

def test_animation_performance_optimizations():
    """Test that animations are optimized for performance"""
    css_path = 'static/css/animations.css'
    
    with open(css_path, 'r') as f:
        content = f.read()
        
        # Check for transform usage (GPU accelerated)
        assert 'transform' in content, "Transform property not used for animations"
        
        # Check for will-change or transform3d hints (optional but good)
        # Note: will-change should be used sparingly
        
        # Check that animations use appropriate properties
        gpu_props = ['transform', 'opacity']
        for prop in gpu_props:
            assert prop in content, f"GPU-accelerated property '{prop}' not found"