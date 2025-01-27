from datetime import datetime, timedelta
from typing import cast

from sqlalchemy import ScalarResult, Table, insert, select
from sqlalchemy.orm import Session

from fetcher.database.models import Community, Post


class Service:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def recreate(self) -> None:
        engine = self.db_session.bind
        assert engine is not None, "Database engine is not bound to the session"

        cast(Table, Community.__table__).create(engine, checkfirst=True)
        cast(Table, Post.__table__).create(engine, checkfirst=True)

    def populate(self, communities: list[dict[str, str]]) -> None:
        self.db_session.execute(
            insert(Community),
            communities,
        )

    def _get_communities(
        self, *, active: bool | None = None, cutoff: timedelta | None = None
    ) -> ScalarResult[Community]:
        query = select(Community)
        if active is not None:
            query = query.where(Community.active == active)

        if cutoff is not None:
            query = query.where(
                (Community.last_fetched >= datetime.now() - cutoff)
                | (Community.last_fetched.is_(None))
            )

        return self.db_session.scalars(query)

    def get_all_communities(self) -> ScalarResult[Community]:
        return self._get_communities()

    def get_active_communities(self) -> ScalarResult[Community]:
        return self._get_communities(active=True)

    def get_unfetched_active_communities(self, cutoff: timedelta):
        return self._get_communities(active=True, cutoff=cutoff)
