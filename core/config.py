import os
from pathlib import Path

from dotenv import load_dotenv
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION")
    FRONTEND_URL: str = os.getenv('FRONTEND_URL')

    # POSTGRES_USER : str = os.getenv("POSTGRES_USER")
    # POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    # POSTGRES_SERVER : str = os.getenv("POSTGRES_SERVER","localhost")
    # POSTGRES_PORT : str = os.getenv("POSTGRES_PORT",5432) # default postgres port is 5432
    # POSTGRES_DB : str = os.getenv("POSTGRES_DB","tdd")
    # DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")

    SECRET_KEY : str = os.getenv("SECRET_KEY")   
    # ALGORITHM = "HS256"                         
    # ACCESS_TOKEN_EXPIRE_MINUTES = 30  

    MAILER_PORT: int = os.getenv("MAILER_PORT")
    MAILER_DOMAIN: str = os.getenv("MAILER_DOMAIN")
    MAILER_USERNAME: str = os.getenv("MAILER_USERNAME")
    MAILER_PASSWORD: str = os.getenv("MAILER_PASSWORD")

settings = Settings()
