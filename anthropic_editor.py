import anthropic
from dotenv import load_dotenv
from anthropic.types.beta import BetaTextBlock, BetaToolUseBlock

load_dotenv()

client = anthropic.Anthropic()

input_goal="""Generate a well-structured architecture for a new software project.
The project is a web application that allows users to create and share documents.
The application should have a user-friendly interface that allows users to easily create, edit, and share documents.
The application should also have a robust backend that can handle a large number of users and documents.
"""

done = False
while not done:
    response = client.beta.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
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
        messages=[{"role": "user", "content": input_goal}],
        betas=["computer-use-2024-10-22"],
    )
    if response.stop_reason=='tool_use':
        messages = response.content
        for message in messages:
            if isinstance(message, BetaTextBlock):
                output = message.text
                print(output)
            if isinstance(message, BetaToolUseBlock):
                tool = message.input['command']
                print(tool)

    if response.stop_reason in ['end_turn', 'max_tokens', 'stop_sequence']:
        print("Stopped: ", response.stop_reason)
        print(response.content[0].text)
        done = True
