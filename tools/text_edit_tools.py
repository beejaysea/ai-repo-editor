import os

class TextEditTools:
    def __init__(self, directory):
        self.directory = directory
        self.file_histories = {}

    def _normalize_path(self, path):
        clean_path = path.replace('/repo/', '/', 1)
        return os.path.join('work_dir', self.directory, clean_path.lstrip('/'))

    def _is_path_allowed(self, path):
        work_dir = os.path.join(os.getcwd(), 'work_dir', self.directory)
        abs_path = os.path.abspath(path)
        return abs_path.startswith(work_dir)

    def _denormalize_path(self, path):
        work_dir_prefix = os.path.join('work_dir', self.directory)
        return '/repo/' + path.replace(work_dir_prefix + os.sep, '', 1)

    def view(self, path, view_range=None, truncate_length=None):
        path = self._normalize_path(path)
        if not self._is_path_allowed(path):
            return "Error: Invalid path"
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
            output = self.list_directory(path, depth=2)
        else:
            output = f"Error: Path does not exist"

        if truncate_length and len(output) > truncate_length:
            output = output[:truncate_length] + '\n<response clipped>'
        return output

    def list_directory(self, path, depth):
        path = self._normalize_path(path)
        if not self._is_path_allowed(path):
            return "Error: Invalid path"
        result = []
        work_dir_prefix = os.path.join(os.getcwd(), 'work_dir', self.directory) + os.sep
        if not os.path.exists(path):
            os.makedirs(path)
        def helper(current_path, current_depth):
            if current_depth > depth:
                return
            for item in os.listdir(current_path):
                if not item.startswith('.'):
                    full_path = os.path.join(current_path, item)
                    relative_path = '/repo/' + full_path[len(work_dir_prefix):]
                    result.append(relative_path)
                    if os.path.isdir(full_path):
                        helper(full_path, current_depth + 1)

        helper(path, 1)
        return '\n'.join(result)

    def create(self, path, file_text):
        path = self._normalize_path(path)
        if not self._is_path_allowed(path):
            return "Error: Invalid path"
        if os.path.exists(path):
            if os.path.isfile(path):
                return "Error: File already exists"
            else:
                return "Error: Path exists and is not a file"
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(file_text)
            self.file_histories[path] = [file_text]
            return f"File created at {self._denormalize_path(path)}"

    def str_replace(self, path, old_str, new_str):
        path = self._normalize_path(path)
        if not self._is_path_allowed(path):
            return "Error: Invalid path"
        if not os.path.isfile(path):
            return "Error: File does not exist"

        with open(path, 'r') as f:
            lines = f.readlines()
        old_lines = old_str.splitlines(keepends=True)
        new_lines = new_str.splitlines(keepends=True)

        matches = []
        for i in range(len(lines) - len(old_lines) + 1):
            if lines[i:i + len(old_lines)] == old_lines:
                matches.append(i)

        if len(matches) == 0:
            return "Error: old_str not found in file"
        elif len(matches) > 1:
            return "Error: old_str is not unique in file"
        else:
            idx = matches[0]
            new_content_lines = lines[:idx] + new_lines + lines[idx + len(old_lines):]
            new_content = ''.join(new_content_lines)
            if path in self.file_histories:
                self.file_histories[path].append(''.join(lines))
            else:
                self.file_histories[path] = [''.join(lines)]
            with open(path, 'w') as f:
                f.write(new_content)
            return f"Replaced text in {self._denormalize_path(path)}"

    def insert(self, path, insert_line, new_str):
        path = self._normalize_path(path)
        if not self._is_path_allowed(path):
            return "Error: Invalid path"
        if not os.path.isfile(path):
            return "Error: File does not exist"

        with open(path, 'r') as f:
            lines = f.readlines()
        if insert_line < 1 or insert_line > len(lines):
            return "Error: insert_line is out of range"

        insert_idx = insert_line
        new_lines = new_str.splitlines(keepends=True)
        new_content_lines = lines[:insert_idx] + new_lines + lines[insert_idx:]
        new_content = ''.join(new_content_lines)
        if path in self.file_histories:
            self.file_histories[path].append(''.join(lines))
        else:
            self.file_histories[path] = [''.join(lines)]
        with open(path, 'w') as f:
            f.write(new_content)
        return f"Inserted text into {self._denormalize_path(path)} after line {insert_line}"

    def undo_edit(self, path):
        path = self._normalize_path(path)
        if not self._is_path_allowed(path):
            return "Error: Invalid path"
        if path not in self.file_histories or len(self.file_histories[path]) == 0:
            return "No edits to undo"
        else:
            last_content = self.file_histories[path].pop()
            with open(path, 'w') as f:
                f.write(last_content)
            return f"Last edit to {self._denormalize_path(path)} has been undone"
