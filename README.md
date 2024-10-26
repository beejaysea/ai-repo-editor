# Anthropic Editor

A Python-based text editor tool that integrates with Anthropic's Claude API to enable AI-assisted file editing and manipulation.

## Features
- File viewing and manipulation
- Directory listing
- Text replacement and insertion
- Edit history with undo capability
- Safe file path handling within work directory

## Requirements
- Python
- anthropic
- python-dotenv

## Installation
```bash
pip install -r requirements.txt
```

## Usage
Create a `.env` file with your Anthropic API key, then run:
```bash
python anthropic_editor.py
