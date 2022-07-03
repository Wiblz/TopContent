from datetime import datetime

from utils import format_number
from model.post import Post as DBPost


class Post:
    def __init__(self, id, community, likes, reposts, date, text, views, attachments, url=None, is_pinned=0):
        self._id = id
        self._community = community
        self._likes = likes
        self._reposts = reposts
        self._text = text
        self._date = date
        self._fetch_date = datetime.now()
        self._views = views
        self._url = url
        self._is_pinned = is_pinned
        self._attachments = attachments

        self._popularity = round(self._views / self._likes, 2)

    @property
    def id(self):
        return self._id

    @property
    def community(self):
        return self._community

    @property
    def likes(self):
        return self._likes

    @property
    def reposts(self):
        return self._reposts

    @property
    def text(self):
        return self._text

    @property
    def date(self):
        return self._date

    @property
    def fetched_on(self):
        return self._fetch_date

    @property
    def views(self):
        return self._views

    @property
    def popularity(self):
        return self._popularity

    @property
    def url(self):
        return self._url

    @property
    def is_pinned(self):
        return self._is_pinned

    @property
    def attachments(self):
        return self._attachments

    def set_difference(self, community):
        self.views_diff = round(self.views - community.ema_views, 2)
        self.likes_diff = round(self.likes - community.ema_likes, 2)
        self.reposts_diff = round(self.reposts - community.ema_reposts, 2)
        self.popularity_diff = round(self.popularity - community.ema_popularity, 2)

    def is_worthy(self):
        return self.views > self.community.ema_views or \
               self.likes > self.community.ema_likes or \
               self.reposts > self.community.ema_reposts or \
               self.popularity < self.community.ema_popularity

    def to_db_representation(self):
        return DBPost(
            link=self.url,
            community_id=self.community.id,
            views=self.views,
            likes=self.likes,
            reposts=self.reposts,
            popularity=self.popularity,
            is_worthy=self.is_worthy(),
            fetched_on=self.fetched_on,
            posted_on=self.date,
        )

    def __str__(self):
        return f'{self.url}\n' \
               f'Popularity: {self.popularity} ({format_number(self.popularity_diff, inverse=True, small=True)})\n' \
               '\n' \
               f'{self.views} views ({format_number(self.views_diff)})\n' \
               f'{self.likes} likes ({format_number(self.likes_diff)})\n' \
               f'{self.reposts} reposts ({format_number(self.reposts_diff)})'
