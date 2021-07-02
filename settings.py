from typing import List, Union, Optional

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    SERVER_NAME: str = "localhost"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Response Cache API"
    PROJECT_DESCRIPTION: str = "Cache responses from different API servers."
    PROJECT_VERSION: str = "0.0.1"

    API_KEYS: List[str] = []
    API_KEY_NAME: str = "api_key"

    @validator("API_KEYS", pre=True)
    def assemble_api_keys(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DATABASE: int = 0
    REDIS_PASSWORD: Optional[str]

    # AIOHTTP
    AIOHTTP_USERAGENT: str = f"response-cache-api ({PROJECT_VERSION})"

    class Config:
        case_sensitive = True


settings = Settings()
