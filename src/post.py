from datetime import datetime, timezone
from functools import cached_property

from pydantic import BaseModel, Field, computed_field, ConfigDict

from src.model.community import Community
from utils import format_number
from model.post import Post as DBPost


class Post(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    community: Community
    likes: int
    reposts: int
    date: datetime
    text: str
    views: int
    attachments: list[str]
    url: str | None = None
    is_pinned: int = 0
    fetch_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @computed_field(return_type=float)  # type: ignore[prop-decorator]
    @cached_property
    def popularity(self) -> float:
        return round(self.likes / self.views, 2) if self.views > 0 else 0.0

    @computed_field(return_type=bool)  # type: ignore[prop-decorator]
    @cached_property
    def is_worthy(self) -> bool:
        return (
            self.views_diff > 0
            or self.likes_diff > 0
            or self.reposts_diff > 0
            or self.popularity_diff > 0
        )

    @computed_field(return_type=float)  # type: ignore[prop-decorator]
    @cached_property
    def views_diff(self) -> float:
        return round(self.views - self.community.ema_views, 2)

    @computed_field(return_type=float)  # type: ignore[prop-decorator]
    @cached_property
    def likes_diff(self) -> float:
        return round(self.likes - self.community.ema_likes, 2)

    @computed_field(return_type=float)  # type: ignore[prop-decorator]
    @cached_property
    def reposts_diff(self) -> float:
        return round(self.reposts - self.community.ema_reposts, 2)

    @computed_field(return_type=float)  # type: ignore[prop-decorator]
    @cached_property
    def popularity_diff(self) -> float:
        return round(self.popularity - self.community.ema_popularity, 2)

    def to_db_representation(self) -> DBPost:
        return DBPost(
            link=self.url,
            community_id=self.community.id,
            views=self.views,
            likes=self.likes,
            reposts=self.reposts,
            popularity=self.popularity,
            is_worthy=self.is_worthy,
            fetched_on=self.fetch_date,
            posted_on=self.date,
        )

    def __str__(self) -> str:
        return (
            f"{self.url}\n"
            f"Popularity: {self.popularity} ({format_number(self.popularity_diff, small=True)})\n"
            "\n"
            f"{self.views} views ({format_number(self.views_diff)})\n"
            f"{self.likes} likes ({format_number(self.likes_diff)})\n"
            f"{self.reposts} reposts ({format_number(self.reposts_diff)})"
        )
