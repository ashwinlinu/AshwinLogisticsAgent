from langchain_core.messages import HumanMessage
from app.ai.graph import graph

class AIService:

    async def generate_response(self, message: str) -> str:

        result = await graph.ainvoke(
            {
                "messages": [
                    HumanMessage(content=message)
                ]
            }
        )
        return result["messages"][-1].content

ai_service = AIService()