from dotenv import load_dotenv
from openai import OpenAI
import os
from pinecone import Pinecone
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

llm = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
client = genai.Client(api_key=api_key) #For getting token counts
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("gross-app")

assistant_message = "How can I help you today?"
print(f"Assistant: {assistant_message}\n")
user_input = input("\nUser: ")
history = [
    {
        "role": "developer",
        "content": f"""You are an AI customer support technician who is knowledgeable about software products created by the company called GROSS
        One such product is a web browser called lavafox."""
    },
    {
        "role": "assistant", "content": assistant_message
    },
]

while user_input != "exit":
    #RAG Step 1: Retrieve relevant chunks from vector DB:
    results = dense_index.search(
        namespace="lavafox",
        query={
            "top_k": 3,
            "inputs": {"text": user_input}
        }
    )

    #RAG Step 2: Convert chunks into one long string of documentation:
    documentation = ""
    for hit in results['result']['hits']:
        fields = hit.get('fields')
        chunk_text = fields.get("chunk_text")
        documentation += chunk_text

    #RAG Step 3: Insert retireved documentation into prompt
    history.extend([
        {
            "role": "user",
            "content": f"""Here are excerpts from the official lavafox web browser documentation: {documentation}.
            Use whatever info from the above documentation excerpts (and no other info) to answer the follwoing query: {user_input}"""
        }
    ])

    response = llm.chat.completions.create(
        model = "gemini-3.1-flash-lite",
        temperature=0,
        messages=history,
    )

    print(f"\nAssistant: {response.choices[0].message.content}")

    history.extend([
        {"role": "assistant", "content": response.choices[0].message.content}
    ])

    user_input = input("\nUser: ")