print("SCRIPT STARTED")

from app.ai.client import client
from app.config.settings import settings

print("CLIENT IMPORTED")
print("DEPLOYMENT:", settings.azure_openai_deployment)


def main():
    print("ENTERING MAIN")

    response = client.responses.create(
        model=settings.azure_openai_deployment,
        input="Say hello from Ashwin Logistics in one sentence.",
        max_output_tokens=500,
    )
    print("OUTPUT TEXT:")
    print(repr(response.output_text))


if __name__ == "__main__":
    main()