import time
import sys
import msvcrt
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
from rich.console import Console
from rich.status import Status
from rich.text import Text

client = OpenAI(api_key="PLACE YOUR API KEY HERE")

console = Console()
console.print("Welcome", style="bold green")
time.sleep(1)
console.print("Client Initialized", style="bold green")
time.sleep(1)


# Display spinner animation on first boot
with console.status("[bold blue]Booting...[/bold blue]", spinner="dots12"):
    assistant = client.beta.assistants.create(
        instructions="You are a weather bot. Use the provided functions to answer questions.",
        model="gpt-4o",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_current_temperature",
                    "description": "Get the current temperature for a specific location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g., San Francisco, CA"
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["Celsius", "Fahrenheit"],
                                "description": "The temperature unit to use. Infer this from the user's location."
                            }
                        },
                        "required": ["location", "unit"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_rain_probability",
                    "description": "Get the probability of rain for a specific location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g., San Francisco, CA"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
    )
    time.sleep(4)
console.print("Boot successful", style="bold green")

class EventHandler(AssistantEventHandler):
    @override
    def on_event(self, event):
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id
            self.handle_requires_action(event.data, run_id)
        elif event.event == 'thread.message.delta':
            sys.stdout.write(event.data.delta.content[0].text.value)
            sys.stdout.flush()
        elif event.event == 'thread.message.completed':
            sys.stdout.write('\r' + event.data.content[0].text.value)
            sys.stdout.flush()
        elif event.event == 'thread.run.completed':
            print("")

    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "get_current_temperature":
                tool_outputs.append({"tool_call_id": tool.id, "output": "57"})
            elif tool.function.name == "get_rain_probability":
                tool_outputs.append({"tool_call_id": tool.id, "output": "0.06"})

        # Submit all tool_outputs at the same time
        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        # Use the submit_tool_outputs_stream helper
        with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()  # DO NOT CHANGE THIS


def message_assistant(thread_id, message):
    # make sure this prints on same line as the helper function
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message,
    )
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant.id,
        event_handler=EventHandler()
    ) as stream:
        stream.until_done()

thread = client.beta.threads.create()
# console.print("Thread created for session", style="bold blue")

def show_help():
    console.print("Available commands:", style="bold yellow")
    console.print("/bye - Exit the chat", style="bold cyan")
    console.print("/clear - Clear the console", style="bold cyan")
    console.print("/help - Show this help message", style="bold cyan")

def custom_input(prompt, placeholder):
    console.print(prompt, end="", style="bold blue")
    console.print(placeholder, end="", style="dim")
    input_text = ""
    placeholder_displayed = True
    while True:
        ch = msvcrt.getch()
        if ch in (b'\r', b'\n'):
            break
        if ch == b'\x08':  # Backspace
            if len(input_text) > 0:
                input_text = input_text[:-1]
                sys.stdout.write('\b \b')
        elif ch == b'\x03':  # Ctrl+C
            console.print("\nGoodbye!", style="bold green")
            sys.exit(0)
        else:
            if placeholder_displayed:
                sys.stdout.write('\b' * len(placeholder) + ' ' * len(placeholder) + '\b' * len(placeholder))
                placeholder_displayed = False
            try:
                input_text += ch.decode()
                sys.stdout.write(ch.decode())
            except UnicodeDecodeError:
                continue
    print()  # Move to the next line after input
    return input_text

while True:
    message = custom_input(">>> ", "Send a message (/? for help)")
    if message == "/bye":
        console.print("Goodbye!", style="bold green")
        break
    elif message == "/clear":
        console.clear()
    elif message == "/help" or message == "/?":
        show_help()
    else:
        message_assistant(thread.id, message)
