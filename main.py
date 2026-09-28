from fastapi import FastAPI
from constants import ENV_VARS


app = FastAPI()

__version__ = ENV_VARS.app_version


@app.get("/health")
async def health():
    return {f"Ashwin Logistics AI Support Agent running.... in version {__version__}"}


