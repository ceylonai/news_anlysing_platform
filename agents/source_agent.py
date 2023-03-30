import asyncio
from ceylon import CeylonAIAgent

source_agent = CeylonAIAgent()


@source_agent.register("source_agent", number_of_agents=1)
class SourceAgent:

    def __init__(self):
        pass

    @source_agent.init()
    async def setup_method(self):
        pass

    @source_agent.background("source_reader")
    async def source_reader(self):
        while True:
            await asyncio.sleep(1)
            print("source_reader")
