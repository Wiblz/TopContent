from datetime import datetime

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from fetcher.ema import EMA


class Base(DeclarativeBase):
    pass


class Community(Base):
    __tablename__ = "communities"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str]
    posts_fetched: Mapped[int]
    worthy_posts: Mapped[int]
    avg_posts_per_day: Mapped[float]
    active: Mapped[bool] = mapped_column(default=True)
    days: Mapped[int]
    ema_views: Mapped[float]
    ema_likes: Mapped[float]
    ema_reposts: Mapped[float]
    ema_popularity: Mapped[float]
    last_fetched: Mapped[datetime | None]

    last_avg_views: Mapped[float]
    last_avg_likes: Mapped[float]
    last_avg_reposts: Mapped[float]

    def update_ema(self) -> None:
        self.ema_views = EMA(self.ema_views, self.last_avg_views)
        self.ema_likes = EMA(self.ema_likes, self.last_avg_likes)
        self.ema_reposts = EMA(self.ema_reposts, self.last_avg_reposts)

        if self.ema_views == 0 or self.ema_likes == 0:
            self.ema_popularity = 0
        else:
            self.ema_popularity = round(self.ema_likes / self.ema_views, 2)

    def record_fetch(self, total_fetched: int, worthy: int) -> None:
        self.avg_posts_per_day = round(
            (self.avg_posts_per_day * self.days + total_fetched) / (self.days + 1),
            2,
        )
        self.posts_fetched += total_fetched
        self.worthy_posts += worthy
        self.days += 1
        self.last_fetched = datetime.now()

    def __repr__(self):
        return (
            f"id: {self.id},\nname: {self.name},\nposts_fetched: {self.posts_fetched},\n"
            f"moving average of views per day: {self.ema_views}\n"
            f"moving average of likes per day: {self.ema_likes}\n"
            f"moving average of reposts per day: {self.ema_reposts}\n" + "-" * 30 + "\n"
        )


class Post(Base):
    __tablename__ = "posts"

    link: Mapped[str] = mapped_column(primary_key=True)
    community_id: Mapped[str] = mapped_column(ForeignKey(Community.id))

    views: Mapped[int]
    likes: Mapped[int]
    reposts: Mapped[int]
    popularity: Mapped[float]

    is_worthy: Mapped[bool]
    fetched_on: Mapped[datetime]
    posted_on: Mapped[datetime]
