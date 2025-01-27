from typing import Annotated

from pydantic import computed_field, AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", cli_parse_args=True)

    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    vk_access_token: str
    vk_api_version: str

    tg_access_token: str
    tg_chat_id: int

    local_report_path: str
    dry_run: Annotated[bool, Field(alias="d")] = False  # CLI argument

    @computed_field  # type: ignore[prop-decorator]
    @property
    def db_uri(self) -> str:
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
