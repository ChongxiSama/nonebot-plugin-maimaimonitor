from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Config(BaseSettings):
    model_config = ConfigDict(extra='ignore')
    maimai_bot_client_id: str
    maimai_bot_private_key: str
    maimai_bot_display_name: str
    maimai_worker_url: str = "https://maiapi.chongxi.us"
