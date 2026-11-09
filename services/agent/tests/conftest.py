import importlib.util
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import REPO_ROOT
from app.db import Base, get_session
from app.main import app
from app.seed import load_dataset


def _load_generator():
    spec = importlib.util.spec_from_file_location(
        "seed_generate", REPO_ROOT / "data" / "seed" / "generate.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def generated():
    return _load_generator().generate(n_customers=30, seed=7, as_of=date(2026, 11, 1))


@pytest.fixture
def client(generated):
    # In-memory SQLite keeps tests independent of the docker Postgres.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)
    with TestSession() as s:
        load_dataset(s, generated[0])

    def override():
        with TestSession() as s:
            yield s

    app.dependency_overrides[get_session] = override
    yield TestClient(app)
    app.dependency_overrides.clear()
