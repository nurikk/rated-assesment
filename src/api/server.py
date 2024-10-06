import uvicorn
from fastapi import FastAPI

from api.routers.stats import customers_router


def get_application() -> FastAPI:
    _app = FastAPI()

    _app.include_router(customers_router)
    return _app


app = get_application()

if __name__ == "__main__":
    uvicorn.run("api.server:app", reload=True)
