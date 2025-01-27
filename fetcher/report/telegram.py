import json
import time

import requests

from fetcher.database.models import Community
from fetcher.post import Post
from fetcher.report import Reporter
from fetcher.settings import settings


class TelegramReporter(Reporter):
    def __init__(self):
        self.chat_id = settings.tg_chat_id

        # init telegram
        self.tg_url_prefix = (
            f"https://api.telegram.org/bot{settings.tg_access_token}/sendMediaGroup"
        )
        self.tg_url_prefix_single = (
            f"https://api.telegram.org/bot{settings.tg_access_token}/sendPhoto"
        )

    def report(self, fetched_posts: dict[Community, list[Post]]):
        # API only allows to send 20 messages per minute so we neet to wait
        messages_sent = 0
        to_send = len(
            [
                attachment
                for posts in fetched_posts.values()
                for post in posts
                for attachment in post.attachments
                if "photo" in attachment
            ]
        )
        print(f"Sending {to_send} messages to telegram")
        start_time = time.time()
        s = requests.Session()
        for community, posts in fetched_posts.items():
            for post in posts:
                msg = []
                for a in filter(lambda a_: "photo" in a_, post.attachments):
                    obj = {
                        "type": "photo",
                        "media": max(a["photo"]["sizes"], key=lambda sz: sz["height"])[
                            "url"
                        ],
                    }
                    msg.append(obj)
                if msg:
                    caption = str(post)
                    request = None
                    if len(msg) == 1:
                        request = requests.Request(
                            "GET",
                            self.tg_url_prefix_single,
                            params={
                                "chat_id": self.chat_id,
                                "photo": msg[0]["media"],
                                "caption": caption,
                                "disable_notification": True,
                            },
                        )
                        request = request.prepare()
                    else:
                        msg[0]["caption"] = caption
                        request = requests.Request(
                            "GET",
                            self.tg_url_prefix,
                            params={
                                "chat_id": self.chat_id,
                                "media": json.dumps(msg),
                                "disable_notification": True,
                            },
                        )
                        request = request.prepare()
                        # response = requests.get(self.tg_url_prefix, params={
                        #     'chat_id': self.chat_id,
                        #     'media': json.dumps(msg),
                        #     'disable_notification': True
                        # })
                    response = s.send(request)
                    while response.status_code != 200:
                        print(f"Error sending message to telegram: {response.text}")
                        wait_time = json.loads(response.text)["parameters"][
                            "retry_after"
                        ]
                        print(f"Waiting {wait_time} seconds")
                        time.sleep(wait_time)
                        response = s.send(request)

                    messages_sent += len(msg)
                    print(f"Sent {messages_sent} / {to_send} messages to telegram")
                    time.sleep(1.0)

        print(f"{messages_sent} messages sent in {time.time() - start_time} seconds")
