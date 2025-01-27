from datetime import datetime

from fetcher.database.models import Community
from fetcher.post import Post
from fetcher.report import Reporter
from fetcher.settings import settings
from fetcher.utils import get_max_str_length, get_max_formatted_number_length


class FileReporter(Reporter):
    def __init__(self, path: str | None = None):
        self.path = settings.local_report_path
        if path is not None:
            self.path = path

    @staticmethod
    def _get_report_header() -> str:
        return f"\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    def report(self, fetched_posts: dict[Community, list[Post]]) -> None:
        if not fetched_posts:
            return

        with open(self.path, "a") as f:
            f.write(FileReporter._get_report_header())
            for community, posts in fetched_posts.items():
                posts = posts[:20]

                num_width = 4 if len(posts) > 10 else 3
                url_width = get_max_str_length(posts, "url")
                views_length = get_max_formatted_number_length(posts, "views")
                likes_length = get_max_formatted_number_length(posts, "likes")
                reposts_length = get_max_formatted_number_length(posts, "reposts")
                popularity_length = get_max_str_length(posts, "popularity")

                views_d_length = get_max_formatted_number_length(posts, "views_diff")
                likes_d_length = get_max_formatted_number_length(posts, "likes_diff")
                reposts_d_length = get_max_formatted_number_length(
                    posts, "reposts_diff"
                )
                popularity_d_length = get_max_formatted_number_length(
                    posts, "popularity_diff"
                )

            f.write(
                f"{community.name} [{len(posts)}] -- {community.ema_views} views, {community.ema_likes} likes, {community.ema_reposts} reposts, {community.ema_popularity} popularity.\n"
            )
            for i, post in enumerate(posts):
                if i == 20:
                    f.write("\n\n")
                    break

                f.write(
                    f"{i + 1:<{num_width}} {post.url:<{url_width}} | {post.views:<{views_length}} views ({post.views_diff:<+{views_d_length}.2f}) | {post.likes:<{likes_length}} likes ({post.likes_diff:<+{likes_d_length}.2f}) | {post.reposts:<{reposts_length}} reposts ({post.reposts_diff:<+{reposts_d_length}.2f})   Popularity: {post.popularity:<{popularity_length}} ({post.popularity_diff:<+{popularity_d_length}.2f})\n"
                )
            f.write("\n\n")
