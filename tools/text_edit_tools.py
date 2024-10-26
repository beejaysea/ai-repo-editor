import os

# Global state for file histories used in undo_edit
file_histories = {}

def _normalize_path(path):
    if not path.startswith('work_dir'):
        return os.path.join('work_dir', path.lstrip('/'))
    return path

def _is_path_allowed(path):
    work_dir = os.path.join(os.getcwd(), 'work_dir')
    abs_path = os.path.abspath(path)
    return abs_path.startswith(work_dir)

def view(path, view_range=None, truncate_length=None):
    path = _normalize_path(path)
    if not _is_path_allowed(path):
        return "Error: Path must be within ./work_dir"
    if os.path.isfile(path):
        with open(path, 'r') as f:
            lines = f.readlines()
        if view_range:
            start_line = view_range[0] - 1
            end_line = view_range[1]
            if end_line == -1:
                end_line = len(lines)
            lines = lines[start_line:end_line]
            line_offset = start_line
        else:
            line_offset = 0
        numbered_lines = ['{:>6}\t{}'.format(idx + line_offset + 1, line) for idx, line in enumerate(lines)]
        output = ''.join(numbered_lines)
    elif os.path.isdir(path):
        output = list_directory(path, depth=2)
    else:
        output = f"Error: Path {path} does not exist."

    if truncate_length and len(output) > truncate_length:
        output = output[:truncate_length] + '\n<response clipped>'
    return output

def list_directory(path, depth):
    path = _normalize_path(path)
    if not _is_path_allowed(path):
        return "Error: Path must be within ./work_dir"
    result = []
    work_dir_prefix = os.path.join(os.getcwd(), 'work_dir') + os.sep

    def helper(current_path, current_depth):
        if current_depth > depth:
            return
        for item in os.listdir(current_path):
            if not item.startswith('.'):
                full_path = os.path.join(current_path, item)
                relative_path = full_path[len(work_dir_prefix):]
                result.append(relative_path)
                if os.path.isdir(full_path):
                    helper(full_path, current_depth + 1)

    helper(path, 1)
    return '\n'.join(result)

def create(path, file_text):
    path = _normalize_path(path)
    if not _is_path_allowed(path):
        return "Error: Path must be within ./work_dir"
    if os.path.exists(path):
        if os.path.isfile(path):
            return f"Error: File {path} already exists."
        else:
            return f"Error: Path {path} exists and is not a file."
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(file_text)
        file_histories[path] = [file_text]
        return f"File {path} created."

def str_replace(path, old_str, new_str):
    path = _normalize_path(path)
    if not _is_path_allowed(path):
        return "Error: Path must be within ./work_dir"
    if not os.path.isfile(path):
        return f"Error: File {path} does not exist."

    with open(path, 'r') as f:
        lines = f.readlines()
    old_lines = old_str.splitlines(keepends=True)
    new_lines = new_str.splitlines(keepends=True)

    matches = []
    for i in range(len(lines) - len(old_lines) + 1):
        if lines[i:i + len(old_lines)] == old_lines:
            matches.append(i)

    if len(matches) == 0:
        return "Error: old_str not found in file."
    elif len(matches) > 1:
        return "Error: old_str is not unique in file."
    else:
        idx = matches[0]
        new_content_lines = lines[:idx] + new_lines + lines[idx + len(old_lines):]
        new_content = ''.join(new_content_lines)
        if path in file_histories:
            file_histories[path].append(''.join(lines))
        else:
            file_histories[path] = [''.join(lines)]
        with open(path, 'w') as f:
            f.write(new_content)
        return f"Replaced old_str in {path}."

def insert(path, insert_line, new_str):
    path = _normalize_path(path)
    if not _is_path_allowed(path):
        return "Error: Path must be within ./work_dir"
    if not os.path.isfile(path):
        return f"Error: File {path} does not exist."

    with open(path, 'r') as f:
        lines = f.readlines()
    if insert_line < 1 or insert_line > len(lines):
        return "Error: insert_line is out of range."

    insert_idx = insert_line
    new_lines = new_str.splitlines(keepends=True)
    new_content_lines = lines[:insert_idx] + new_lines + lines[insert_idx:]
    new_content = ''.join(new_content_lines)
    if path in file_histories:
        file_histories[path].append(''.join(lines))
    else:
        file_histories[path] = [''.join(lines)]
    with open(path, 'w') as f:
        f.write(new_content)
    return f"Inserted new_str into {path} after line {insert_line}."

def undo_edit(path):
    path = _normalize_path(path)
    if not _is_path_allowed(path):
        return "Error: Path must be within ./work_dir"
    if path not in file_histories or len(file_histories[path]) == 0:
        return f"No edits to undo for {path}."
    else:
        last_content = file_histories[path].pop()
        with open(path, 'w') as f:
            f.write(last_content)
        return f"Last edit to {path} has been undone."
