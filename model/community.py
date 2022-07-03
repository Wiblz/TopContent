from sqlalchemy import Column, Text, Integer, REAL, TEXT, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Community(Base):
    __tablename__ = 'communities'

    id = Column(TEXT, primary_key=True)
    name = Column(TEXT)
    posts_fetched = Column('posts_fetched', Integer, default=0)
    worthy_posts = Column('worthy_posts', Integer, default=0)
    avg_posts_per_day = Column('avg_posts_per_day', REAL, default=0.0)
    active = Column('active', Boolean, default=True)
    days = Column('days', Integer, default=0)
    ema_views = Column('ema_views', REAL, default=0.0)
    ema_likes = Column('ema_likes', REAL, default=0.0)
    ema_reposts = Column('ema_reposts', REAL, default=0.0)
    ema_popularity = Column('ema_popularity', REAL, default=0.0)
    last_fetched = Column('last_fetched', DateTime)

    last_avg_views = Column('last_avg_views', REAL, default=0.0)
    last_avg_likes = Column('last_avg_likes', REAL, default=0.0)
    last_avg_reposts = Column('last_avg_reposts', REAL, default=0.0)

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.posts_fetched = 0
        self.worthy_posts = 0
        self.avg_posts_per_day = 0.0
        self.active = True
        self.days = 0
        self.ema_views = 0.0
        self.ema_likes = 0.0
        self.ema_reposts = 0.0
        self.ema_popularity = 0.0
        self.last_fetched = None
        self.last_avg_views = 0.0
        self.last_avg_likes = 0.0
        self.last_avg_reposts = 0.0

    def __repr__(self):
        return f'id: {self.id},\nname: {self.name},\nposts_fetched: {self.posts_fetched},\n'\
               f'moving average of views per day: {self.ema_views}\n' \
               f'moving average of likes per day: {self.ema_likes}\n' \
               f'moving average of reposts per day: {self.ema_reposts}\n' +\
               '-' * 30 + '\n'
