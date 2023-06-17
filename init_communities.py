import json

from sqlalchemy.orm import sessionmaker

from helpers import _create_engine
from model.community import Community

if __name__ == "__main__":
    with open("communities.json", "r") as f:
        communities = json.load(f)

    engine = _create_engine()
    db_session = sessionmaker(bind=engine)()

    db_session.add_all([Community(**community) for community in communities["communities"]])
    db_session.commit()
    db_session.close()
