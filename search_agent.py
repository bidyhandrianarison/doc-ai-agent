
from pydantic_ai import Agent 
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from search_tools import SearchTool
SYSTEM_PROMPT_TEMPLATE = """
You are a helpful assistant for the technical documentation of langchain.

Use the search tool when necessary.
Base your answers on retrieved documents.
"""

def init_agent(index, api_key):
    """Initialize an agent with the given index and repository information."""
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format()
    search_tool = SearchTool(index)
    agent = Agent(
        name="doc_agent",
        instructions=system_prompt,
        model=GroqModel(
            model_name="llama-3.3-70b-versatile",
            provider=GroqProvider(api_key=api_key),
        ),
        tools=[search_tool.search]
    )
    return agent