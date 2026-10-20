from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
import os
from dotenv import load_dotenv

load_dotenv()
endpoint = os.getenv("PROJECT_ENDPOINT")
agent_name = os.getenv("AGENT_NAME")

SYSTEM_PROMPT = """
You are a customer support assistant.

Answer the customer's question using ONLY the provided sources.

After your answer, cite the source URL you used.

If the sources do not contain the answer, say:
"I don't have that information in the available knowledge base."

Never invent policies, prices, refund rules, or timelines.
"""

project = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential()
)

try:    
    agent = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model = "gpt-5-mini",
            instructions = SYSTEM_PROMPT
        )
    )
    
except Exception as e:
    print(f"exception details: {e}")