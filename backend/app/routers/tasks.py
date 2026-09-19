from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import case, select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Task, utc_now
from app.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
DatabaseSession = Annotated[Session, Depends(get_session)]


def find_task(task_id: int, session: Session) -> Task:
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("", response_model=list[TaskRead])
def list_tasks(
    session: DatabaseSession,
    is_completed: bool | None = None,
    due_before: date | None = None,
    due_from: date | None = None,
    due_to: date | None = None,
):
    if due_from and due_to and due_from > due_to:
        raise HTTPException(status_code=422, detail="due_from must not be after due_to")
    if due_from and due_before and due_from >= due_before:
        raise HTTPException(status_code=422, detail="due_from must be before due_before")

    query = select(Task)
    if is_completed is not None:
        query = query.where(Task.is_completed == is_completed)
    if due_before is not None:
        query = query.where(Task.due_date < due_before)
    if due_from is not None:
        query = query.where(Task.due_date >= due_from)
    if due_to is not None:
        query = query.where(Task.due_date <= due_to)

    if is_completed is True:
        query = query.order_by(Task.completed_at.desc(), Task.id.desc())
    else:
        query = query.order_by(
            Task.due_date.is_(None), Task.due_date,
            case((Task.priority == "high", 0), (Task.priority == "medium", 1), else_=2),
            Task.id,
        )
    return session.scalars(query).all()


@router.post("", response_model=TaskRead, status_code=201)
def create_task(payload: TaskCreate, session: DatabaseSession):
    task = Task(**payload.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskRead)
def retrieve_task(task_id: int, session: DatabaseSession):
    return find_task(task_id, session)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, session: DatabaseSession):
    task = find_task(task_id, session)
    changes = payload.model_dump(exclude_unset=True)
    completed = changes.pop("is_completed", None)
    if completed is not None and completed != task.is_completed:
        task.is_completed = completed
        task.completed_at = utc_now() if completed else None
    for name, value in changes.items():
        setattr(task, name, value)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: DatabaseSession):
    session.delete(find_task(task_id, session))
    session.commit()
    return Response(status_code=204)
