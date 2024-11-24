import anthropic
from dotenv import load_dotenv
import yaml
import sys
import requests
from anthropic.types.beta import BetaTextBlock, BetaToolUseBlock
import readline

load_dotenv()

client = anthropic.Anthropic()
global_history = []

TOOLS_SERVICE_URL = "http://localhost:9191/text_editor"

def call_tools_service(endpoint, directory, payload):
    url = f"{TOOLS_SERVICE_URL}/{directory}/{endpoint}"
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.text

def process_goal(input_goal, start_dir="."):
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
                {"type": "text_editor_20241022", "name": "str_replace_editor"},
                {
                    "name": "file_delete",
                    "description": "Delete a file",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The path to the file to delete",
                            }
                        },
                        "required": ["path"],
                    },
                },
                {"type": "bash_20241022", "name": "bash"},
            ],
            messages=message_history,
            betas=["computer-use-2024-10-22"],
        )
        if response.stop_reason == "tool_use":
            messages = response.content
            content = []
            for message in messages:
                if isinstance(message, BetaTextBlock):
                    content.append({"type": "text", "text": message.text})
                if isinstance(message, BetaToolUseBlock):
                    tool_input = message.input
                    content.append(
                        {
                            "type": "tool_use",
                            "id": message.id,
                            "name": message.name,
                            "input": tool_input,
                        }
                    )
                    message_history.append({"role": "assistant", "content": content})
                    print(message.name)
                    try:
                        if message.name == "file_delete":
                            command = tool_input['command']
                            print(f"> {command} {tool_input['path']}")
                            result = call_tools_service("delete", start_dir, tool_input)
                        if message.name=='str_replace_editor':
                            # look for the sub command in 'command' in tool_input
                            command = tool_input['command']
                            print(f"> {command} {tool_input['path']}")
                            if command == "view":
                                result = call_tools_service("view", start_dir, tool_input)
                            elif command == "create":
                                result = call_tools_service("create", start_dir, tool_input)
                            elif command == "str_replace":
                                result = call_tools_service("str_replace", start_dir, tool_input)
                            elif command == "insert":
                                result = call_tools_service("insert", start_dir, tool_input)
                            elif command == "undo_edit":
                                result = call_tools_service("undo_edit", start_dir, tool_input)
                        if message.name == "bash":
                            print(f"> {tool_input['command']}")
                            result = call_tools_service("bash", start_dir, tool_input)
                        message_history.append(
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": message.id,
                                        "content": result,
                                    }
                                ],
                            }
                        )
                    except requests.HTTPError as e:
                        print(f"HTTP error occurred: {e}")
                    except Exception as e:
                        print(f"An error occurred: {e}")

        if response.stop_reason in ["end_turn", "max_tokens", "stop_sequence"]:
            print("Stopped: ", response.stop_reason)
            print(response.content[0].text)
            done = True
            global_history.append(
                {"role": "assistant", "content": response.content[0].text}
            )


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"

    with open("yamls/" + config_path, "r") as f:
        config = yaml.safe_load(f)

    repo_path = config["repo_path"]
    input_goal = config["input_goal"]

    if config.get("include_files", True):
        input_goal += f"""

Here's a list of the existing files in the project:
{call_tools_service('list_directory', repo_path, {'path': '.', 'depth': 6})}

Review the existing files and create or update files as needed to execute the goal.
"""
    # if we have an arg that says --cli, skip the first process_goal call
    if "--cli" not in sys.argv:
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
