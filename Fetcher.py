from datetime import datetime
import time

from configobj import ConfigObj
import vk
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Community import Community
from post import Post


def get_api_obj():
    properties = ConfigObj('properties')
    vk_session = vk.Session(access_token=properties['access_token'])

    print(properties['vk_api_v'])
    print(type(properties['vk_api_v']))
    return vk.API(vk_session, v=properties['vk_api_v'], timeout=10000)


def get_db_session():
    properties = ConfigObj('properties')
    engine = create_engine(f'postgresql+psycopg2://{properties["db_user"]}:{properties["db_password"]}@{properties["db_host"]}:{properties.as_int("db_port")}/{properties["db_name"]}')
    Session = sessionmaker(bind=engine)

    return Session()


def set_difference(community, post=None, post_list=None):
    if post_list is not None:
        for post in post_list:
            set_difference(community, post=post)
    else:
        post.views_diff = round(post.views - community.avg_views, 2)
        post.likes_diff = round(post.likes - community.avg_likes, 2)
        post.reposts_diff = round(post.reposts - community.avg_reposts, 2)
        post.popularity_diff = round(post.popularity - community.avg_popularity, 2)


def put_header():
    with open('output.txt', 'a') as f:
        f.write('\n\n')
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        f.write('\n\n')


def report(posts, community):
    if not posts:
        return

    posts = sorted(posts, key=lambda x: x.popularity)
    posts = posts[:20]
    set_difference(community, post_list=posts)

    num_width = 4 if len(posts) > 10 else 3
    url_width = max([len(post.url) for post in posts])
    views_length = max([len(str(post.views)) for post in posts])
    likes_length = max([len(str(post.likes)) for post in posts])
    reposts_length = max([len(str(post.reposts)) for post in posts])
    popularity_length = max([len(str(post.popularity)) for post in posts])

    views_d_length = max([len(format(post.views_diff, '+.2f')) for post in posts])
    likes_d_length = max([len(format(post.likes_diff, '+.2f')) for post in posts])
    reposts_d_length = max([len(format(post.reposts_diff, '+.2f')) for post in posts])
    popularity_d_length = max([len(format(post.popularity_diff, '+.2f')) for post in posts])

    with open('output.txt', 'a') as f:
        f.write(f'{community.name} [{len(posts)}] -- {community.avg_views} views, {community.avg_likes} likes, {community.avg_reposts} reposts, {community.avg_popularity} popularity.\n')
        for i, post in enumerate(posts):
            if i == 20:
                f.write("\n\n")
                break

            f.write(f'{i+1:<{num_width}} {post.url:<{url_width}} | {post.views:<{views_length}} views ({post.views_diff:<+{views_d_length}.2f}) | {post.likes:<{likes_length}} likes ({post.likes_diff:<+{likes_d_length}.2f}) | {post.reposts:<{reposts_length}} reposts ({post.reposts_diff:<+{reposts_d_length}.2f})   Popularity: {post.popularity:<{popularity_length}} ({post.popularity_diff:<+{popularity_d_length}.2f})\n')
        f.write("\n\n")


def daily_fetch(api, db_session):
    put_header()
    SECONDS_IN_DAY = 86400
    TO_TIME = round(time.time()) - SECONDS_IN_DAY
    FROM_TIME = TO_TIME - SECONDS_IN_DAY

    for community in db_session.query(Community)\
                               .filter(Community.active == True):
        print(community.id)

        seen = 0
        parsed = 0
        views = 0
        likes = 0
        reposts = 0
        outdated = False
        worthy_posts = []
        while not outdated:
            print(seen)
            response = api.wall.get(domain=community.id, count=100, offset=seen)
            print('OK!')
            posts = response["items"]
            if not posts:
                break

            seen += len(posts)

            for post in posts:
                if ('is_pinned' in post and post['is_pinned'] == 1) or post['date'] > TO_TIME:
                    continue

                if post['date'] < FROM_TIME:
                    outdated = True
                    break

                if 'views' not in post:
                    print(f'{post["id"]}{post["from_id"]} has no views attribute')
                    continue

                post = Post(
                    id=post["id"],
                    text=post["text"],
                    likes=post["likes"]["count"],
                    reposts=post["reposts"]["count"],
                    date=post["date"],
                    views=post["views"]["count"],
                    url=f'https://vk.com/wall{post["from_id"]}_{post["id"]}',
                    is_pinned=post.get("is_pinned", 0)
                )

                parsed += 1
                if post.views > community.avg_views or\
                   post.likes > community.avg_likes or\
                   post.reposts > community.avg_reposts or\
                   post.popularity < community.avg_popularity:
                    worthy_posts.append(post)

                views += post.views
                likes += post.likes
                reposts += post.reposts

        if parsed > 0:
            community.avg_views = round((community.avg_views * community.parsed + views) / (community.parsed + parsed), 2)
            community.avg_likes = round((community.avg_likes * community.parsed + likes) / (community.parsed + parsed), 2)
            community.avg_reposts = round((community.avg_reposts * community.parsed + reposts) / (community.parsed + parsed), 2)
            community.avg_popularity = round(community.avg_views / community.avg_likes, 2)
            community.posts_day = round((community.posts_day * community.days + parsed) / (community.days + 1), 2)
            community.parsed += parsed
            community.days += 1
            db_session.commit()

        report(worthy_posts, community)


def main():
    api = get_api_obj()
    db_session = get_db_session()
    daily_fetch(api, db_session)
    db_session.close()


if __name__ == '__main__':
    main()
