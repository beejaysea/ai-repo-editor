import anthropic
from dotenv import load_dotenv
import yaml
import sys
from anthropic.types.beta import BetaTextBlock, BetaToolUseBlock
from tools.text_edit_tools import TextEditTools
import readline

load_dotenv()

client = anthropic.Anthropic()
global_history = []

def process_goal(input_goal, start_dir='.'):
    tools = TextEditTools(start_dir)
    files = tools.list_directory('.', 6)
    system_prompt = open("system_prompt.txt", "r").read()
    input_goal_message = {"role": "user", "content": input_goal}

    global_history.append(input_goal_message)
    message_history = global_history.copy()

    done = False
    while not done:
        response = client.beta.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=system_prompt,
            max_tokens=4095,
            tools=[
                {
                    "type": "text_editor_20241022",
                    "name": "str_replace_editor"
                },
                {
                    "name": "file_delete",
                    "description": "Delete a file",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The path to the file to delete"
                            }
                        },
                        "required": ["path"],
                    },
                }
            ],
            messages=message_history,
            betas=["computer-use-2024-10-22"],
        )
        if response.stop_reason=='tool_use':
            messages = response.content
            content = []
            for message in messages:
                if isinstance(message, BetaTextBlock):
                    content.append({"type": "text", "text": message.text})
                    print(message.text)
                if isinstance(message, BetaToolUseBlock):
                    tool_input = message.input
                    content.append({"type": "tool_use", "id": message.id, "name": message.name, "input": tool_input})
                    message_history.append({"role": "assistant", "content": content})
                    if message.name == "file_delete":
                        result = tools.delete(tool_input['path'])
                    else:
                        command = tool_input['command']
                        if command == 'view':
                            result = tools.view(tool_input['path'], tool_input.get('view_range'))
                        elif command == 'create':
                            result = tools.create(tool_input['path'], tool_input['file_text'])
                        elif command == 'str_replace':
                            result = tools.str_replace(tool_input['path'], tool_input['old_str'], tool_input['new_str'])
                        elif command == 'insert':
                            result = tools.insert(tool_input['path'], tool_input['insert_line'], tool_input['new_str'])
                        elif command == 'undo_edit':
                            result = tools.undo_edit(tool_input['path'])
                    message_history.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": message.id, "content": result}]})
                    print(result)

        if response.stop_reason in ['end_turn', 'max_tokens', 'stop_sequence']:
            print("Stopped: ", response.stop_reason)
            print(response.content[0].text)
            done = True
            global_history.append( {"role": "assistant", "content": response.content[0].text} )

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config.yaml'
    
    with open("yamls/" + config_path, 'r') as f:
        config = yaml.safe_load(f)

    repo_path = config['repo_path']
    input_goal = config['input_goal']

    if config.get('include_files', True):
        input_goal += f"""

Here's a list of the existing files in the project:
{TextEditTools(repo_path).list_directory('.', 6)}

Review the existing files and create or update files as needed to implement the site.
"""
    # chat loop
    process_goal(input_goal, repo_path)
    user_quit = False
    while not user_quit:
        user_input = input("> ")
        if user_input == "/quit":
            user_quit = True
        else:
            process_goal(user_input, repo_path)

if __name__ == "__main__":
    main()
