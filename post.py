from utils import format_number


class Post:
    def __init__(self, id, likes, reposts, date, text, views, attachments, url=None, is_pinned=0):
        self._id = id
        self._likes = likes
        self._reposts = reposts
        self._text = text
        self._date = date
        self._views = views
        self._url = url
        self._is_pinned = is_pinned
        self._attachments = attachments

        self._popularity = round(self._views / self._likes, 2)

    @property
    def id(self):
        return self._id

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
        self.views_diff = round(self.views - community.avg_views, 2)
        self.likes_diff = round(self.likes - community.avg_likes, 2)
        self.reposts_diff = round(self.reposts - community.avg_reposts, 2)
        self.popularity_diff = round(self.popularity - community.avg_popularity, 2)

    def is_worthy(self, community):
        return self.views > community.avg_views or \
               self.likes > community.avg_likes or \
               self.reposts > community.avg_reposts or \
               self.popularity < community.avg_popularity

    def __str__(self):
        return f'''{self.url}
Popularity: {self.popularity} ({format_number(self.popularity_diff, inverse=True, small=True)})
    
{self.views} views ({format_number(self.views_diff)})
{self.likes} likes ({format_number(self.likes_diff)})
{self.reposts} reposts ({format_number(self.reposts_diff)}) '''
