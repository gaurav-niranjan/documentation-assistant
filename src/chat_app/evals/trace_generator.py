import csv
from pathlib import Path
from chat_app.evals.chatbot import rag, rag_chunks, system_prompt, user_prompt, llm_response

evals_dir = Path(__file__).resolve().parent
input_file = evals_dir / "queries.csv"
output_file = evals_dir / "traces.csv"

with open(input_file, mode='r', encoding="utf-8") as infile, \
open(output_file, mode='w', encoding="utf-8") as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    writer.writerow(["Query Topic", "User Query", "History", "AI Response"])

    for row_index, row in enumerate(reader):
        query_topic = row[0]
        user_input = row[1]
        rag_chunks.clear()
        rag(user_input, rag_chunks)
        history = [
            system_prompt(),
            {"role": "assistant", "content": "How can I help you today?"},
            user_prompt(user_input)
        ]
        response = llm_response(history)

        writer.writerow([query_topic, user_input, str(history), str(response.choices[0].message.content)])
        print(f"query {row_index} completed")

