# AI Image Generator

Generate beautiful images from text prompts using AI APIs.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set API keys (choose one or both):
```bash
# For DALL-E
export OPENAI_API_KEY="your-openai-api-key"

# For Stability AI
export STABILITY_API_KEY="your-stability-api-key"
```

## Usage

### Interactive Mode
```bash
python image_generator.py --interactive
```

### Single Generation
```bash
python image_generator.py --prompt "Lord Krishna playing flute by river"
```

### Specify Provider
```bash
python image_generator.py --prompt "beautiful landscape" --provider dalle
python image_generator.py --prompt "portrait of a warrior" --provider stability
```

## Features

- **Multiple AI Providers**: DALL-E 3 and Stability AI support
- **Prompt Enhancement**: Automatically improves prompts with artistic details
- **Interactive Mode**: Continuous prompt input
- **Smart Styling**: Detects content type and suggests appropriate art styles
- **High Quality**: Generates 1024x1024 HD images
- **Auto Save**: Images saved to `generated_images/` folder

## API Keys

Get your API keys from:
- OpenAI: https://platform.openai.com/api-keys
- Stability AI: https://platform.stability.ai/account/keys

## Examples

- "Lord Krishna playing flute near Yamuna river"
- "Peaceful meditation scene in a forest"
- "Beautiful sunset over mountains"
- "Traditional Indian palace architecture"