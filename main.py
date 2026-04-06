"""Project entrypoint for the ai-agent document indexing pipeline."""
from ingest import index_data
import os
from dotenv import load_dotenv
from search_agent import init_agent
import logs
import asyncio
load_dotenv()
def initialize_index():
    print("Chargement...")
    index = index_data(
        repo_owner="langchain-ai",
        repo_name="langchain",
        branch="master")
    return index

def initialize_agent(index):
    print("Initialisation de l'agent...")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Set it before running the agent.")
    agent = init_agent(
        index=index,
        api_key=api_key)
    return agent

async def main():
    """Display available module entrypoints for each pipeline stage."""
    index = initialize_index()
    agent = initialize_agent(index)
    print("\nPrêt pour répondre à vos questions!")
    print("Saisissez 'stop' pour sortir du programme.\n")

    while True:
        question = input("Votre question: ")
        if question.strip().lower() == 'stop':
            print("Goodbye!")
            break

        print("Analyse de votre question...")
        result = await agent.run(question)
        logs.log_interaction_to_file(logs.log_entry(
            agent_name=agent.name,
            system_prompt=agent.instructions,
            model_name=agent.model.model_name,
            question=question,
            answer=result.response.text,
            search_results="N/A",
            source="user"
        ))
        

        print("\n" + "="*50 + "\n")
    


if __name__ == "__main__":
    asyncio.run(main())
