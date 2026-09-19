from datetime import datetime

import pytest


def create(client, **fields):
    response = client.post("/api/tasks", json={"title": "A task", **fields})
    assert response.status_code == 201
    return response.json()


def test_create_task_defaults(client):
    task = create(client, title="  Plan my day  ")
    assert task["title"] == "Plan my day"
    assert task["priority"] == "medium"
    assert task["description"] is None
    assert task["due_date"] is None
    assert task["is_completed"] is False
    assert task["completed_at"] is None
    assert task["id"] > 0
    assert datetime.fromisoformat(task["created_at"]).utcoffset().total_seconds() == 0
    assert datetime.fromisoformat(task["updated_at"]) >= datetime.fromisoformat(task["created_at"])


def test_create_task_all_fields(client):
    task = create(client, description="Bring documents", due_date="2026-09-20", priority="high")
    assert task["description"] == "Bring documents"
    assert task["due_date"] == "2026-09-20"
    assert task["priority"] == "high"


@pytest.mark.parametrize("payload", [
    {}, {"title": ""}, {"title": " \t\n\u2003 "}, {"title": None},
    {"title": "x" * 201}, {"title": "ok", "priority": "urgent"},
    {"title": "ok", "priority": None}, {"title": "ok", "due_date": "2026-02-30"},
    {"title": "ok", "due_date": "2026-09-20T00:00:00Z"},
    {"title": "ok", "due_date": 0}, {"title": "ok", "completed_at": "2026-09-19"},
])
def test_invalid_create(client, payload):
    assert client.post("/api/tasks", json=payload).status_code == 422
    assert client.get("/api/tasks").json() == []


def test_title_boundary(client):
    assert create(client, title="x" * 200)["title"] == "x" * 200


def test_retrieve_and_list(client):
    assert client.get("/api/tasks").json() == []
    task = create(client)
    response = client.get(f"/api/tasks/{task['id']}")
    assert response.status_code == 200
    assert response.json() == task
    assert client.get("/api/tasks").json() == [task]


def test_update_and_clear_optional_fields(client):
    original = create(client, description="Keep me", due_date="2026-09-20")
    url = f"/api/tasks/{original['id']}"
    response = client.patch(url, json={"title": " Updated ", "priority": "low"})
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Updated"
    assert updated["priority"] == "low"
    assert updated["description"] == "Keep me"
    assert updated["due_date"] == "2026-09-20"
    assert updated["created_at"] == original["created_at"]
    assert updated["updated_at"] > original["updated_at"]
    cleared = client.patch(url, json={"description": None, "due_date": None}).json()
    assert cleared["description"] is None and cleared["due_date"] is None
    assert client.get(url).json() == cleared


@pytest.mark.parametrize("payload", [
    {"title": " \n "}, {"title": "x" * 201}, {"title": None},
    {"priority": "urgent"}, {"priority": None}, {"is_completed": None},
    {"due_date": "not-a-date"}, {"created_at": "2026-09-19"},
])
def test_invalid_update_does_not_change_task(client, payload):
    task = create(client)
    url = f"/api/tasks/{task['id']}"
    assert client.patch(url, json=payload).status_code == 422
    assert client.get(url).json() == task


def test_complete_reopen_and_complete_again(client):
    task = create(client)
    url = f"/api/tasks/{task['id']}"
    completed = client.patch(url, json={"is_completed": True}).json()
    assert completed["is_completed"] is True
    assert datetime.fromisoformat(completed["completed_at"]).utcoffset().total_seconds() == 0
    assert client.get(url).json() == completed
    assert client.patch(url, json={"is_completed": True}).json() == completed
    reopened = client.patch(url, json={"is_completed": False}).json()
    assert reopened["is_completed"] is False
    assert reopened["completed_at"] is None
    assert client.get(url).json() == reopened
    completed_again = client.patch(url, json={"is_completed": True}).json()
    assert completed_again["completed_at"] > completed["completed_at"]


def test_empty_patch_is_noop(client):
    task = create(client)
    assert client.patch(f"/api/tasks/{task['id']}", json={}).json() == task


def test_delete(client):
    task = create(client)
    response = client.delete(f"/api/tasks/{task['id']}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/tasks/{task['id']}").status_code == 404
    assert client.get("/api/tasks").json() == []


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_missing_task(client, method):
    kwargs = {"json": {"title": "Missing"}} if method == "patch" else {}
    response = getattr(client, method)("/api/tasks/999999", **kwargs)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_date_filters_and_priority_order(client):
    overdue = create(client, due_date="2026-09-18")
    low = create(client, due_date="2026-09-19", priority="low")
    high = create(client, due_date="2026-09-19", priority="high")
    medium = create(client, due_date="2026-09-19")
    future = create(client, due_date="2026-09-20")
    undated = create(client)
    def ids(**params):
        response = client.get("/api/tasks", params=params)
        assert response.status_code == 200
        return [task["id"] for task in response.json()]

    assert ids() == [t["id"] for t in [overdue, high, medium, low, future, undated]]
    assert ids(due_before="2026-09-19") == [overdue["id"]]
    assert ids(due_from="2026-09-19", due_to="2026-09-19") == [t["id"] for t in [high, medium, low]]
    assert ids(due_from="2026-09-20") == [future["id"]]
    assert ids(due_to="2026-09-18") == [overdue["id"]]


def test_completion_filters_and_order(client):
    first, second, active = create(client), create(client), create(client)
    for task in (first, second):
        client.patch(f"/api/tasks/{task['id']}", json={"is_completed": True})
    assert [t["id"] for t in client.get("/api/tasks?is_completed=true").json()] == [second["id"], first["id"]]
    assert client.get("/api/tasks?is_completed=false").json() == [active]
    assert len(client.get("/api/tasks").json()) == 3
    assert client.get("/api/tasks?is_completed=true&due_from=2026-09-19").json() == []


@pytest.mark.parametrize("query", [
    "due_from=bad", "due_to=2026-02-30", "is_completed=maybe",
    "due_from=2026-09-20&due_to=2026-09-19",
    "due_from=2026-09-19&due_before=2026-09-19",
])
def test_invalid_filters(client, query):
    assert client.get(f"/api/tasks?{query}").status_code == 422
