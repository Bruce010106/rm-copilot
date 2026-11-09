"""Load data/seed/output/dataset.json into the database (drops and recreates tables).

Usage (from services/agent):  python -m app.seed [path/to/dataset.json]
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import REPO_ROOT
from app.db import Base, SessionLocal, engine
from app.models import Customer, Holding, Interaction, Product, RelationshipManager

DEFAULT_PATH = REPO_ROOT / "data" / "seed" / "output" / "dataset.json"


def _d(v: str | None) -> date | None:
    return date.fromisoformat(v) if v else None


def load_dataset(session: Session, data: dict) -> None:
    session.add_all(RelationshipManager(**r) for r in data["relationship_managers"])
    session.add_all(Product(**p) for p in data["products"])
    session.flush()
    session.add_all(
        Customer(**{**c, "birth_date": _d(c["birth_date"]), "onboarded_at": _d(c["onboarded_at"])})
        for c in data["customers"]
    )
    session.flush()
    session.add_all(
        Holding(**{**h, "start_date": _d(h["start_date"]), "maturity_date": _d(h["maturity_date"])})
        for h in data["holdings"]
    )
    session.add_all(
        Interaction(**{**i, "occurred_at": datetime.fromisoformat(i["occurred_at"])})
        for i in data["interactions"]
    )
    session.commit()


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    data = json.loads(path.read_text("utf-8"))
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        load_dataset(session, data)
    print(f"loaded {len(data['customers'])} customers from {path}")


if __name__ == "__main__":
    main()
