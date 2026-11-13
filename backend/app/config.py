import os
from dotenv import load_dotenv

load_dotenv()  # busca el .env subiendo por las carpetas


class Settings:
    cr_api_key: str = os.getenv("CR_API_KEY", "")


settings = Settings()