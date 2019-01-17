class Post:
    def __init__(self, id, likes, reposts, date, text, views, url=None, is_pinned=0):
        self._id = id
        self._likes = likes
        self._reposts = reposts
        self._text = text
        self._date = date
        self._views = views
        self._url = url
        self._is_pinned = is_pinned
        
        self._popularity = round(self._views/self._likes, 2)

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
