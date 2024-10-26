# AI Repo Editor

A Python-based text editor tool that leverages Anthropic's Claude-3 API for AI-powered file manipulation and code generation.

## Features
- AI-powered text and code generation using Claude-3
- File creation and modification
- String replacement functionality
- Line-specific text insertion
- Edit history with undo capability
- Safe file operations within work directory
- Directory listing and traversal
- File viewing with line range support

## Requirements
- Python 3.x
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
```

The editor uses Claude-3's computer-use beta capabilities to perform file operations and generate content based on natural language input.
