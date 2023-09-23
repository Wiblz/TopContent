import argparse
from datetime import datetime, timedelta
import json

import requests
import time

from configobj import ConfigObj
import vk
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from ema import EMA
from helpers import _create_engine
from model.community import Community
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
        self.vk_api = vk.API(access_token=self.properties['access_token'], v=self.properties['vk_api_v'], timeout=10000)

        # init db session
        engine = _create_engine(self.properties)
        self.db_session = sessionmaker(bind=engine)()

        # init telegram
        self.tg_url_prefix = f'https://api.telegram.org/bot{self.properties["telegram_token"]}/sendMediaGroup'
        self.tg_url_prefix_single = f'https://api.telegram.org/bot{self.properties["telegram_token"]}/sendPhoto'

    def fetch(self):
        communities = self.db_session.query(Community).filter(Community.active == True)
        worthy_posts = []
        if not self.args.dry_run:
            communities = communities.filter(or_(Community.last_fetched == None, (
                    datetime.now() - timedelta(seconds=Fetcher.SECONDS_IN_DAY)) > Community.last_fetched))

        for community in communities:
            posts = sorted(self.fetch_community(community), key=lambda x: -x.popularity)
            if posts:
                worthy_posts.append((posts, community))

        self.report_to_tg(worthy_posts)
        if not self.args.dry_run:
            self.report(worthy_posts)

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
                    community=community,
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

        worthy_posts = list(filter(lambda p: p.is_worthy(), post_objects))
        set_differences(community, post_list=worthy_posts)
        print(len(worthy_posts), 'posts found!')

        if len(post_objects) > 0:
            community.last_avg_views = sum(map(lambda p: p.views, post_objects)) / len(post_objects)
            community.last_avg_likes = sum(map(lambda p: p.likes, post_objects)) / len(post_objects)
            community.last_avg_reposts = sum(map(lambda p: p.reposts, post_objects)) / len(post_objects)

        community.ema_views = EMA(community.ema_views, community.last_avg_views)
        community.ema_likes = EMA(community.ema_likes, community.last_avg_likes)
        community.ema_reposts = EMA(community.ema_reposts, community.last_avg_reposts)
        if community.ema_views == 0 or community.ema_likes == 0:
            community.ema_popularity = 0.0
        else:
            community.ema_popularity = round(community.ema_likes / community.ema_views, 2)
        community.avg_posts_per_day = round(
            (community.avg_posts_per_day * community.days + len(post_objects)) / (community.days + 1), 2)
        community.posts_fetched += len(post_objects)
        community.worthy_posts += len(worthy_posts)
        community.days += 1
        community.last_fetched = datetime.now()
        if not self.args.dry_run:
            self.db_session.commit()

        return worthy_posts

    def put_header(self, f):
        f.write('\n\n')
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        f.write('\n\n')

    def report(self, fetched_posts):
        if not fetched_posts:
            return

        with open(self.report_output, 'a') as f:
            self.put_header(f)
            for posts, community in fetched_posts:
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

            f.write(
                f'{community.name} [{len(posts)}] -- {community.ema_views} views, {community.ema_likes} likes, {community.ema_reposts} reposts, {community.ema_popularity} popularity.\n')
            for i, post in enumerate(posts):
                if i == 20:
                    f.write("\n\n")
                    break

                f.write(
                    f'{i + 1:<{num_width}} {post.url:<{url_width}} | {post.views:<{views_length}} views ({post.views_diff:<+{views_d_length}.2f}) | {post.likes:<{likes_length}} likes ({post.likes_diff:<+{likes_d_length}.2f}) | {post.reposts:<{reposts_length}} reposts ({post.reposts_diff:<+{reposts_d_length}.2f})   Popularity: {post.popularity:<{popularity_length}} ({post.popularity_diff:<+{popularity_d_length}.2f})\n')
            f.write("\n\n")

    def report_to_tg(self, fetched_posts):
        # API only allows to send 20 messages per minute so we neet to wait
        messages_sent = 0
        to_send = len([a for pl in fetched_posts for p in pl[0] for a in p.attachments if 'photo' in a])
        print(f'Sending {to_send} messages to telegram')
        start_time = time.time()
        s = requests.Session()
        for posts, community in fetched_posts:
            for post in posts:
                msg = []
                for a in filter(lambda a_: 'photo' in a_, post.attachments):
                    obj = {'type': 'photo', 'media': max(a['photo']['sizes'], key=lambda sz: sz['height'])['url']}
                    msg.append(obj)
                if msg:
                    caption = str(post)
                    request = None
                    if len(msg) == 1:
                        request = requests.Request(
                            'GET',
                            self.tg_url_prefix_single,
                            params={
                                'chat_id': self.chat_id,
                                'photo': msg[0]['media'],
                                'caption': caption,
                                'disable_notification': True
                            }
                        )
                        request = request.prepare()
                    else:
                        msg[0]['caption'] = caption
                        request = requests.Request(
                            'GET',
                            self.tg_url_prefix,
                            params={
                                'chat_id': self.chat_id,
                                'media': json.dumps(msg),
                                'disable_notification': True
                            }
                        )
                        request = request.prepare()
                        # response = requests.get(self.tg_url_prefix, params={
                        #     'chat_id': self.chat_id,
                        #     'media': json.dumps(msg),
                        #     'disable_notification': True
                        # })
                    response = s.send(request)
                    while response.status_code != 200:
                        print(f'Error sending message to telegram: {response.text}')
                        wait_time = json.loads(response.text)['parameters']['retry_after']
                        print(f'Waiting {wait_time} seconds')
                        time.sleep(wait_time)
                        response = s.send(request)

                    messages_sent += len(msg)
                    print(f'Sent {messages_sent} / {to_send} messages to telegram')
                    time.sleep(1.0)

        print(f'{messages_sent} messages sent in {time.time() - start_time} seconds')


def main():
    print('Starting fetcher')
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dry_run",
                        action="store_true")
    args = parser.parse_args()

    fetcher = Fetcher(args)
    fetcher.fetch()
    fetcher.db_session.close()


if __name__ == '__main__':
    main()
