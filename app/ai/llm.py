from langchain_openai import ChatOpenAI

from app.ai.client import token_provider
from app.config.settings import settings


llm = ChatOpenAI(
    model=settings.azure_openai_deployment,
    base_url=f"{settings.azure_openai_endpoint.rstrip('/')}/openai/v1/",
    api_key=token_provider,
)