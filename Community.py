from sqlalchemy import Column, Text, Integer, REAL, TEXT, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Community(Base):
    __tablename__ = 'communities'

    id = Column(TEXT, primary_key=True)
    name = Column(TEXT)
    parsed = Column(Integer)
    posts_day = Column(REAL)
    active = Column(Boolean)
    days = Column(Integer)
    avg_views = Column(REAL)
    avg_likes = Column(REAL)
    avg_reposts = Column(REAL)
    avg_popularity = Column(REAL)

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

    def __repr__(self):
        return f'id: {self.id},\nname: {self.name},\nparsed: {self.parsed},\n'\
               f'average views per day: {self.avg_views}\n' \
               f'average likes per day: {self.avg_likes}\n' \
               f'average reposts per day: {self.avg_reposts}\n' +\
               '-' * 30 + '\n'
