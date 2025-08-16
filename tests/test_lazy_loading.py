import pytest
from flask import Flask
from bs4 import BeautifulSoup
import os

@pytest.fixture
def client():
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_lazy_load_script_loaded(client):
    """Test that lazy loading script is loaded on index page"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for lazy load script
    scripts = soup.find_all('script', src='/static/js/lazyLoad.js')
    assert len(scripts) > 0, "Lazy loading script not found"
    
    # Check that script has defer attribute for performance
    assert scripts[0].get('defer') is not None, "Lazy load script should have defer attribute"

def test_lazy_load_styles_present(client):
    """Test that lazy loading styles are present"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for inline styles for lazy loading
    style_tags = soup.find_all('style')
    styles_found = False
    for style in style_tags:
        if style.string and '[data-src]' in style.string:
            styles_found = True
            # Check for blur filter
            assert 'filter: blur' in style.string, "Blur filter not found for lazy load"
            assert 'transition: filter' in style.string, "Filter transition not found"
            assert '.fade-in' in style.string, "Fade-in class styles not found"
            break
    
    assert styles_found, "Lazy loading styles not found in page"

def test_animate_on_scroll_classes(client):
    """Test that animate-on-scroll classes are applied to elements"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for elements with animate-on-scroll class
    animated_elements = soup.find_all(class_='animate-on-scroll')
    assert len(animated_elements) > 0, "No elements with animate-on-scroll class found"
    
    # Check hero section has animation
    hero_section = soup.find('section', class_='py-20 md:py-32')
    if hero_section:
        classes = hero_section.get('class', [])
        assert 'animate-on-scroll' in classes, "Hero section should have animate-on-scroll"

def test_hover_lift_classes(client):
    """Test that hover-lift classes are applied to cards"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for elements with hover-lift class
    hover_elements = soup.find_all(class_='hover-lift')
    assert len(hover_elements) > 0, "No elements with hover-lift class found"
    
    # Check that cards in how-it-works section have hover-lift
    cards = soup.find_all('div', class_='bg-slate-800 p-8 rounded-2xl')
    for card in cards:
        classes = card.get('class', [])
        assert 'hover-lift' in classes, "Cards should have hover-lift class"

def test_lazy_load_javascript_file_exists():
    """Test that lazy load JavaScript file exists and has expected content"""
    js_path = 'static/js/lazyLoad.js'
    assert os.path.exists(js_path), f"Lazy load JS file not found at {js_path}"
    
    with open(js_path, 'r') as f:
        content = f.read()
        
        # Check for key functionality
        assert 'IntersectionObserver' in content, "IntersectionObserver not found in script"
        assert 'data-src' in content, "data-src attribute handling not found"
        assert 'lazyImages' in content, "Lazy images variable not found"
        assert 'lazyVideos' in content, "Lazy videos variable not found"
        assert 'lazyIframes' in content, "Lazy iframes variable not found"
        assert 'isIntersecting' in content, "Intersection check not found"
        assert 'observe' in content, "Observer.observe method not found"
        assert 'unobserve' in content, "Observer.unobserve method not found"
        assert 'fade-in' in content, "Fade-in class addition not found"
        assert 'animate-on-scroll' in content, "Scroll animation handling not found"
        assert 'rootMargin' in content, "Observer rootMargin configuration not found"
        assert 'threshold' in content, "Observer threshold configuration not found"

def test_lazy_load_image_attributes(client):
    """Test that images can have data-src attributes for lazy loading"""
    # This test checks if the structure supports lazy loading
    # In a real implementation, you would add data-src to actual images
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check that the page structure supports lazy loading
    # The script should be present to handle data-src attributes
    scripts = soup.find_all('script', src='/static/js/lazyLoad.js')
    assert len(scripts) > 0, "Lazy load script required for data-src handling"

def test_animation_observer_configuration():
    """Test that animation observer is properly configured"""
    js_path = 'static/js/lazyLoad.js'
    
    with open(js_path, 'r') as f:
        content = f.read()
        
        # Check for animation observer configuration
        assert 'animationObserver' in content or 'IntersectionObserver' in content, "Animation observer not configured"
        
        # Check for proper threshold (for triggering animations)
        assert 'threshold: 0.1' in content or 'threshold:' in content, "Observer threshold not configured"
        
        # Check for rootMargin to trigger animations before element is fully visible
        assert 'rootMargin' in content, "RootMargin not configured for early trigger"
        
        # Check that animated class is added
        assert "classList.add('animated')" in content or ".add('animated')" in content, "Animated class not being added"

def test_performance_optimization_defer():
    """Test that scripts are loaded with defer for performance"""
    js_files = ['static/js/lazyLoad.js', 'static/js/mobileNav.js', 'static/js/accessibility.js']
    
    for js_file in js_files:
        assert os.path.exists(js_file), f"JavaScript file {js_file} should exist"
    
    # Check that these scripts would be loaded with defer in the HTML
    # This is validated by checking the actual HTML output
    from app import app
    with app.test_client() as client:
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        for js_file in js_files:
            script_name = js_file.replace('static/', '/static/')
            script = soup.find('script', src=script_name)
            if script:  # Only check if script is actually included
                assert script.get('defer') is not None, f"{script_name} should have defer attribute"