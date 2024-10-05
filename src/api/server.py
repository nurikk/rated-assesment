from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.routers.stats import customers_router
from common import db
from models import Base


@asynccontextmanager
async def lifespan(_: FastAPI):
    engine = db.get_engine()
    Base.metadata.create_all(engine)
    yield


def get_application() -> FastAPI:
    _app = FastAPI(lifespan=lifespan)

    _app.include_router(customers_router)
    return _app


app = get_application()

if __name__ == "__main__":
    uvicorn.run("api.server:app", reload=True)
