import time
from collections import defaultdict
from datetime import timedelta
from typing import Final

import vk

from fetcher.database.models import Community
from fetcher.database.service import Service
from fetcher.report import Reporter, FileReporter, TelegramReporter
from fetcher.settings import settings
from fetcher.post import Post


class Fetcher:
    SECONDS_IN_DAY: Final[int] = 86400
    TO_TIME = round(time.time()) - timedelta(days=1).total_seconds()
    FROM_TIME = round(TO_TIME) - timedelta(days=1).total_seconds()

    def __init__(self, *, db_service: Service, dry_run: bool = False):
        # init vk api object
        self.vk_api = vk.API(
            access_token=settings.vk_access_token,
            v=settings.vk_api_version,
            timeout=10000,
        )

        self.dry_run = dry_run

        self.reporters: list[Reporter] = [FileReporter()]
        if not dry_run:
            self.reporters.append(TelegramReporter())

        self.db_service = db_service

    def fetch(self) -> None:
        worthy_posts = defaultdict(list)
        if self.dry_run:
            communities = self.db_service.get_active_communities()
        else:
            communities = self.db_service.get_unfetched_active_communities(
                cutoff=timedelta(days=1)
            )

        for community in communities:
            posts = sorted(
                self.fetch_community(community),
                key=lambda x: -x.popularity,
            )
            if posts:
                worthy_posts[community].extend(posts)

        for reporter in self.reporters:
            reporter.report(worthy_posts)

    def fetch_community(self, community: Community) -> list[Post]:
        seen = 0
        print(f"Fetching {community.name}...")
        outdated = False
        post_objects = []

        while not outdated:
            response = self.vk_api.wall.get(domain=community.id, count=100, offset=seen)
            posts = response["items"]
            if not posts:
                break

            seen += len(posts)
            for post in filter(
                lambda p: not (
                    ("is_pinned" in p and p["is_pinned"] == 1)
                    or p["date"] > Fetcher.TO_TIME
                    or "views" not in p
                    or p["marked_as_ads"] != 0
                ),
                posts,
            ):
                if post["date"] < Fetcher.FROM_TIME:
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
                    url=f"https://vk.com/wall{post['from_id']}_{post['id']}",
                    is_pinned=post.get("is_pinned", 0),
                    attachments=post["attachments"] if "attachments" in post else [],
                )

                post_objects.append(post)

        worthy_posts = [p for p in post_objects if p.is_worthy]
        print(len(worthy_posts), "posts found!")

        if len(post_objects) > 0:
            community.last_avg_views = sum(p.views for p in post_objects) / len(
                post_objects
            )
            community.last_avg_likes = sum(p.likes for p in post_objects) / len(
                post_objects
            )
            community.last_avg_reposts = sum(p.reposts for p in post_objects) / len(
                post_objects
            )

        community.update_ema()
        community.record_fetch(len(post_objects), len(worthy_posts))

        return worthy_posts
