from configobj import ConfigObj
from sqlalchemy import create_engine


def _create_engine(properties=None):
    if not properties:
        properties = ConfigObj('properties')

    return create_engine(
        f'postgresql+psycopg2://{properties["db_user"]}:{properties["db_password"]}@{properties["db_host"]}:{properties.as_int("db_port")}/{properties["db_name"]}')
