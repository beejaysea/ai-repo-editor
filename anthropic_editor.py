import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

message="""Generate a well-structured architecture for a new software project.
The project is a web application that allows users to create and share documents.
The application should have a user-friendly interface that allows users to easily create, edit, and share documents.
The application should also have a robust backend that can handle a large number of users and documents.
"""
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
    messages=[{"role": "user", "content": message}],
    betas=["computer-use-2024-10-22"],
)
print(response)
