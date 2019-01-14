import time

import psycopg2
from pprint import pprint
from configobj import ConfigObj
import vk
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Community import Community


def get_api_obj():
    properties = ConfigObj('properties')
    vk_session = vk.Session(access_token=properties['access_token'])

    return vk.API(vk_session, v=properties['vk_api_v'])


def get_db_session():
    properties = ConfigObj('properties')
    engine = create_engine(f'postgresql+psycopg2://{properties["db_user"]}:{properties["db_password"]}@{properties["db_host"]}:{properties.as_int("db_port")}/{properties["db_name"]}')
    Session = sessionmaker(bind=engine)

    return Session()


def add_community(api, db_session, id, name):
    community = Community(id=id, name=name, parsed=0, avg_views=0, avg_likes=0, avg_reposts=0,
                          avg_views_day=0, avg_likes_day=0, avg_reposts_day=0, posts_day=0, active=True)
    seen = 0
    while community.parsed < 500:
        response = api.wall.get(domain=community.id, count=100, offset=seen)

        posts = response["items"]
        if not posts:
            break

        seen += len(posts)

        for post in posts:
            if 'is_pinned' in post and post['is_pinned'] == 1:
                continue

            if 'views' not in post:
                print(f'{post["id"]}{post["from_id"]} has no views attribute')
                continue

            community.parsed += 1
            community.avg_views += (post['views']['count'] - community.avg_views) / community.parsed
            community.avg_likes += (post['likes']['count'] - community.avg_likes) / community.parsed
            community.avg_reposts += (post['reposts']['count'] - community.avg_reposts) / community.parsed

    community.avg_views = round(community.avg_views, 2)
    community.avg_likes = round(community.avg_likes, 2)
    community.avg_reposts = round(community.avg_reposts, 2)

    db_session.add(community)
    db_session.commit()
    db_session.close()


def main():
    SECONDS_IN_DAY = 86400
    TO_TIME = round(time.time()) - SECONDS_IN_DAY
    FROM_TIME = TO_TIME - SECONDS_IN_DAY

    api = get_api_obj()
    db_session = get_db_session()


if __name__ == '__main__':
    main()
