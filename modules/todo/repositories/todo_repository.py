from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

from modules.todo.schemas.todo_schema import (
    TodoCreate,
    TodoUpdate
)

from models import Todo


class TodoRepository:

    def __init__(self, engine):
        self.engine = engine

    def create(self, todo_data: TodoCreate, user_id: int):

        with Session(self.engine) as session:

            todo = Todo(
                user_id=user_id,
                title=todo_data.title,
                description=todo_data.description,
                due_date=todo_data.due_date,
                due_time=todo_data.due_time
            )

            session.add(todo)
            session.commit()
            session.refresh(todo)

            return todo

    def search(
        self,
        user_id: int,
        title: str | None = None,
        due_date=None,
        status: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
        limit: int | None = None
    ):

        with Session(self.engine) as session:

            query = session.query(Todo).filter(
                Todo.user_id == user_id,
                Todo.deleted_at.is_(None)
            )

            if title:
                query = query.filter(
                    Todo.title.ilike(f"%{title}%")
                )

            if due_date:
                query = query.filter(
                    Todo.due_date == due_date
                )

            if status:
                query = query.filter(
                    Todo.status == status
                )
            
            # Sorting
            if sort_by == "created_at":
                if sort_order == "asc":
                    query = query.order_by(Todo.created_at.asc())
                else:
                    query = query.order_by(Todo.created_at.desc())

            elif sort_by == "updated_at":
                if sort_order == "asc":
                    query = query.order_by(Todo.updated_at.asc())
                else:
                    query = query.order_by(Todo.updated_at.desc())

            elif sort_by == "due_date":
                if sort_order == "asc":
                    query = query.order_by(
                        Todo.due_date.asc()
                    )
                else:
                    query = query.order_by(
                        Todo.due_date.desc()
                    )
            # Limit
            if limit:
                query = query.limit(limit)
                
            print(
                "Repo SEARCH:",
                {
                    "title": title,
                    "due_date": due_date,
                    "status": status,
                    "sort_by": sort_by,
                    "sort_order": sort_order,
                    "limit": limit
                }
            )

            result = query.all()

            return result

    def update(
        self,
        todo_id: int,
        user_id: int,
        todo_data: TodoUpdate
    ):

        with Session(self.engine) as session:

            todo = (
                session.query(Todo)
                .filter(
                    Todo.id == todo_id,
                    Todo.user_id == user_id,
                    Todo.deleted_at.is_(None)
                )
                .first()
            )

            if not todo:
                return None

            update_data = todo_data.model_dump(
                exclude_unset=True,
                exclude_none=True
            )

            for field, value in update_data.items():
                setattr(todo, field, value)

            session.commit()
            session.refresh(todo)

            return todo
        
    def search_candidates(self, user_id: int, title_keywords: list[str], due_date=None, status: str | None = None, limit: int = 10):
        with Session(self.engine) as session:

            query = session.query(Todo).filter(
                Todo.user_id == user_id,
                Todo.deleted_at.is_(None)
            )

            if title_keywords:
                title_conditions = [
                    Todo.title.ilike(f"%{keyword}%")
                    for keyword in title_keywords
                ]

                query = query.filter(
                    or_(*title_conditions)
                )

            if due_date:
                query = query.filter(
                    Todo.due_date == due_date
                )

            if status:
                query = query.filter(
                    Todo.status == status
                )

            return query.limit(limit).all()
    
    def soft_delete(self, todo_id: int, user_id: int):
        with Session(self.engine) as session:

            todo = (
                session.query(Todo)
                .filter(
                    Todo.id == todo_id,
                    Todo.user_id == user_id,
                    Todo.deleted_at.is_(None)
                )
                .first()
            )

            if not todo:
                return None

            todo.deleted_at = datetime.utcnow()

            session.commit()
            session.refresh(todo)

            return todo
        
    def complete(self, todo_id: int, user_id: int):
        with Session(self.engine) as session:

            todo = (
                session.query(Todo)
                .filter(
                    Todo.id == todo_id,
                    Todo.user_id == user_id,
                    Todo.deleted_at.is_(None)
                )
                .first()
            )

            if not todo:
                return None

            todo.status = "completed"

            session.commit()
            session.refresh(todo)

            return todo