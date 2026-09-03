from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

llm = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

with open("data_sources/lavafox.md", "r", encoding="utf-8") as f:
    documentation = f.read()

assistant_message = "How can I help you today?"
print(f"Assistant: {assistant_message}\n")
user_input = input("User: ")
history = [
    {
        "role": "developer",
        "content": f"""You are an AI customer support technician who is knowledgeable about software products created by the company called GROSS
        One such product is a web browser called lavafox.
        You are to answer user queries below solely on the following documentation: {documentation}"""
    },
    {
        "role": "assistant", "content": assistant_message
    },
    {
        "role": "user", "content": user_input
    },
]

while user_input != "exit":
    response = llm.chat.completions.create(
        model = "gemini-3.1-flash-lite",
        temperature=0,
        messages=history,
    )

    print(f"Assistant: {response.choices[0].message.content}")
    user_input = input("\nUser: ")
    history.extend([
        {"role": "assistant", "content": response.choices[0].message.content},
        {"role": "user", "content": user_input }
    ])