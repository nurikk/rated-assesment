from tortoise import Tortoise

from src.common.settings import get_settings

settings = get_settings()
TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["src.models"],
            "default_connection": "default",
        }
    }
}


async def init():
    await Tortoise.init(config=TORTOISE_ORM)
    # await Tortoise.generate_schemas()
