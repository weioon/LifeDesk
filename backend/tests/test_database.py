from datetime import datetime

import pytest
from alembic import command
from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import PROJECT_ROOT, database_path
from app.models import Task
from conftest import migration_config


def test_persists_after_engine_recreated(client, engine):
    created = client.post("/api/tasks", json={"title": "Survives restart"}).json()
    url = engine.url
    engine.dispose()
    restarted = create_engine(url)
    try:
        with Session(restarted) as session:
            task = session.scalar(select(Task).where(Task.id == created["id"]))
            assert task.title == "Survives restart"
    finally:
        restarted.dispose()


def test_migration_round_trip_and_metadata(engine):
    with engine.begin() as connection:
        config = migration_config(connection)
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0001_create_tasks"
        command.check(config)
        command.downgrade(config, "base")
        assert "tasks" not in inspect(connection).get_table_names()
        command.upgrade(config, "head")
        assert "tasks" in inspect(connection).get_table_names()


@pytest.mark.parametrize("values", [
    {"title": "   "}, {"title": "x" * 201}, {"priority": "urgent"},
    {"is_completed": True, "completed_at": None},
    {"is_completed": False, "completed_at": datetime(2026, 9, 19)},
])
def test_database_constraints(engine, values):
    with Session(engine) as session:
        session.add(Task(**{"title": "Valid", **values}))
        with pytest.raises(IntegrityError):
            session.commit()


def test_database_path_independent_of_working_directory(monkeypatch, tmp_path):
    monkeypatch.delenv("LIFEDESK_DB_PATH", raising=False)
    monkeypatch.chdir(tmp_path)
    assert database_path() == PROJECT_ROOT / "data" / "lifedesk.db"
    monkeypatch.setenv("LIFEDESK_DB_PATH", "data/custom.db")
    assert database_path() == PROJECT_ROOT / "data" / "custom.db"
