from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
import os
from dotenv import load_dotenv

load_dotenv()

project_endpoint = os.getenv('PROJECT_ENDPOINT')
search_endpoint = os.getenv('SEARCH_ENDPOINT')
index_name = os.getenv('INDEX_NAME')
agent_name  = os.getenv('AGENT_NAME')

project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential()
)

open_ai_client = project_client.get_openai_client()

search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=DefaultAzureCredential()
)

def ask(question):
    results = search_client.search(
        search_text=question,
        vector_queries=[
            VectorizableTextQuery(
                text = question,
                k_nearest_neighbors=3,
                fields='text_vector'
            )
        ],
        select=['chunk','title','parent_id'],
        top=3
    )

    source_list = []

    for result in results:
        title = result.get("title", "Unknown source")
        parent_id = result.get("parent_id", "")
        chunk = result.get("chunk", "")

        source_text = f"""
[Source title: {title}]
[Parent ID: {parent_id}]
{chunk}
"""
        source_list.append(source_text)        

    sources = "\n\n".join(source_list)

    # Step 3: Build the grounded prompt for the agent
    prompt = f"""
You are a customer support agent for CloudXeus Technology Services.

Answer the customer question using only the sources provided below.
If the sources do not contain enough information, say that the knowledge base does not contain enough information.

Sources:
{sources}

Customer question:
{question}
"""

    print("\nPrompt sent to agent:\n")
    print(prompt)

    response = open_ai_client.responses.create(
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "type": "agent_reference"
            }
        },
        input=prompt,
    )

    return response.output_text


print(ask("Can I get my money back?"))
