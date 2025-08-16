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

def test_accessibility_script_loaded(client):
    """Test that accessibility script is loaded on index page"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for accessibility script
    scripts = soup.find_all('script', src='/static/js/accessibility.js')
    assert len(scripts) > 0, "Accessibility script not found"
    
    # Check that script has defer attribute
    assert scripts[0].get('defer') is not None, "Accessibility script should have defer attribute"

def test_main_content_id(client):
    """Test that main content has proper ID for skip navigation"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for main content ID
    main_content = soup.find('main', id='main-content')
    assert main_content is not None, "Main content with id='main-content' not found"
    
    # Check for role attribute
    assert main_content.get('role') == 'main', "Main element should have role='main'"

def test_aria_labels_on_sections(client):
    """Test that sections have proper ARIA labels"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check hero section
    hero_section = soup.find('section', role='region', attrs={'aria-label': 'Hero section'})
    assert hero_section is not None, "Hero section with ARIA label not found"
    
    # Check how it works section
    how_it_works = soup.find('section', id='how-it-works')
    assert how_it_works is not None, "How it works section not found"
    assert how_it_works.get('role') == 'region', "How it works section should have role='region'"
    assert how_it_works.get('aria-label') is not None, "How it works section should have aria-label"
    
    # Check stories section
    stories_section = soup.find('section', id='stories')
    assert stories_section is not None, "Stories section not found"
    assert stories_section.get('role') == 'region', "Stories section should have role='region'"
    assert stories_section.get('aria-label') is not None, "Stories section should have aria-label"

def test_mobile_menu_button_accessibility(client):
    """Test that mobile menu button has accessibility attributes"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    mobile_toggle = soup.find('button', id='mobile-menu-toggle')
    assert mobile_toggle is not None, "Mobile menu toggle button not found"
    
    # Check for aria-label
    assert mobile_toggle.get('aria-label') is not None, "Mobile menu button should have aria-label"
    
    # Check for aria-expanded
    assert mobile_toggle.get('aria-expanded') is not None, "Mobile menu button should have aria-expanded"

def test_accessibility_css_loaded(client):
    """Test that accessibility CSS is loaded"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for animations CSS which includes accessibility styles
    animation_link = soup.find('link', href='/static/css/animations.css')
    assert animation_link is not None, "Animations/Accessibility CSS not linked"

def test_accessibility_css_file_content():
    """Test that accessibility CSS file has required styles"""
    css_path = 'static/css/animations.css'
    assert os.path.exists(css_path), f"Animations CSS file not found at {css_path}"
    
    with open(css_path, 'r') as f:
        content = f.read()
        
        # Check for screen reader only styles
        assert '.sr-only' in content, "Screen reader only class not found"
        assert 'position: absolute' in content, "SR-only positioning not found"
        assert 'width: 1px' in content, "SR-only width not found"
        assert 'clip: rect(0, 0, 0, 0)' in content, "SR-only clipping not found"
        
        # Check for focus visible styles
        assert 'focus\\:not-sr-only:focus' in content or 'focus:not-sr-only' in content, "Focus visible styles not found"
        
        # Check for keyboard navigation styles
        assert 'body.keyboard-nav' in content, "Keyboard navigation styles not found"
        assert 'outline: 3px solid' in content, "Focus outline styles not found"
        
        # Check for high contrast mode
        assert 'body.high-contrast' in content, "High contrast mode styles not found"
        assert 'filter: contrast' in content, "Contrast filter not found"
        
        # Check for reduced motion
        assert '@media (prefers-reduced-motion: reduce)' in content, "Reduced motion media query not found"
        assert 'animation-duration: 0.01ms' in content, "Reduced animation duration not found"

def test_accessibility_javascript_file_content():
    """Test that accessibility JavaScript file has expected content"""
    js_path = 'static/js/accessibility.js'
    assert os.path.exists(js_path), f"Accessibility JS file not found at {js_path}"
    
    with open(js_path, 'r') as f:
        content = f.read()
        
        # Check for skip link creation
        assert 'Skip to main content' in content, "Skip to main content text not found"
        assert '#main-content' in content, "Main content anchor not found"
        assert 'createElement' in content, "Element creation not found"
        
        # Check for keyboard navigation
        assert 'keyboard-nav' in content, "Keyboard navigation class not found"
        assert 'Tab' in content, "Tab key detection not found"
        assert 'Enter' in content, "Enter key handling not found"
        
        # Check for ARIA live region
        assert 'aria-live' in content, "ARIA live region not found"
        assert 'polite' in content, "ARIA polite setting not found"
        assert 'aria-atomic' in content, "ARIA atomic setting not found"
        assert 'announceToScreenReader' in content, "Screen reader announcement function not found"
        
        # Check for ARIA labels
        assert 'aria-label' in content, "ARIA label handling not found"
        assert 'setAttribute' in content, "setAttribute method not found"
        
        # Check for alt text handling
        assert 'img:not([alt])' in content or 'alt' in content, "Alt text handling not found"
        
        # Check for high contrast mode
        assert 'highContrast' in content, "High contrast mode handling not found"
        assert 'localStorage' in content, "LocalStorage usage not found"
        
        # Check for reduced motion
        assert 'prefers-reduced-motion' in content, "Reduced motion preference not found"

def test_button_press_animation_class(client):
    """Test that buttons have press animation class"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for any elements with button-press class
    button_press_elements = soup.find_all(class_='button-press')
    assert len(button_press_elements) > 0, "At least some buttons should have button-press class for interaction feedback"
    
    # Check that glow buttons exist (alternative animation)
    glow_buttons = soup.find_all(class_='glow-button')
    assert len(glow_buttons) > 0, "Glow buttons should exist for visual feedback"

def test_focus_outline_styles():
    """Test that focus styles are properly defined"""
    css_path = 'static/css/animations.css'
    
    with open(css_path, 'r') as f:
        content = f.read()
        
        # Check for focus outline color
        assert '#fde047' in content, "Focus outline color (yellow) not found"
        assert 'outline-offset: 2px' in content, "Focus outline offset not found"

def test_semantic_html_structure(client):
    """Test that HTML has proper semantic structure for accessibility"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for header element
    header = soup.find('header')
    assert header is not None, "Header element not found"
    
    # Check for nav element
    nav = soup.find('nav')
    assert nav is not None, "Nav element not found"
    
    # Check for main element
    main = soup.find('main')
    assert main is not None, "Main element not found"
    
    # Check for sections with proper structure
    sections = soup.find_all('section')
    assert len(sections) > 0, "No section elements found"
    
    # Check that sections have role attributes
    for section in sections:
        role = section.get('role')
        if role:
            assert role == 'region', f"Section role should be 'region', found '{role}'"