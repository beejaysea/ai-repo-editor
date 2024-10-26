import anthropic
from dotenv import load_dotenv
from anthropic.types.beta import BetaTextBlock, BetaToolUseBlock
from tools.text_edit_tools import list_directory, view, create, str_replace, insert, undo_edit

load_dotenv()

client = anthropic.Anthropic()

files = list_directory('.', 6)

input_goal=f"""Generate a well-structured architecture for a new software project.
The project is a web application that allows users to create and share documents.
The application should have a user-friendly interface that allows users to easily create, edit, and share documents.
The application should also have a robust backend that can handle a large number of users and documents.
Create an architecture doc, and the first couple of code files for a working example.

Here's a list of the existing files in the project:
{files}
"""

message_history = [{"role": "user", "content": input_goal}]

done = False
while not done:
    # print(message_history)
    response = client.beta.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4095,
        tools=[
            # {
            #   "type": "computer_20241022",
            #   "name": "computer",
            #   "display_width_px": 1024,
            #   "display_height_px": 768,
            #   "display_number": 1,
            # },
            {
            "type": "text_editor_20241022",
            "name": "str_replace_editor"
            },
            # {
            #   "type": "bash_20241022",
            #   "name": "bash"
            # }
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
                command = tool_input['command']
                if command == 'view':
                    result = view(tool_input['path'], tool_input.get('view_range'))
                elif command == 'create':
                    result = create(tool_input['path'], tool_input['file_text'])
                elif command == 'str_replace':
                    result = str_replace(tool_input['path'], tool_input['old_str'], tool_input['new_str'])
                elif command == 'insert':
                    result = insert(tool_input['path'], tool_input['insert_line'], tool_input['new_str'])
                elif command == 'undo_edit':
                    result = undo_edit(tool_input['path'])
                message_history.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": message.id, "content": result}]})
                print(result)

    if response.stop_reason in ['end_turn', 'max_tokens', 'stop_sequence']:
        print("Stopped: ", response.stop_reason)
        print(response.content[0].text)
        done = True
