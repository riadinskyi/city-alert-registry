from contextlib import asynccontextmanager
import uvicorn

from fastapi import FastAPI
from api_v1 import router as api_v1_router
from core.middlewares.auth import AuthMiddleWare
from core.openapi import custom_openapi


@asynccontextmanager
async def lifespan(app: FastAPI):
    from core.tools.location.xsls_to_json import download_xlsx_and_parse_to_json

    await download_xlsx_and_parse_to_json()
    yield


app = FastAPI(lifespan=lifespan, version="1.0.0")

app.add_middleware(AuthMiddleWare)

app.include_router(api_v1_router)


app.openapi = lambda: custom_openapi(app=app)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
