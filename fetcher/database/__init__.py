from fetcher.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(settings.db_uri)
Session = sessionmaker(bind=engine)
