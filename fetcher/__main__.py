import argparse
import json

from fetcher.database import Session
from fetcher.database.service import Service
from fetcher.fetcher import Fetcher
from fetcher.settings import settings

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")

init_parser = subparsers.add_parser("init")
populate_parser = subparsers.add_parser("populate")

args = parser.parse_args()

session = Session()
try:
    service = Service(db_session=session)
    if args.command == "init":
        print("Initializing database...")
        service.recreate()
    elif args.command == "populate":
        print("Populating database...")
        with open("communities.json", "r") as f:
            communities = json.load(f)

        service.populate(communities)
    else:
        print("Fetching data...")
        fetcher = Fetcher(db_service=service, dry_run=settings.dry_run)
        fetcher.fetch()
    if not settings.dry_run:
        session.commit()
finally:
    session.close()
