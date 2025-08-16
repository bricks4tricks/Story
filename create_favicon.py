"""
Create a high-quality favicon for LogicAndStories.

This script generates multiple favicon formats for optimal browser support.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_favicon():
    """Create a professional favicon for LogicAndStories."""
    
    # Create a high-resolution base image (256x256 for scaling)
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Color scheme - educational and professional
    bg_color = (79, 70, 229)  # Indigo
    accent_color = (251, 191, 36)  # Amber
    text_color = (255, 255, 255)  # White
    
    # Draw background circle with slight padding
    padding = 8
    circle_size = size - (padding * 2)
    draw.ellipse([padding, padding, size - padding, size - padding], 
                 fill=bg_color, outline=(229, 231, 235), width=3)
    
    # Draw book/story element
    book_left = size * 0.2
    book_right = size * 0.8
    book_top = size * 0.15
    book_bottom = size * 0.85
    
    # Book cover
    draw.rectangle([book_left, book_top, book_right, book_bottom], 
                   fill=accent_color, outline=(217, 119, 6), width=2)
    
    # Book spine
    spine_x = book_left + (book_right - book_left) * 0.15
    draw.line([spine_x, book_top, spine_x, book_bottom], 
              fill=(217, 119, 6), width=3)
    
    # Logic symbols
    center_x = size // 2
    center_y = size // 2
    
    # Try to use a font, fallback to default if not available
    try:
        font_large = ImageFont.truetype("arial.ttf", size // 8)
        font_small = ImageFont.truetype("arial.ttf", size // 16)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Mathematical plus symbol
    plus_x = center_x - 20
    plus_y = center_y - 30
    draw.text((plus_x, plus_y), "+", fill=text_color, font=font_large, anchor="mm")
    
    # Small dots representing story elements
    dot_size = 6
    dots = [
        (center_x - 15, center_y + 20),
        (center_x, center_y + 30),
        (center_x + 15, center_y + 20)
    ]
    
    for dot_x, dot_y in dots:
        draw.ellipse([dot_x - dot_size//2, dot_y - dot_size//2, 
                     dot_x + dot_size//2, dot_y + dot_size//2], 
                    fill=text_color)
    
    # Brain/logic overlay (simplified)
    brain_x = center_x + 25
    brain_y = center_y - 15
    brain_width = 30
    brain_height = 20
    
    draw.ellipse([brain_x - brain_width//2, brain_y - brain_height//2,
                 brain_x + brain_width//2, brain_y + brain_height//2],
                outline=text_color, width=2)
    
    # Add "LS" text at bottom
    ls_y = size - 30
    draw.text((center_x, ls_y), "LS", fill=text_color, font=font_small, anchor="mm")
    
    return img

def save_favicon_formats(base_img):
    """Save favicon in multiple formats and sizes."""
    static_dir = "static"
    
    # Common favicon sizes
    sizes = [16, 32, 48, 64, 128, 256]
    
    # Save as ICO (multi-size)
    ico_images = []
    for size in [16, 32, 48]:
        resized = base_img.resize((size, size), Image.Resampling.LANCZOS)
        ico_images.append(resized)
    
    # Save the main favicon.ico
    ico_images[0].save(
        os.path.join(static_dir, "favicon.ico"),
        format='ICO',
        sizes=[(img.size[0], img.size[1]) for img in ico_images],
        append_images=ico_images[1:]
    )
    
    # Save PNG versions for modern browsers
    for size in [32, 192, 512]:
        resized = base_img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(os.path.join(static_dir, f"favicon-{size}x{size}.png"), format='PNG')
    
    # Save Apple touch icon
    apple_icon = base_img.resize((180, 180), Image.Resampling.LANCZOS)
    apple_icon.save(os.path.join(static_dir, "apple-touch-icon.png"), format='PNG')
    
    print("✅ Generated favicon files:")
    print("  - favicon.ico (16x16, 32x32, 48x48)")
    print("  - favicon-32x32.png")
    print("  - favicon-192x192.png") 
    print("  - favicon-512x512.png")
    print("  - apple-touch-icon.png (180x180)")

if __name__ == "__main__":
    print("🎨 Creating LogicAndStories favicon...")
    
    # Create the base favicon image
    favicon_img = create_favicon()
    
    # Save in multiple formats
    save_favicon_formats(favicon_img)
    
    print("\n🚀 Favicon creation complete!")
    print("💡 Add these lines to your HTML <head> section:")
    print("""
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="192x192" href="/static/favicon-192x192.png">
    <link rel="icon" type="image/png" sizes="512x512" href="/static/favicon-512x512.png">
    <link rel="apple-touch-icon" href="/static/apple-touch-icon.png">
    """)