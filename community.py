from sqlalchemy import Column, Text, Integer, REAL, TEXT, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Community(Base):
    __tablename__ = 'communities'

    id = Column(TEXT, primary_key=True)
    name = Column(TEXT)
    parsed = Column('parsed', Integer, default=0)
    posts_day = Column('posts_day', REAL, default=0.0)
    active = Column('active', Boolean, default=True)
    days = Column('days', Integer, default=0)
    avg_views = Column('avg_views', REAL, default=0.0)
    avg_likes = Column('avg_likes', REAL, default=0.0)
    avg_reposts = Column('avg_reposts', REAL, default=0.0)
    avg_popularity = Column('avg_popularity', REAL, default=0.0)
    last_fetched = Column('last_fetched', DateTime)

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.parsed = 0.0
        self.posts_day = 0.0
        self.active = True
        self.days = 0
        self.avg_views = 0.0
        self.avg_likes = 0.0
        self.avg_reposts = 0.0
        self.avg_popularity = 0.0
        self.last_fetched = None

    def __repr__(self):
        return f'id: {self.id},\nname: {self.name},\nparsed: {self.parsed},\n'\
               f'average views per day: {self.avg_views}\n' \
               f'average likes per day: {self.avg_likes}\n' \
               f'average reposts per day: {self.avg_reposts}\n' +\
               '-' * 30 + '\n'
