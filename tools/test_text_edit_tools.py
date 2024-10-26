import os
from text_edit_tools import TextEditTools

# Initialize with a test directory
tools = TextEditTools('test_dir')

# Create a test file
print(tools.create('test.txt', 'Hello\nWorld\n'))

# View the file
print(tools.view('test.txt'))

# Make some edits
print(tools.str_replace('test.txt', 'World', 'Universe'))
print(tools.insert('test.txt', 1, 'New line\n'))

# View changes
print(tools.view('test.txt'))

# Undo last edit
print(tools.undo_edit('test.txt'))

# View final state
print(tools.view('test.txt'))
