from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import RegisterTortoise

from api.routers.stats import customers_router
from common.db import TORTOISE_ORM
from models import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(customers_router)

if __name__ == "__main__":
    uvicorn.run("api.server:app", reload=True)
