import uvicorn

from fastapi import FastAPI
from api_v1 import router as api_v1_router
from core.middlewares.auth import AuthMiddleWare
from core.openapi import custom_openapi

app = FastAPI()

# Register authentication middleware
app.add_middleware(AuthMiddleWare)

app.include_router(api_v1_router)


app.openapi = lambda :custom_openapi(app=app)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
