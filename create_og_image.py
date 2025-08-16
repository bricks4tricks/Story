"""
Create Open Graph and social media preview images for LogicAndStories.

This script generates optimized images for search engines and social platforms.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_og_image():
    """Create Open Graph image for social sharing."""
    
    # Standard OG image size (1200x630 is optimal for most platforms)
    width, height = 1200, 630
    img = Image.new('RGB', (width, height), (79, 70, 229))  # Indigo background
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(height):
        # Gradient from indigo to purple
        r = int(79 + (124 - 79) * (y / height))
        g = int(70 + (58 - 70) * (y / height))
        b = int(229 + (237 - 229) * (y / height))
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add subtle pattern overlay
    for x in range(0, width, 60):
        for y in range(0, height, 60):
            draw.ellipse([x-2, y-2, x+2, y+2], fill=(255, 255, 255, 20))
    
    # Try to load fonts, fallback to default
    try:
        title_font = ImageFont.truetype("arial.ttf", 72)
        subtitle_font = ImageFont.truetype("arial.ttf", 36)
        desc_font = ImageFont.truetype("arial.ttf", 28)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        desc_font = ImageFont.load_default()
    
    # Text content
    title = "Logic & Stories"
    subtitle = "Math Learning Through Storytelling"
    description = "Engaging math education for kids with interactive stories and logic puzzles"
    
    # Calculate text positions (centered)
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = height // 2 - 100
    
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title_y + 90
    
    desc_bbox = draw.textbbox((0, 0), description, font=desc_font)
    desc_width = desc_bbox[2] - desc_bbox[0]
    desc_x = (width - desc_width) // 2
    desc_y = subtitle_y + 60
    
    # Add text shadow for better readability
    shadow_offset = 3
    draw.text((title_x + shadow_offset, title_y + shadow_offset), title, 
              fill=(0, 0, 0, 80), font=title_font)
    draw.text((subtitle_x + shadow_offset, subtitle_y + shadow_offset), subtitle, 
              fill=(0, 0, 0, 80), font=subtitle_font)
    draw.text((desc_x + shadow_offset, desc_y + shadow_offset), description, 
              fill=(0, 0, 0, 80), font=desc_font)
    
    # Add main text
    draw.text((title_x, title_y), title, fill=(255, 255, 255), font=title_font)
    draw.text((subtitle_x, subtitle_y), subtitle, fill=(251, 191, 36), font=subtitle_font)
    draw.text((desc_x, desc_y), description, fill=(255, 255, 255, 220), font=desc_font)
    
    # Add decorative elements
    # Book icon on the left
    book_x, book_y = 100, height // 2 - 60
    book_width, book_height = 80, 120
    
    # Book cover
    draw.rectangle([book_x, book_y, book_x + book_width, book_y + book_height], 
                   fill=(251, 191, 36), outline=(217, 119, 6), width=3)
    
    # Book spine
    spine_x = book_x + 12
    draw.line([spine_x, book_y, spine_x, book_y + book_height], 
              fill=(217, 119, 6), width=4)
    
    # Mathematical symbols on the right
    symbols_x = width - 150
    symbols_y = height // 2 - 50
    
    # Plus symbol
    draw.text((symbols_x, symbols_y), "+", fill=(255, 255, 255), font=title_font)
    
    # Brain/logic symbol
    brain_x = symbols_x + 20
    brain_y = symbols_y + 60
    draw.ellipse([brain_x, brain_y, brain_x + 60, brain_y + 40], 
                outline=(255, 255, 255), width=3)
    
    # Add small decorative dots
    for i, (x, y) in enumerate([(300, 150), (900, 200), (350, 500), (850, 480)]):
        size = 8 if i % 2 == 0 else 6
        draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], 
                    fill=(255, 255, 255, 150))
    
    return img

def create_twitter_card():
    """Create Twitter card image (different aspect ratio)."""
    width, height = 1200, 600
    img = Image.new('RGB', (width, height), (79, 70, 229))
    draw = ImageDraw.Draw(img)
    
    # Similar to OG image but optimized for Twitter
    # Gradient background
    for y in range(height):
        r = int(79 + (124 - 79) * (y / height))
        g = int(70 + (58 - 70) * (y / height))
        b = int(229 + (237 - 229) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 64)
        subtitle_font = ImageFont.truetype("arial.ttf", 32)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Centered text
    title = "Logic & Stories"
    subtitle = "Math Learning Through Storytelling"
    
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = height // 2 - 50
    
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title_y + 80
    
    # Text with shadow
    draw.text((title_x + 2, title_y + 2), title, fill=(0, 0, 0, 80), font=title_font)
    draw.text((title_x, title_y), title, fill=(255, 255, 255), font=title_font)
    
    draw.text((subtitle_x + 2, subtitle_y + 2), subtitle, fill=(0, 0, 0, 80), font=subtitle_font)
    draw.text((subtitle_x, subtitle_y), subtitle, fill=(251, 191, 36), font=subtitle_font)
    
    return img

def save_social_images():
    """Save all social media images."""
    static_dir = "static"
    
    # Create Open Graph image
    og_img = create_og_image()
    og_img.save(os.path.join(static_dir, "og-image.png"), format='PNG', optimize=True)
    
    # Create Twitter card image
    twitter_img = create_twitter_card()
    twitter_img.save(os.path.join(static_dir, "twitter-card.png"), format='PNG', optimize=True)
    
    # Create a square version for various platforms
    square_img = og_img.resize((630, 630), Image.Resampling.LANCZOS)
    square_img.save(os.path.join(static_dir, "social-square.png"), format='PNG', optimize=True)
    
    print("✅ Generated social media images:")
    print("  - og-image.png (1200x630) - Open Graph standard")
    print("  - twitter-card.png (1200x600) - Twitter optimized") 
    print("  - social-square.png (630x630) - Square format")

if __name__ == "__main__":
    print("🎨 Creating social media preview images...")
    save_social_images()
    print("\n🚀 Social media images created successfully!")
    print("💡 These will appear when your site is shared on social platforms and search engines.")