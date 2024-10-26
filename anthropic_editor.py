import anthropic
from dotenv import load_dotenv
from anthropic.types.beta import BetaTextBlock, BetaToolUseBlock
from tools.text_edit_tools import list_directory, view, create, str_replace, insert, undo_edit

load_dotenv()

client = anthropic.Anthropic()

def process_goal(input_goal):
    files = list_directory('.', 6)
    message_history = [{"role": "user", "content": input_goal}]

    done = False
    while not done:
        # print(message_history)
        response = client.beta.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4095,
            tools=[
                {
                "type": "text_editor_20241022",
                "name": "str_replace_editor"
                },
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

input_goal=f"""Our project is a brochure site for a boutique software development firm specializing in AI.
The landing page should include the following sections:
- A hero section with a title and a brief description of the company
- A section with a list of services offered
- A section with a list of projects completed
- A contact form
- A footer with contact information
- A navigation bar with links to each section
- A case studies page
- A pricing page
- An about page

Here's a list of the existing files in the project:
{list_directory('.', 6)}

Review the existing files and create or update files as needed to implement the site.
"""

process_goal(input_goal)
