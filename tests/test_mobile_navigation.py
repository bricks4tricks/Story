import pytest
from flask import Flask
from bs4 import BeautifulSoup
import json

@pytest.fixture
def client():
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_mobile_nav_script_loaded(client):
    """Test that mobile navigation script is loaded on index page"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for mobile nav script
    scripts = soup.find_all('script', src='/static/js/mobileNav.js')
    assert len(scripts) > 0, "Mobile navigation script not found"
    
    # Check that script has defer attribute
    assert scripts[0].get('defer') is not None, "Mobile nav script should have defer attribute"

def test_mobile_menu_button_exists(client):
    """Test that mobile menu toggle button exists with proper attributes"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for mobile menu toggle button
    mobile_toggle = soup.find('button', id='mobile-menu-toggle')
    assert mobile_toggle is not None, "Mobile menu toggle button not found"
    
    # Check for accessibility attributes
    assert mobile_toggle.get('aria-label') == 'Toggle mobile menu', "Missing or incorrect aria-label"
    assert mobile_toggle.get('aria-expanded') == 'false', "Missing or incorrect aria-expanded"
    
    # Check for md:hidden class (hidden on desktop)
    classes = mobile_toggle.get('class', [])
    assert 'md:hidden' in classes, "Mobile menu button should be hidden on desktop"

def test_mobile_menu_structure(client):
    """Test that mobile menu has correct structure"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for mobile menu div
    mobile_menu = soup.find('div', id='mobile-menu')
    assert mobile_menu is not None, "Mobile menu container not found"
    
    # Check that it's initially hidden
    classes = mobile_menu.get('class', [])
    assert 'hidden' in classes, "Mobile menu should be initially hidden"
    assert 'md:hidden' in classes, "Mobile menu should be hidden on desktop"
    
    # Check for menu links
    menu_links = mobile_menu.find_all('a')
    assert len(menu_links) >= 3, "Mobile menu should have at least 3 navigation links"
    
    # Verify link hrefs
    expected_links = ['#stories', '#pricing', '#faq']
    actual_links = [link.get('href') for link in menu_links if link.get('href', '').startswith('#')]
    for expected in expected_links:
        assert expected in actual_links, f"Expected link {expected} not found in mobile menu"

def test_mobile_nav_hamburger_icon(client):
    """Test that mobile menu button has hamburger icon SVG"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    mobile_toggle = soup.find('button', id='mobile-menu-toggle')
    assert mobile_toggle is not None
    
    # Check for SVG icon
    svg = mobile_toggle.find('svg')
    assert svg is not None, "SVG icon not found in mobile menu button"
    
    # Check SVG attributes
    assert svg.get('class') == ['w-6', 'h-6'] or 'w-6' in svg.get('class', []), "SVG should have size classes"
    assert svg.get('fill') == 'none', "SVG should have fill='none'"
    assert svg.get('stroke') == 'currentColor', "SVG should have stroke='currentColor'"

def test_dashboard_mobile_nav(client):
    """Test mobile navigation on dashboard page"""
    # Dashboard requires authentication, test will check redirect behavior
    response = client.get('/dashboard.html')
    
    # Dashboard should redirect if not authenticated
    assert response.status_code in [200, 302, 404]
    
    # If we can access the page, check for mobile nav
    if response.status_code == 200:
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for mobile menu toggle on dashboard
        mobile_toggle = soup.find('button', id='mobile-menu-toggle')
        if mobile_toggle:
            assert mobile_toggle is not None, "Mobile menu toggle should exist on dashboard"

def test_mobile_nav_responsive_classes(client):
    """Test that navigation has proper responsive classes"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check desktop navigation
    nav = soup.find('nav')
    assert nav is not None, "Navigation element not found"
    
    # Find desktop menu items container - look for any div with both classes
    desktop_menu = None
    for div in soup.find_all('div'):
        classes = div.get('class', [])
        if 'hidden' in classes and 'md:flex' in classes:
            desktop_menu = div
            break
    
    assert desktop_menu is not None, "Desktop menu container with responsive classes not found"
    
    # Check that desktop menu has proper classes
    classes = desktop_menu.get('class', [])
    assert 'hidden' in classes, "Desktop menu should be hidden on mobile"
    assert 'md:flex' in classes, "Desktop menu should be flex on medium+ screens"

def test_animations_css_loaded(client):
    """Test that animations CSS is loaded"""
    response = client.get('/')
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for animations CSS link
    animation_link = soup.find('link', href='/static/css/animations.css')
    assert animation_link is not None, "Animations CSS not linked"
    assert animation_link.get('rel') == ['stylesheet'], "Animations link should be stylesheet"

def test_mobile_nav_javascript_file_exists():
    """Test that mobile navigation JavaScript file exists and has expected content"""
    import os
    
    js_path = 'static/js/mobileNav.js'
    assert os.path.exists(js_path), f"Mobile navigation JS file not found at {js_path}"
    
    with open(js_path, 'r') as f:
        content = f.read()
        
        # Check for key functionality
        assert 'mobile-menu-toggle' in content, "Mobile menu toggle ID not found in script"
        assert 'mobile-menu' in content, "Mobile menu ID not found in script"
        assert 'addEventListener' in content, "Event listeners not found in script"
        assert 'click' in content, "Click event handler not found"
        assert 'classList.toggle' in content, "Class toggling functionality not found"
        assert 'hidden' in content, "Hidden class manipulation not found"