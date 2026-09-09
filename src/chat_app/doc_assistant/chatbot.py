import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
llm = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("gross-app")

def rag(user_input):
    results = dense_index.search(
        namespace="all-gross",
        query={
            "top_k": 3,
            "inputs": {
                "text": user_input
            }
        }
    )

    documentation = ""
    for hit in results['result']['hits']:
        fields = hit.get('fields')
        chunk_text = fields.get('chunk_text')
        documentation += chunk_text

    return documentation

def system_prmpt():
    return {
        "role": "developer",
        "content": """You are an AI customer support technician who is knowledgeable about software products created by the company called GROSS.
        The products are:
        * Lavafox, a web browser.
        * Birdmail: an email client.
        * OpenMRS: an electronic medical record system.
        * Paintscape: a drawing tool for creating and editing SVGs.
        * Blogpress: a content management system."""
    }

def user_prompt(user_input, documentation):
    return {
        "role": "user",
        "content": f"""Here are excerpts from the official GROSS product documentation: {documentation}.
        Use whatever info from the above documentation excerpts (and no other info)
        to answer the following query: {user_input}"""
    }

def llm_response(prompt):
    response = llm.chat.completions.create(
        model = "gemini-3.1-flash-lite",
        temperature=0,
        messages=prompt,
    )

    return response

if __name__ == "__main__":
    print(f"Assistant: How can I help you today?\n")
    user_input = input("\nUser: ")
    history = [
        system_prmpt(),
        {"role": "assistant", "content": "How can I help you today?"}
    ]

    while user_input != "exit":
        documentation = rag(user_input)
        history.extend([user_prompt(user_input, documentation)])
        response = llm_response(history)

        print(f"\nAssistant: {response.choices[0].message.content}\n")

        history.extend([{"role": "assistant", "content": response.choices[0].message.content}])

        user_input = input("\nUser:")