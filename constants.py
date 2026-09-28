import os 
from dotenv import load_dotenv
load_dotenv()

class ENV_VARS:
    app_version = os.getenv("APP_VERSION")