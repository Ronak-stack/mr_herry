import json
from modules.todo.schemas.todo_schema import (
    TodoCreate,
    TodoUpdate,
    TodoTarget,
    TodoUpdateRequest,
    TodoMatchResult,
    TodoDeleteRequest
)

from modules.todo.repositories.todo_repository import TodoRepository
from pydantic import ValidationError
from datetime import date
class TodoService:

    def __init__(self, engine):
        self.engine = engine
        self.repository = TodoRepository(engine=engine)

    def extract_todo(self, prompt, client):
        today = date.today().isoformat()

        system_prompt = f"""
        You are a TODO extraction assistant.

        Your job is to extract TODO information from the user's request
        and convert it into structured JSON.

        Today's date is: {today}

        Return ONLY valid JSON in exactly this format:

        {{
            "title": "...",
            "description": null,
            "due_date": null,
            "due_time": null
        }}

        Rules:

        1. "title" is required.
        2. "description" is optional. Use null if the user does not provide one.
        3. "due_date" must be in YYYY-MM-DD format or null.
        4. "due_time" must be in HH:MM 24-hour format or null.
        5. Resolve relative dates using today's date.
        - "today" = today's date
        - "tomorrow" = today's date + 1 day
        - "day after tomorrow" = today's date + 2 days
        6. Resolve relative time expressions when possible.
        - "6 am" = "06:00"
        - "6 pm" = "18:00"
        - "6:30 am" = "06:30"
        7. Words such as "morning", "afternoon", "evening" should NOT
        create an exact time unless the user provides an exact time.
        8. Do not invent information that the user did not provide.
        9. If the user provides both a relative date and an exact time,
        resolve both.
        10. Return JSON only.
        11. Do not return Markdown.
        12. Do not return explanations.

        Example:

        User request:
        Add buy milk tomorrow next morning at 6 am

        If today's date is 2026-08-26, return:

        {{
            "title": "buy milk",
            "description": null,
            "due_date": "2026-08-27",
            "due_time": "06:00"
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content.strip()

        return json.loads(content)

    def validate_todo(self, todo_data):

        try:
            todo = TodoCreate(**todo_data)

            return {
                "success": True,
                "stage": "validation",
                "data": todo
            }

        except ValidationError as e:

            return {
                "success": False,
                "stage": "validation",
                "error": e.errors()
            }

    def create_from_prompt(
        self,
        prompt,
        user_id,
        client
    ):
        # 1️⃣ Extract
        todo_data = self.extract_todo(
            prompt=prompt,
            client=client
        )

        print("TODO JSON:", todo_data)

        # 2️⃣ Validate
        validation = self.validate_todo(todo_data)

        print("VALIDATION:", validation)

        if not validation["success"]:
            return validation

        # 3️⃣ Repository will come here
        todo = self.repository.create(
            todo_data=validation["data"],
            user_id=user_id
        )
        return todo

    def get_all_todos(self, user_id:int):
        todo = self.repository.find_all(user_id=1)
        return todo

    def search_todos(self, user_id: int, title: str | None = None, due_date: date | None = None, status: str | None = None,  sort_by: str | None = None, sort_order: str | None = None, limit: int | None = None):
        print(
                "Service SEARCH:",
                {
                    "title": title,
                    "due_date": due_date,
                    "status": status,
                    "sort_by": sort_by,
                    "sort_order": sort_order,
                    "limit": limit
                }
            )
        return self.repository.search(
        user_id=user_id,
        title=title,
        due_date=due_date,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit
    )

    def extract_search_filters(self, prompt, client):

        today = date.today().isoformat()

        system_prompt = f"""
                You are a TODO search filter extraction assistant for NEXORA.

                Today's date is: {today}

                Extract only the information needed to search existing TODOs.

                Return ONLY valid JSON in exactly this format:

                {{
                    "title": null,
                    "due_date": null,
                    "status": null,
                    "sort_by": null,
                    "sort_order": null,
                    "limit": null
                }}

                Rules:

                BASIC FILTER RULES:

                - title:
                Extract useful keywords or important words from the user's
                request that can help identify the TODO.
                Use null when no useful title information is present.

                - due_date:
                Return the date in YYYY-MM-DD format or null.

                - status:
                Return one of:
                "pending", "completed", "cancelled", or null.

                - Resolve relative dates using today's date.

                - "today" means today's date.

                - "tomorrow" means today's date + 1 day.

                - "day after tomorrow" means today's date + 2 days.

                - Do not invent information.

                - If a value is not present or cannot be determined,
                return null.

                SORTING RULES:

                - sort_by must be one of:
                "created_at"
                "due_date"
                "updated_at"
                or null.

                - sort_order must be one of:
                "asc"
                "desc"
                or null.

                - "latest", "newest", "most recent", or
                "recently created" means:
                    sort_by = "created_at"
                    sort_order = "desc"

                - "oldest", "first created" means:
                    sort_by = "created_at"
                    sort_order = "asc"

                - "recently updated", "last updated" means:
                    sort_by = "updated_at"
                    sort_order = "desc"

                - "next todo", "next task", or "next due todo" means:
                    sort_by = "due_date"
                    sort_order = "asc"

                - If the user does not ask for any sorting,
                sort_by must be null and sort_order must be null.

                LIMIT RULES:

                - limit must be an integer or null.

                - "latest todo", "next todo", "oldest todo",
                or any request asking for only one TODO means:
                    limit = 1

                - "latest 3 todos", "last 5 todos", etc.:
                extract the requested number as limit.

                - If the user does not specify a number and does not
                imply a single result, use null.

                - Never invent a limit.

                IMPORTANT:

                - Sorting information must not be placed inside title,
                due_date, or status.

                - The word "latest" refers to sorting by created_at,
                not to the TODO title.

                - The word "next" refers to due_date ordering,
                not to the title.

                - Do not use any information that was not provided
                by the user.

                - Return JSON only.

                - Do not return Markdown.

                - Do not return explanations.

                Examples:

                User:
                Mera ATM wala todo dikha

                Output:
                {{
                    "title": "ATM",
                    "due_date": null,
                    "status": null,
                    "sort_by": null,
                    "sort_order": null,
                    "limit": null
                }}

                User:
                28 August wale pending todos dikhao

                Output:
                {{
                    "title": null,
                    "due_date": "2026-08-28",
                    "status": "pending",
                    "sort_by": null,
                    "sort_order": null,
                    "limit": null
                }}

                User:
                Mere saare pending todos dikhao

                Output:
                {{
                    "title": null,
                    "due_date": null,
                    "status": "pending",
                    "sort_by": null,
                    "sort_order": null,
                    "limit": null
                }}

                User:
                Mera latest todo dikhao

                Output:
                {{
                    "title": null,
                    "due_date": null,
                    "status": null,
                    "sort_by": "created_at",
                    "sort_order": "desc",
                    "limit": 1
                }}

                User:
                Mere latest 3 todos dikhao

                Output:
                {{
                    "title": null,
                    "due_date": null,
                    "status": null,
                    "sort_by": "created_at",
                    "sort_order": "desc",
                    "limit": 3
                }}

                User:
                Mera next todo dikhao

                Output:
                {{
                    "title": null,
                    "due_date": null,
                    "status": null,
                    "sort_by": "due_date",
                    "sort_order": "asc",
                    "limit": 1
                }}

                User:
                Recently updated 5 todos dikhao

                Output:
                {{
                    "title": null,
                    "due_date": null,
                    "status": null,
                    "sort_by": "updated_at",
                    "sort_order": "desc",
                    "limit": 5
                }}

                User:
                Mere pending latest 2 todos dikhao

                Output:
                {{
                    "title": null,
                    "due_date": null,
                    "status": "pending",
                    "sort_by": "created_at",
                    "sort_order": "desc",
                    "limit": 2
                }}
                """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content.strip()

        return json.loads(content)

    def update_todo(
        self,
        todo_id: int,
        user_id: int,
        todo_data: TodoUpdate
        ):

        return self.repository.update(
            todo_id=todo_id,
            user_id=user_id,
            todo_data=todo_data
        )

    def extract_update_request(self, prompt, client):

        today = date.today().isoformat()

        system_prompt = f"""
            You are a TODO update extraction assistant for NEXORA.

            Today's date is: {today}

            Your job is to understand the user's request and extract:

            1. TARGET:
            Which existing TODO does the user want to update?

            2. CHANGES:
            Which fields of that TODO does the user want to change?

            Return ONLY valid JSON in exactly this structure:

            {{
                "target": {{
                    "title": null,
                    "due_date": null,
                    "status": null
                }},
                "changes": {{
                    "title": null,
                    "description": null,
                    "due_date": null,
                    "due_time": null
                }}
            }}

            TARGET RULES:

            - Use "title" when the user refers to a TODO using words from
            its title.
            - Use due_date when the user identifies the TODO by its date.
            - Use status when the user identifies the TODO by its status.
            - Do not invent target information.
            - Use null when a target field is not available.

            CHANGES RULES:

            - Include only the fields that the user actually wants to change.
            - Do not change fields that the user did not mention.
            - due_date must be YYYY-MM-DD.
            - due_time must be HH:MM in 24-hour format.
            - Resolve relative dates using today's date.
            - "tomorrow" = today's date + 1 day.
            - "today" = today's date.
            - "day after tomorrow" = today's date + 2 days.
            - Convert AM/PM times into 24-hour format.
            - "morning", "afternoon", or "evening" alone must NOT create
            an exact time.
            - Understand English, Hindi, Hinglish, and mixed-language requests.

            IMPORTANT:
            - target tells us WHICH TODO to find.
            - changes tells us WHAT TO UPDATE.
            - Never put a change inside target.
            - Never put target information inside changes unless the user
            explicitly wants to modify that field.

            Examples:

            User:
            Mere ATM wale todo ki date 5 September kar do

            Output:
            {{
                "target": {{
                    "title": "ATM"
                }},
                "changes": {{
                    "due_date": "2026-09-05"
                }}
            }}

            User:
            Mere doodh wale todo ka time 6 PM kar do

            Output:
            {{
                "target": {{
                    "title": "milk"
                }},
                "changes": {{
                    "due_time": "18:00"
                }}
            }}

            User:
            Kal wale todo ka title change karke buy groceries kar do

            Output:
            {{
                "target": {{
                    "due_date": "2026-09-04"
                }},
                "changes": {{
                    "title": "buy groceries"
                }}
            }}

            Return JSON only.
            Do not return Markdown.
            Do not return explanations.
    """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content.strip()

        raw_data = json.loads(content)

        try:
            update_request = TodoUpdateRequest(**raw_data)

            print("UPDATE REQUEST:", update_request)

            return update_request

        except ValidationError as e:
            print("UPDATE REQUEST VALIDATION ERROR:", e)

            return {
                "error": e.errors()
            }

    # def update_from_prompt(self, prompt, user_id, client):
    #     # 1. Extract target + changes
    #     update_request = self.extract_update_request(
    #         prompt=prompt,
    #         client=client
    #     )

    #     # Extraction / validation failed
    #     if isinstance(update_request, dict) and "error" in update_request:
    #         return {
    #             "success": False,
    #             "stage": "update_extraction",
    #             "error": update_request["error"]
    #         }

    #     target = update_request.target
    #     changes = update_request.changes

    #     # 2. Find matching TODO
    #     todos = self.search_todos(
    #         user_id=user_id,
    #         title=target.title,
    #         due_date=target.due_date,
    #         status=target.status
    #     )

    #     # 3. No matching TODO
    #     if not todos:
    #         return {
    #             "success": False,
    #             "stage": "search",
    #             "error": "No matching todo found"
    #         }

    #     # 4. Multiple matching TODOs
    #     if len(todos) > 1:
    #         return {
    #             "success": False,
    #             "stage": "search",
    #             "error": "Multiple matching todos found",
    #             "matches": [
    #                 {
    #                     "id": todo.id,
    #                     "title": todo.title,
    #                     "due_date": todo.due_date,
    #                     "due_time": todo.due_time
    #                 }
    #                 for todo in todos
    #             ]
    #         }

    #     # 5. Exactly one TODO found
    #     todo = todos[0]

    #     # 6. Update TODO
    #     updated_todo = self.update_todo(
    #         todo_id=todo.id,
    #         user_id=user_id,
    #         todo_data=changes
    #     )

    #     if not updated_todo:
    #         return {
    #             "success": False,
    #             "stage": "update",
    #             "error": "Todo could not be updated"
    #         }

    #     return updated_todo
    
    def update_from_prompt(self, prompt, user_id, client):
        # 1. Extract target + changes
        update_request = self.extract_update_request(
            prompt=prompt,
            client=client
        )

        if (
            isinstance(update_request, dict)
            and "error" in update_request
        ):
            return update_request

        target = update_request.target
        changes = update_request.changes

        # 2. Convert target title into keywords
        title_keywords = (
            target.title.split()
            if target.title
            else []
        )

        # 3. Retrieve candidate TODOs
        candidates = self.search_candidates(
            user_id=user_id,
            title_keywords=title_keywords,
            due_date=target.due_date,
            status=target.status
        )

        print("CANDIDATES:", candidates)

        if not candidates:
            return {
                "success": False,
                "stage": "search",
                "error": "No matching todo candidates found"
            }

        # 4. Ask LLM to choose the correct candidate
        match = self.match_todo_candidate(
            target=target,
            candidates=candidates,
            client=client
        )
        
        print("MATCH RESULT:", match)

        if (
            isinstance(match, dict)
            and "error" in match
        ):
            return match

        if match.decision == "NO_MATCH":
            return {
                "success": False,
                "stage": "matching",
                "error": "No matching todo found",
                "reason": match.reason
            }
        
        if match.decision == "AMBIGUOUS":

            ambiguous_todos = []

            candidate_lookup = {
                todo.id: todo
                for todo in candidates
            }

            for candidate in match.candidates:
                todo = candidate_lookup[candidate.todo_id]

                ambiguous_todos.append({
                    "id": todo.id,
                    "title": todo.title,
                    "due_date": todo.due_date,
                    "due_time": todo.due_time,
                    "status": todo.status
                })

            return {
                "success": False,
                "stage": "matching",
                "error": "Multiple matching todos found",
                "reason": match.reason,
                "candidates": ambiguous_todos
            }

        # MATCHED
        updated_todo = self.update_todo(
            todo_id=match.todo_id,
            user_id=user_id,
            todo_data=changes
        )

        if not updated_todo:
            return {
                "success": False,
                "stage": "update",
                "error": "Todo could not be updated"
            }

        return updated_todo
        
    def search_candidates(self, user_id: int, title_keywords: list[str], due_date=None, status: str | None = None):
        return self.repository.search_candidates(
            user_id=user_id,
            title_keywords=title_keywords,
            due_date=due_date,
            status=status
        )
        
    def match_todo_candidate(self, target, candidates, client):
        candidate_data = [
            {
                "id": todo.id,
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
            for todo in candidates
        ]

        system_prompt = """
    You are a TODO candidate matching assistant for NEXORA.

    Your job is to determine which existing TODO, if any,
    the user is referring to.

    You will receive:
    1. The original user request.
    2. Candidate TODOs retrieved from the database.

    For every candidate, assign a relevance score from 0.0 to 1.0.

    Scoring guidance:

    - 1.0 = extremely strong match
    - 0.8 = strong match
    - 0.6 = plausible match
    - 0.4 = weak match
    - 0.0 = unrelated

    IMPORTANT:

    - Evaluate the meaning of the user's request, not just exact words.
    - Understand English, Hindi, Hinglish, and mixed-language requests.
    - Do NOT force a winner.
    - If two or more candidates are similarly relevant,
    mark the result as AMBIGUOUS.
    - If no candidate is relevant, mark the result as NO_MATCH.
    - Only mark MATCHED when one candidate is clearly more relevant
    than the others.
    - Never invent a TODO ID.
    - Every returned TODO ID must exist in the candidate list.

    IMPORTANT MATCHING RULE:

    Use ONLY the TARGET information to determine which existing
    TODO the user is referring to.
    
    - If the target is broad, such as "AI", and multiple candidates
    are equally relevant, return AMBIGUOUS.
    - Do not select a candidate merely because its current due_date
    matches a date mentioned in the requested change.
    - A requested change is never evidence that the candidate is the target.

    Do NOT use any requested changes as evidence for matching.

    For example:

    User request:
    "AI wala todo ki date 22 September kar do"

    Target:
    {
        "title": "AI"
    }

    Change:
    {
        "due_date": "2026-09-22"
    }

    The date 2026-09-22 is a NEW value to be applied.
    It must NOT be used to identify the existing TODO.

    Only information inside TARGET can be used to identify
    the existing TODO.

    Return ONLY valid JSON in this format:

    {
        "decision": "MATCHED",
        "todo_id": 2,
        "candidates": [
            {
                "todo_id": 1,
                "score": 0.40
            },
            {
                "todo_id": 2,
                "score": 0.93
            }
        ],
        "reason": "The phrase 'AI course' strongly matches the course assignment."
    }

    Possible decisions:

    MATCHED
    AMBIGUOUS
    NO_MATCH

    For AMBIGUOUS:

    {
        "decision": "AMBIGUOUS",
        "todo_id": null,
        "candidates": [
            {
                "todo_id": 1,
                "score": 0.88
            },
            {
                "todo_id": 2,
                "score": 0.90
            }
        ],
        "reason": "Both candidates are similarly relevant."
    }

    For NO_MATCH:

    {
        "decision": "NO_MATCH",
        "todo_id": null,
        "candidates": [
            {
                "todo_id": 1,
                "score": 0.20
            },
            {
                "todo_id": 2,
                "score": 0.15
            }
        ],
        "reason": "None of the candidates clearly matches the request."
    }
    """

        user_prompt = f"""
        TARGET TODO REFERENCE:

        {target.model_dump_json(indent=2)}

        CANDIDATE TODOS:

        {json.dumps(candidate_data, indent=2)}
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        content = response.choices[0].message.content.strip()

        try:
            raw_data = json.loads(content)

            result = TodoMatchResult(**raw_data)

        except (json.JSONDecodeError, ValidationError) as e:

            return {
                "success": False,
                "stage": "matching_validation",
                "error": str(e)
            }

        # Make sure LLM returned only valid candidate IDs
        candidate_ids = {
            todo.id for todo in candidates
        }

        for candidate in result.candidates:
            if candidate.todo_id not in candidate_ids:
                return {
                    "success": False,
                    "stage": "matching_validation",
                    "error": (
                        f"LLM returned invalid TODO ID: "
                        f"{candidate.todo_id}"
                    )
                }

        # Sort candidates by score
        ranked = sorted(
            result.candidates,
            key=lambda x: x.score,
            reverse=True
        )

        if not ranked:
            return {
                "success": False,
                "stage": "matching",
                "error": "No candidate scores returned"
            }

        best = ranked[0]
        second = ranked[1] if len(ranked) > 1 else None

        # Our application decides whether the result is actually clear.
        MIN_SCORE = 0.75
        MIN_GAP = 0.15

        if best.score < MIN_SCORE:
            result.decision = "NO_MATCH"
            result.todo_id = None

        elif second and (best.score - second.score) < MIN_GAP:
            result.decision = "AMBIGUOUS"
            result.todo_id = None

        else:
            result.decision = "MATCHED"
            result.todo_id = best.todo_id

        result.candidates = ranked

        print("MATCH RESULT:", result)
        
        if self.is_broad_target_ambiguous(target=target,candidates=candidates):
            result.decision = "AMBIGUOUS"
            result.todo_id = None

            print("MATCH RESULT:", result)

            return result

        return result
    
    def is_broad_target_ambiguous(self, target, candidates):
        if not target.title:
            return False

        target_words = {
            word.lower()
            for word in target.title.split()
            if len(word) > 2
        }

        if not target_words:
            return False

        matching_candidates = []

        for todo in candidates:

            title_words = {
                word.lower()
                for word in todo.title.split()
            }

            overlap = target_words.intersection(title_words)

            if overlap:
                matching_candidates.append(
                    (todo.id, len(overlap))
                )

        if len(matching_candidates) <= 1:
            return False

        max_overlap = max(
            overlap
            for _, overlap in matching_candidates
        )

        best_candidates = [
            todo_id
            for todo_id, overlap in matching_candidates
            if overlap == max_overlap
        ]

        return len(best_candidates) > 1
    
    def extract_delete_request(self, prompt, client):
        today = date.today().isoformat()

        system_prompt = f"""
    You are a TODO deletion target extraction assistant for NEXORA.

    Today's date is: {today}

    Your job is to identify WHICH existing TODO the user wants
    to delete.

    Return ONLY valid JSON in exactly this format:

    {{
        "target": {{
            "title": null,
            "due_date": null,
            "status": null
        }}
    }}

    Rules:

    - target tells us which existing TODO should be deleted.
    - title should contain useful words that identify the TODO.
    - due_date should be used when the user identifies the TODO
    by its date.
    - status should be used when the user identifies it by status.
    - Resolve relative dates using today's date.
    - "tomorrow" = today's date + 1 day.
    - "today" = today's date.
    - Do not invent information.
    - Understand English, Hindi, Hinglish, and mixed-language requests.
    - Return JSON only.
    - Do not return explanations.

    Examples:

    User:
    Mera ATM wala todo hata do

    Output:
    {{
        "target": {{
            "title": "ATM"
        }}
    }}

    User:
    28 August wala todo delete kar do

    Output:
    {{
        "target": {{
            "due_date": "2026-08-28"
        }}
    }}

    User:
    Mera pending milk wala todo remove kar do

    Output:
    {{
        "target": {{
            "title": "milk",
            "status": "pending"
        }}
    }}

    Return JSON only.
    """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content.strip()

        try:
            raw_data = json.loads(content)

            delete_request = TodoDeleteRequest(
                **raw_data
            )

            print(
                "DELETE REQUEST:",
                delete_request
            )

            return delete_request

        except (
            json.JSONDecodeError,
            ValidationError
        ) as e:

            return {
                "success": False,
                "stage": "delete_extraction",
                "error": str(e)
            }
            
    def delete_from_prompt(self, prompt, user_id, client):
        # 1. Extract target
        delete_request = self.extract_delete_request(
            prompt=prompt,
            client=client
        )

        if (
            isinstance(delete_request, dict)
            and "error" in delete_request
        ):
            return delete_request

        target = delete_request.target

        # 2. Create search keywords
        title_keywords = (
            target.title.split()
            if target.title
            else []
        )

        print("DELETE TITLE KEYWORDS:", title_keywords)

        # 3. Retrieve candidates
        candidates = self.search_candidates(
            user_id=user_id,
            title_keywords=title_keywords,
            due_date=target.due_date,
            status=target.status
        )

        print("DELETE CANDIDATES:", candidates)

        if not candidates:
            return {
                "success": False,
                "stage": "search",
                "error": "No matching todo found"
            }

        # 4. Semantic matching
        match = self.match_todo_candidate(
            target=target,
            candidates=candidates,
            client=client
        )

        if (
            isinstance(match, dict)
            and "error" in match
        ):
            return match

        # 5. No match
        if match.decision == "NO_MATCH":

            return {
                "success": False,
                "stage": "matching",
                "error": "No matching todo found",
                "reason": match.reason
            }

        # 6. Ambiguous
        if match.decision == "AMBIGUOUS":

            candidate_lookup = {
                todo.id: todo
                for todo in candidates
            }

            ambiguous_todos = []

            for candidate in match.candidates:

                todo = candidate_lookup[
                    candidate.todo_id
                ]

                ambiguous_todos.append({
                    "id": todo.id,
                    "title": todo.title,
                    "due_date": todo.due_date,
                    "due_time": todo.due_time,
                    "status": todo.status
                })

            return {
                "success": False,
                "stage": "matching",
                "error": "Multiple matching todos found",
                "reason": match.reason,
                "candidates": ambiguous_todos
            }

        # 7. Exact Todo selected
        deleted_todo = self.repository.soft_delete(
            todo_id=match.todo_id,
            user_id=user_id
        )

        if not deleted_todo:
            return {
                "success": False,
                "stage": "delete",
                "error": "Todo could not be deleted"
            }

        return deleted_todo
    
    def delete_todo(self, todo_id: int, user_id: int):
        return self.repository.soft_delete(
            todo_id=todo_id,
            user_id=user_id
        )

    def complete_todo(self, todo_id: int, user_id: int):
        return self.repository.complete(
            todo_id=todo_id,
            user_id=user_id
        )

    def extract_complete_request(self, prompt, client):
        today = date.today().isoformat()

        system_prompt = f"""
            You are a TODO completion target extraction assistant for NEXORA.

            Today's date is: {today}

            Your job is to identify WHICH existing TODO the user wants
            to mark as completed.

            Return ONLY valid JSON in exactly this format:

            {{
                "target": {{
                    "title": null,
                    "due_date": null,
                    "status": null
                }}
            }}

            Rules:

            - target tells us which existing TODO should be completed.
            - Use title when the user identifies the TODO by words from its title.
            - Use due_date when the user identifies the TODO by its date.
            - Do not invent information.
            - Resolve relative dates using today's date.
            - "today" = today's date.
            - "tomorrow" = today's date + 1 day.
            - Understand English, Hindi, Hinglish, and mixed-language requests.
            - Return JSON only.
            - Do not return explanations.

            Examples:

            User:
            Mera AI course wala todo complete kar do

            Output:
            {{
                "target": {{
                    "title": "AI course"
                }}
            }}

            User:
            Kal wala todo complete kar do

            Output:
            {{
                "target": {{
                    "due_date": "2026-09-20"
                }}
            }}

            User:
            Mera ATM withdrawal wala task complete kar do

            Output:
            {{
                "target": {{
                    "title": "ATM withdrawal"
                }}
            }}
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content.strip()

        try:
            raw_data = json.loads(content)

            complete_request = TodoDeleteRequest(
                **raw_data
            )

            print(
                "COMPLETE REQUEST:",
                complete_request
            )

            return complete_request

        except (
            json.JSONDecodeError,
            ValidationError
        ) as e:

            return {
                "success": False,
                "stage": "complete_extraction",
                "error": str(e)
            }
            
    def complete_from_prompt(
        self,
        prompt,
        user_id,
        client
    ):
            # 1. Extract target
            complete_request = self.extract_complete_request(
                prompt=prompt,
                client=client
            )
    
            if (
                isinstance(complete_request, dict)
                and "error" in complete_request
            ):
                return complete_request
    
            target = complete_request.target
    
            # 2. Candidate keywords
            title_keywords = (
                target.title.split()
                if target.title
                else []
            )
    
            # 3. Retrieve candidates
            candidates = self.search_candidates(
                user_id=user_id,
                title_keywords=title_keywords,
                due_date=target.due_date,
                status=target.status
            )
    
            print("COMPLETE CANDIDATES:", candidates)
    
            if not candidates:
                return {
                    "success": False,
                    "stage": "search",
                    "error": "No matching todo found"
                }
    
            # 4. Semantic matching
            match = self.match_todo_candidate(
                target=target,
                candidates=candidates,
                client=client
            )
    
            if isinstance(match, dict) and "error" in match:
                return match
    
            # 5. No match
            if match.decision == "NO_MATCH":
                return {
                    "success": False,
                    "stage": "matching",
                    "error": "No matching todo found",
                    "reason": match.reason
                }
    
            # 6. Ambiguous
            if match.decision == "AMBIGUOUS":
    
                candidate_lookup = {
                    todo.id: todo
                    for todo in candidates
                }
    
                ambiguous_todos = []
    
                for candidate in match.candidates:
                    todo = candidate_lookup[candidate.todo_id]
    
                    ambiguous_todos.append({
                        "id": todo.id,
                        "title": todo.title,
                        "due_date": todo.due_date,
                        "due_time": todo.due_time,
                        "status": todo.status
                    })
    
                return {
                    "success": False,
                    "stage": "matching",
                    "error": "Multiple matching todos found",
                    "reason": match.reason,
                    "candidates": ambiguous_todos
                }
    
            # 7. Exact Todo selected
            completed_todo = self.complete_todo(
                todo_id=match.todo_id,
                user_id=user_id
            )
    
            if not completed_todo:
                return {
                    "success": False,
                    "stage": "complete",
                    "error": "Todo could not be completed"
                }
    
            return completed_todo