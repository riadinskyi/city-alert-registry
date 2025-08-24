import uvicorn

from fastapi import FastAPI
from api_v1 import router as api_v1_router

app = FastAPI(version="0.0.1")

app.include_router(api_v1_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
