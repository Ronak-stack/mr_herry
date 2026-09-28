from modules.todo.services.todo_service import TodoService
from modules.todo.todo_action import detect_todo_action
from memory.context_store import save_memory


def todo_to_dict(todo):
    return {
        "id": todo.id,
        "user_id": todo.user_id,
        "title": todo.title,
        "description": todo.description,
        "due_date": (
            todo.due_date.isoformat()
            if todo.due_date
            else None
        ),
        "due_time": (
            todo.due_time.strftime("%H:%M")
            if todo.due_time
            else None
        ),
        "status": todo.status
    }


def handle_todo(
    state,
    client,
    engine,
    background_tasks
):
    prompt = state.current_prompt

    service = TodoService(engine)

    action = detect_todo_action(
        prompt=prompt,
        client=client
    )

    print("TODO ACTION:", action)

    # =========================
    # CREATE
    # =========================
    if action == "CREATE":

        todo = service.create_from_prompt(
            prompt=prompt,
            user_id=state.user_id,
            client=client
        )

        if isinstance(todo, dict):
            return todo

        todo_data = todo_to_dict(todo)

        save_memory(
            intent="TODO",
            prompt=prompt,
            output=todo_data,
            metadata={
                "action": "create",
                "todo_id": todo.id
            }
        )

        return {
            "success": True,
            "stage": "created",
            "data": todo_data
        }

    # =========================
    # SEARCH
    # =========================
    elif action == "SEARCH":

        filters = service.extract_search_filters(
            prompt=prompt,
            client=client
        )

        if isinstance(filters, dict) and "error" in filters:
            return {
                "success": False,
                "stage": "search_filter_validation",
                "error": filters["error"]
            }

        todos = service.search_todos(
            user_id=state.user_id,
            title=filters.get("title"),
            due_date=filters.get("due_date"),
            status=filters.get("status"),
            sort_by=filters.get("sort_by"),
            sort_order=filters.get("sort_order"),
            limit=filters.get("limit")
        )

        todo_data = [
            todo_to_dict(todo)
            for todo in todos
        ]

        return {
            "success": True,
            "stage": "search",
            "filters": filters,
            "count": len(todo_data),
            "data": todo_data
        }

    # =========================
    # UPDATE
    # =========================
    elif action == "UPDATE":

        result = service.update_from_prompt(
            prompt=prompt,
            user_id=state.user_id,
            client=client
        )

        if isinstance(result, dict):
            return result

        todo_data = todo_to_dict(result)

        save_memory(
            intent="TODO",
            prompt=prompt,
            output=todo_data,
            metadata={
                "action": "update",
                "todo_id": result.id
            }
        )

        return {
            "success": True,
            "stage": "update",
            "data": todo_data
        }

    # =========================
    # DELETE
    # =========================
    elif action == "DELETE":
        result = service.delete_from_prompt(
            prompt=prompt,
            user_id=state.user_id,
            client=client
        )

        if isinstance(result, dict):
            return result

        deleted_todo = {
            "id": result.id,
            "user_id": result.user_id,
            "title": result.title,
            "description": result.description,
            "due_date": (
                result.due_date.isoformat()
                if result.due_date
                else None
            ),
            "due_time": (
                result.due_time.strftime("%H:%M")
                if result.due_time
                else None
            ),
            "status": result.status,
            "deleted_at": (
                result.deleted_at.isoformat()
                if result.deleted_at
                else None
            )
        }

        save_memory(
            intent="TODO",
            prompt=prompt,
            output=deleted_todo,
            metadata={
                "action": "delete",
                "todo_id": result.id
            }
        )

        return {
            "success": True,
            "stage": "deleted",
            "data": deleted_todo
        }
    elif action == "COMPLETE":
        result = service.complete_from_prompt(
            prompt=prompt,
            user_id=state.user_id,
            client=client
        )

        if isinstance(result, dict):
            return result

        todo_data = todo_to_dict(result)

        save_memory(
            intent="TODO",
            prompt=prompt,
            output=todo_data,
            metadata={
                "action": "complete",
                "todo_id": result.id
            }
        )

        return {
            "success": True,
            "stage": "completed",
            "data": todo_data
        }
    return {
        "success": False,
        "stage": "action",
        "error": f"Unsupported TODO action: {action}"
    }