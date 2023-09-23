from configobj import ConfigObj

from helpers import _create_engine
from model.community import Community
from model.post import Post

properties = ConfigObj('../properties')
engine = _create_engine(properties)


if __name__ == '__main__':
    Community.__table__.create(engine, checkfirst=True)
    Post.__table__.create(engine, checkfirst=True)
