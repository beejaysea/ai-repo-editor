# Anthropic Editor

A Python-based text editor tool that integrates with Anthropic's Claude-3 API to enable AI-assisted file editing and manipulation.

## Features
- File viewing with line range support
- Directory listing and traversal
- String replacement in files
- Text insertion at specific lines
- Edit history with undo functionality
- Safe file path handling within work directory
- AI-powered text manipulation using Claude-3

## Requirements
- Python
- anthropic
- python-dotenv

## Installation
```bash
pip install -r requirements.txt
```

## Usage
1. Create a `.env` file with your Anthropic API key:
```
ANTHROPIC_API_KEY=your_key_here
```

2. Run the editor:
```bash
python anthropic_editor.py
