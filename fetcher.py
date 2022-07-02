import argparse
from datetime import datetime, timedelta
from functools import reduce
import json
import requests
import time

from configobj import ConfigObj
import vk
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from community import Community
from post import Post
from utils import get_max_str_length, get_max_formatted_number_length, set_differences


class Fetcher:
    SECONDS_IN_DAY = 86400
    TO_TIME = round(time.time()) - SECONDS_IN_DAY
    FROM_TIME = TO_TIME - SECONDS_IN_DAY

    def __init__(self, args):
        self.args = args
        self.properties = ConfigObj('properties')
        
        self.report_output = 'output.txt'
        self.chat_id = self.properties["conversation_id"]
        
        # init vk api object
        vk_session = vk.Session(access_token=self.properties['access_token'])
        self.vk_api = vk.API(vk_session, v=self.properties['vk_api_v'], timeout=10000)

        # init db session
        engine = create_engine(f'postgresql+psycopg2://{self.properties["db_user"]}:{self.properties["db_password"]}@{self.properties["db_host"]}:{self.properties.as_int("db_port")}/{self.properties["db_name"]}')
        self.db_session = sessionmaker(bind=engine)()

        # init telegram
        self.tg_url_prefix = f'https://api.telegram.org/bot{self.properties["telegram_token"]}/sendMediaGroup'
        self.tg_url_prefix_single = f'https://api.telegram.org/bot{self.properties["telegram_token"]}/sendPhoto'

    def put_header(self):
        with open(self.report_output, 'a') as f:
            f.write('\n\n')
            f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            f.write('\n\n')

    def report(self, posts, community):
        if not posts:
            return

        posts = posts[:20]

        num_width = 4 if len(posts) > 10 else 3
        url_width = get_max_str_length(posts, 'url')
        views_length = get_max_formatted_number_length(posts, 'views')
        likes_length = get_max_formatted_number_length(posts, 'likes')
        reposts_length = get_max_formatted_number_length(posts, 'reposts')
        popularity_length = get_max_str_length(posts, 'popularity')

        views_d_length = get_max_formatted_number_length(posts, 'views_diff')
        likes_d_length = get_max_formatted_number_length(posts, 'likes_diff')
        reposts_d_length = get_max_formatted_number_length(posts, 'reposts_diff')
        popularity_d_length = get_max_formatted_number_length(posts, 'popularity_diff')

        with open(self.report_output, 'a') as f:
            f.write(f'{community.name} [{len(posts)}] -- {community.avg_views} views, {community.avg_likes} likes, {community.avg_reposts} reposts, {community.avg_popularity} popularity.\n')
            for i, post in enumerate(posts):
                if i == 20:
                    f.write("\n\n")
                    break

                f.write(f'{i+1:<{num_width}} {post.url:<{url_width}} | {post.views:<{views_length}} views ({post.views_diff:<+{views_d_length}.2f}) | {post.likes:<{likes_length}} likes ({post.likes_diff:<+{likes_d_length}.2f}) | {post.reposts:<{reposts_length}} reposts ({post.reposts_diff:<+{reposts_d_length}.2f})   Popularity: {post.popularity:<{popularity_length}} ({post.popularity_diff:<+{popularity_d_length}.2f})\n')
            f.write("\n\n")

    def report_to_tg(self, worthy_posts):
        for post in worthy_posts:
            msg = []
            for a in filter(lambda a_: 'photo' in a_, post.attachments):
                obj = {'type': 'photo', 'media': max(a['photo']['sizes'], key=lambda sz: sz['height'])['url']}
                msg.append(obj)
            if msg:
                caption = str(post)
                if len(msg) == 1:
                    response = requests.get(self.tg_url_prefix_single, params={
                        'chat_id': self.chat_id,
                        'photo': msg[0]['media'],
                        'caption': caption,
                        'disable_notification': True
                    })

                else:
                    msg[0]['caption'] = caption
                    print(msg)
                    response = requests.get(self.tg_url_prefix, params={
                        'chat_id': self.chat_id,
                        'media': json.dumps(msg),
                        'disable_notification': True
                    })
                time.sleep(0.5)

    def fetch(self):
        communities = self.db_session.query(Community).filter(Community.active == True)
        if not self.args.dry_run:
            communities = communities.filter(or_(Community.last_fetched is None, (datetime.now() - timedelta(seconds=Fetcher.SECONDS_IN_DAY)) > Community.last_fetched))
            self.put_header()
        
        for community in communities:
            worthy_posts = sorted(self.fetch_community(community), key=lambda x: x.popularity)
            self.report_to_tg(worthy_posts)
            if not self.args.dry_run:
                self.report(worthy_posts, community)

    def fetch_community(self, community):
        seen = 0
        print(community.name)
        outdated = False
        post_objects = []
        
        while not outdated:
            response = self.vk_api.wall.get(domain=community.id, count=100, offset=seen)
            posts = response["items"]
            if not posts:
                break

            seen += len(posts)
            for post in filter(lambda p: not (
                            ('is_pinned' in p and p['is_pinned'] == 1) or
                            p['date'] > Fetcher.TO_TIME or
                            'views' not in p or
                            p['marked_as_ads'] != 0), posts):

                if post['date'] < Fetcher.FROM_TIME:
                    outdated = True
                    break

                post = Post(
                    id=post["id"],
                    text=post["text"],
                    likes=post["likes"]["count"],
                    reposts=post["reposts"]["count"],
                    date=post["date"],
                    views=post["views"]["count"],
                    url=f'https://vk.com/wall{post["from_id"]}_{post["id"]}',
                    is_pinned=post.get("is_pinned", 0),
                    attachments=post["attachments"] if 'attachments' in post else []
                )

                post_objects.append(post)

        worthy_posts = list(filter(lambda p: p.is_worthy(community), post_objects))
        set_differences(community, post_list=worthy_posts)
        print(len(worthy_posts), 'posts found!')

        if len(post_objects) > 0:
            parsed = len(post_objects)
            community.avg_views = round((community.avg_views * community.parsed + reduce(lambda x, y: x + y.views, post_objects, 0)) / (community.parsed + parsed), 2)
            community.avg_likes = round((community.avg_likes * community.parsed + reduce(lambda x, y: x + y.likes, post_objects, 0)) / (community.parsed + parsed), 2)
            community.avg_reposts = round((community.avg_reposts * community.parsed + reduce(lambda x, y: x + y.reposts, post_objects, 0)) / (community.parsed + parsed), 2)
            community.avg_popularity = round(community.avg_views / community.avg_likes, 2)
            community.posts_day = round((community.posts_day * community.days + parsed) / (community.days + 1), 2)
            community.parsed += parsed
            community.days += 1
        community.last_fetched = datetime.now()
        if not self.args.dry_run:
            self.db_session.commit()

        return worthy_posts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dry_run",
                        action="store_true")
    args = parser.parse_args()

    fetcher = Fetcher(args)
    fetcher.fetch()
    fetcher.db_session.close()


if __name__ == '__main__':
    main()
