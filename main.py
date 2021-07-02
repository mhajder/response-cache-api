import urllib.parse
from typing import Optional

from aiohttp_client_cache import CachedSession, RedisBackend
from fastapi import FastAPI, Query, Request, HTTPException, Security, Depends, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import APIKey
from fastapi.security.api_key import APIKeyQuery, APIKeyHeader, APIKeyCookie
from pydantic import AnyHttpUrl

from settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url="/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

API_KEYS = settings.API_KEYS
API_KEY_NAME = settings.API_KEY_NAME

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)


async def get_api_key(
        api_key_query: str = Security(api_key_query),
        api_key_header: str = Security(api_key_header),
        api_key_cookie: str = Security(api_key_cookie),
):
    if bool(API_KEYS):
        if api_key_query in API_KEYS:
            return api_key_query
        elif api_key_header in API_KEYS:
            return api_key_header
        elif api_key_cookie in API_KEYS:
            return api_key_cookie
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated"
            )
    else:
        return True


@app.get("/api/v1/cache")
async def cache_get(*,
                    api_key: APIKey = Depends(get_api_key),
                    ttl: Optional[int] = Query(ge=-1, default=0),
                    url: AnyHttpUrl = Query(...),
                    response: Response,
                    ):
    async with CachedSession(cache=RedisBackend(cache_name='response-cache-get',
                                                address=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}',
                                                db=settings.REDIS_DATABASE, password=settings.REDIS_PASSWORD,
                                                expire_after=ttl, allowed_methods='GET'),
                             headers={"Connection": "keep-alive", "User-Agent": settings.AIOHTTP_USERAGENT}) as session:

        async with session.get(url=url, verify_ssl=False, timeout=10) as r:
            if r.headers['Content-Type'] == 'application/json':
                response.status_code = r.status
                return await r.json()
            else:
                response.status_code = r.status
                return await r.text()


@app.post("/api/v1/cache")
async def cache_post(*,
                     api_key: APIKey = Depends(get_api_key),
                     ttl: Optional[int] = Query(ge=-1, default=0),
                     url: AnyHttpUrl = Query(...),
                     post: Request = None,
                     response: Response,
                     ):
    async with CachedSession(cache=RedisBackend(cache_name='response-cache-post',
                                                address=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}',
                                                db=settings.REDIS_DATABASE, password=settings.REDIS_PASSWORD,
                                                expire_after=ttl, allowed_methods='POST'),
                             headers={"Connection": "keep-alive", "User-Agent": settings.AIOHTTP_USERAGENT}) as session:

        async with session.post(url=url, verify_ssl=False, timeout=10,
                                data=urllib.parse.parse_qs((await post.body()).decode())) as r:
            if r.headers['Content-Type'] == 'application/json':
                response.status_code = r.status
                return await r.json()
            else:
                response.status_code = r.status
                return await r.text()
