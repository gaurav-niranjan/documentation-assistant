import os
import re
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

rag_chunks = {}

def rag(user_input, manual_name, rag_chunks):

    rag_chunks.clear()
    manual_names = ["lavafox", "birdmail", "openMRS", "paintscape", "blogpress"]

    results = dense_index.search(
        namespace="all-gross",
        query={
            "top_k": 3,
            "inputs": {
                "text": user_input
            },
            **({"filter": {"manual": manual_name}} \
               if manual_name in manual_names else {})
        }
    )

    for hit in results['result']['hits']:
        fields = hit.get('fields')
        chunk_text = fields.get('chunk_text')
        rag_chunks[hit['id']] = chunk_text


def system_prompt():
    return {
        "role": "developer",
        "content": f"""
        <overview>
        You are an AI customer support technician who is knowledgeable about software products created by the company called GROSS.
        The products are:
        * Lavafox, a web browser.
        * Birdmail: an email client.
        * OpenMRS: an electronic medical record system.
        * Paintscape: a drawing tool for creating and editing SVGs.
        * Blogpress: a content management system.

        You represent GROSS, and you are having a conversation with a human user who needs
        technical support with at least one of these GROSS products.
        </overview>

        You have access to certain excerpts of GROSS products' documentation that is pulled from a RAG system.
        Use this info (and no other info) to advise the user.
        
        <instructions>
        * When helping troubleshoot a user's issue, ask a proactive question to help determine what exactly the issue is.
        * In particular, it may not be clear from the user which GROSS software they're referring to. In this case, proactively ask them which
        software they're using. 
        * When asking proactive follow-up questions, ask exactly one question at a time.
        * Do not mention the terms "documentation excerpts" or "excerpts" in your response.
        * Do not use your general knowledge to answer a user query. Only use the <documentation> provided
        below to advise the user.
        * If you cannot find any advice for the user based on the excerpts, simply apologize and say that
        you do not know how to help the user this time.
        * Before you state any point other than a question, think carefully: which excerpt id does the advice come from?
        Use a special double-brackets notation before your advice to indicate the excerpt id that the advice comes from.

        For example:
        <example>
        [[lavafox-chunk-30]]
        Since the Site Identity Button is gray and you are seeing "Your connection is not secure" on all sites, this indicates that Lavafox
        is not able to establish secure (encrypted) connections. Normally, the Site Identity Buton will be blue or green
        for secures sites, showing that the connection is encrypted and the sit's identity is verified.
        </example>

        If you mention multiple points, use this notation BEFORE EACH POINT.
        For example:
        <example_response>
        [[lavafox-chunk-7]]
        1. Make sure your Lavafox security preferences have not been changed. The Phishing and Malware Protection feature should be enabled by default
        and helps with secure connections. \\n

        [[flamehamster-chunk-8]]
        2. Check if your Flamehamster browser is up to date.
        Older versions might not properly recognize extended validation
        certificates that sites like PayPal use. \\n
        </example_response>
        </instructions>
        
        Here are the documentation excerpts from the GROSS product manuals:
        <documentation>{rag_chunks}</documentation>
        
        Lastly, here are some final instructions:
        <final_instructions>
        * After mentioning any [[citation id]], pause and reflect on the citation id you have cited. Are
        you about to mention something not found in the citation?
        YOU ARE INSTRUCTED NOT TO MENTION ANY ADVICE NOT FOUNF IN THE DOCUMENTATION!!!
        * If the user suggests something not found in the above <documentation>, you should politely reject the user's point.
        * If your advice does not remian faithful to the <documentation>, I WILL LOSE MY JOB!!! PLEASE REMIAN FAITHFUL!
        </final_instructions>"""
    }

def user_prompt(user_input):
    return {
        "role": "user",
        "content": user_input
    }

def llm_response(prompt):
    response = llm.chat.completions.create(
        model = "gemini-3.5-flash-lite",
        temperature=0,
        messages=prompt,
    )

    return response

def expand_query(conversation):
    response = llm.chat.completions.create(
        model="gemini-3.1-flash-lite",
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": f"""Rewrite, in an expanded way, what the user means to say 
                in their final prompt of the following conversation: {conversation}"""
            }
        ]
    )

    return response.choices[0].message.content

def classify_manual(conversation):
    response = llm.chat.completions.create(
        model = "gemini-3.1-flash-lite",
        temperature=0,
        messages = [
            {
                "role": "user",
                "content": f"""Classify which software product the user is referring to in their
                final prompt of the following coversation. Your output should be limited to 
                one of the following choices" [lavafox, birdmail, openMRS, paintscape, blogpress, unsure].
                The option for unsure should be used only if you're not certain which software the user is
                referring to. Output just a single word from the list, nothing else. Here is the conversation: {conversation}"""
            }
        ]
    )

    return response

def remove_bracket_tags(text):
    return re.sub(r'\[\[.*?\]\]\s*(\r?\n)?', '', text)

if __name__ == "__main__":
    print(f"Assistant: How can I help you today?\n")
    user_input = input("\nUser: ")
    history = [
        system_prompt(),
        {"role": "assistant", "content": "How can I help you today?"}
    ]

    while user_input != "exit":
        expanded_query = expand_query(history[1:] + [user_prompt(user_input)])
        manual_name = classify_manual(history[1:] + [user_prompt(user_input)])
        rag(expanded_query, manual_name, rag_chunks)
        history[0] = system_prompt()  #Rewrite the system prompt 
        history.extend([user_prompt(user_input)])
        response = llm_response(history)

        print(f"\nAssistant: {response.choices[0].message.content}\n")

        history.extend([{"role": "assistant", "content": response.choices[0].message.content}])

        user_input = input("\nUser:")