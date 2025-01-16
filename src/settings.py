from pydantic_settings import BaseSettings


class Settings(BaseSettings, env_file=".env"):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    vk_access_token: str
    vk_api_version: str

    tg_access_token: str
    tg_chat_id: int


settings = Settings()
