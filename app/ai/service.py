from app.ai.client import client
from app.config.settings import settings


class AIService:

    async def generate_response(self, message: str) -> str:
        response = await client.responses.create(
            model=settings.azure_openai_deployment,
            input=message
        )

        if response.status != "completed":
            raise RuntimeError(
                f"Azure OpenAI response was not completed: "
                f"{response.status}"
            )

        return response.output_text


ai_service = AIService()