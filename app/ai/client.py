from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AsyncOpenAI

from app.config.settings import settings


credential = DefaultAzureCredential()

_sync_token_provider = get_bearer_token_provider(
    credential,
    "https://cognitiveservices.azure.com/.default",
)


async def token_provider():
    return _sync_token_provider()


client = AsyncOpenAI(
    base_url=f"{settings.azure_openai_endpoint.rstrip('/')}/openai/v1/",
    api_key=token_provider,
)