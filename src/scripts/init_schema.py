from common.db import get_engine
from models import Base

if __name__ == "__main__":
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("All tables created")
