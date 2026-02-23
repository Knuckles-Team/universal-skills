import asyncio
from pydantic_ai import Agent
from agent_skills import add_skills_to_agent

async def main():
    try:
        agent = Agent('test')
        agent = add_skills_to_agent(agent, "universal_skills/skills")
        print(f"Successfully loaded skills. Total tools: {len(agent.tools)}")
    except Exception as e:
        print(f"Failed to load skills: {e}")

if __name__ == "__main__":
    asyncio.run(main())
