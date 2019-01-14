from sqlalchemy import Column, Text, Integer, REAL, TEXT, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Community(Base):
    __tablename__ = 'communities'

    id = Column(TEXT, primary_key=True)
    name = Column(TEXT)
    parsed = Column(Integer)
    avg_views = Column(REAL)
    avg_likes = Column(REAL)
    avg_reposts = Column(REAL)
    avg_views_day = Column(REAL)
    avg_likes_day = Column(REAL)
    avg_reposts_day = Column(REAL)
    posts_day = Column(Integer)
    active = Column(Boolean)

    def __repr__(self):
        return f'id: {self.id},\nname: {self.name},\nparsed: {self.parsed},\naverage views: ' \
               f'{self.avg_views}\naverage likes: {self.avg_likes}\naverage reposts: ' \
               f'{self.avg_reposts}\n\naverage views per day: ' \
               f'{self.avg_views_day}\naverage likes per day: ' \
               f'{self.avg_likes_day}\naverage reposts per day: {self.avg_reposts_day}\n' +\
               '-' * 30 + '\n'
