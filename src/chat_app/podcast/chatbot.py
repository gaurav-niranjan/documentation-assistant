import json
import os
from datetime import date

from dotenv import load_dotenv
from google import genai

from chat_app.podcast.lm_tools import read_webpage, search_web, create_audio

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"
MAX_ROUNDS = 10  # safety limit so the tool loop can never run forever


# ---------- Tools (plain dictionaries, same shape as the docs) ----------
TOOLS = [
    {
        "type": "function",
        "name": "search_web",
        "description": "Searches the web on a query and retrieves an array of relevant URLs.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The query of the web search"}
            },
            "required": ["query"],
        },
    },
    {
        "type": "function",
        "name": "read_webpage",
        "description": "Accesses a webpage and obtains its text.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL of the webpage"}
            },
            "required": ["url"],
        },
    },
    {
        "type": "function",
        "name": "create_audio",
        "description": "Uses a Text-to-Speech model to convert a podcast script into a wav file named podcast.wav",
        "parameters": {
            "type": "object",
            "properties": {
                "script": {"type": "string", "description": "A podcast script read by a single host"}
            },
            "required": ["script"],
        },
    },
]

TOOL_FUNCTIONS = {
    "search_web": search_web,
    "read_webpage": read_webpage,
    "create_audio": create_audio,
}

SYSTEM_PROMPT = f"""Today's date is {date.today().strftime("%B %d, %Y")}.
You are a podcast producer, creating news-based and explainer podcasts for people on any topic they choose.
The podcast should be based on real facts and web reseach. As such, do not create any fictional information for
the podcast. Only use what you find based on your web research.

You have access to several specialized tools. Here are your tools:
<tools>
* With the search_web tool, you can search the web and retrieve URLs of relevant pages.
This is useful for current information and information you don't possess in your internal knowledge.
* With the read_webpage tool, you can read the text of any web page.
Use it together with search_web: search_web finds URLs, read_webpage reads them.
* With the create_audio tool, you can convert a podcast script into a wav file.
</tools>

Here is the plan you should follow step-by-step to create a podcast:
<plan>
1. When the user describes the podcast they want, do not create the podcast until you've obtained
the following information:
    * The topic of the podcast
    * How long the podcast should be. (For eg: five minutes long)
However, do not ask the user about the podcast style. Assume that the podcast style is a single host
reporting news and insight.
2. Next, use the search_web tool to find web page URLs that are relevant to the podcast topic.
This will return an array of URLs. Do not call search_web multiple times at once unless there is an error. After calling search_web
a single time successfully, move on to the next step.
3. Next, use the read_webpage tool on each URL to read the information contained within those web pages.
4. After reading the content of all web pages, determine whether you have enough revelant factual material
to fill a podcast of the user's desired length. 
5. If you do not have enough relevant material, go back to Step 2 to use the search_web tool again, this time on
a new web query you haven't searched previously.
6. If you have enough releavant material, you should then use the create_audio tool to create the podcast,
which will create a wav file called podcast.wav.
</plan>
"""


def ask_model(history):
    """Sends the WHOLE history every time. Nothing is saved on Google's server."""
    return client.interactions.create(
        model=MODEL,
        system_instruction=SYSTEM_PROMPT,
        input=history,
        tools=TOOLS,
        store=False,
    )


def run_tool(name, arguments):
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        return f"Unknown tool: {name}"
    try:
        return function(**arguments)
    except Exception as e:
        return f"Error while running {name}: {e}"


# ---------- Chat loop ----------
print("Assistant: How can I help you today?\n")
history = []
user_input = input("User: ")

while user_input != "exit":
    # 1. Add the user's message to the history
    history.append({
        "type": "user_input",
        "content": [{"type": "text", "text": user_input}],
    })

    for _ in range(MAX_ROUNDS):
        interaction = ask_model(history)

        print("---- model replied with", len(interaction.steps), "steps ----")
        for i, step in enumerate(interaction.steps):
            print(i, step.type, getattr(step, "name", ""))

        # 2. Add everything the model said or did, exactly as received
        for step in interaction.steps:
            history.append(step.model_dump())

        # 3. Find every tool the model wants to use
        calls = [step for step in interaction.steps if step.type == "function_call"]
        if not calls:
            break

        # 4. Run them all and add each result to the history
        for call in calls:
            print(call.name, call.arguments)
            output = run_tool(call.name, call.arguments)
            history.append({
                "type": "function_result",
                "name": call.name,
                "call_id": call.id,
                "result": [{"type": "text", "text": json.dumps(output, default=str)}],
            })

    print(f"\nAssistant: {interaction.output_text}\n")
    user_input = input("User: ")