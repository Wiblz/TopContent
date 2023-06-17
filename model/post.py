from sqlalchemy import Column, Text, INTEGER, DateTime, REAL, ForeignKey, BOOLEAN
from sqlalchemy.orm import declarative_base

from model.community import Community

Base = declarative_base()


class Post(Base):
    __tablename__ = 'posts'

    link = Column(Text, primary_key=True)
    community_id = Column(Text, ForeignKey(Community.id))

    views = Column(INTEGER, default=0)
    likes = Column(INTEGER, default=0)
    reposts = Column(INTEGER, default=0)
    popularity = Column(REAL, default=0.0)

    is_worthy = Column(BOOLEAN, default=False)
    fetched_on = Column(DateTime)
    posted_on = Column(DateTime)

    # def __init__(self, link, community_id):
    #     self.link = link
    #     self.community_id = community_id
    #     self.views = 0
    #     self.likes = 0
    #     self.reposts = 0
    #     self.popularity = 0.0
    #     self.is_worthy = False
    #     self.fetched_on = None
    #     self.posted_on = None
