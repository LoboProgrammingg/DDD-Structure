import uuid
from typing import Any

from httpx import AsyncClient


async def _create(client: AsyncClient, **overrides: Any) -> dict[str, Any]:
    response = await client.post("/api/v1/tasks", json={"title": "Modelar o domínio", **overrides})
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


async def test_create_returns_the_task_and_its_location(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/tasks",
        json={"title": "Escrever glossário", "priority": "high", "due_date": "2099-01-31"},
    )

    assert response.status_code == 201
    body = response.json()
    assert response.headers["location"] == f"/api/v1/tasks/{body['id']}"
    assert body["title"] == "Escrever glossário"
    assert body["priority"] == "high"
    assert body["status"] == "pending"
    assert body["due_date"] == "2099-01-31"
    assert body["version"] == 1


async def test_get_by_id(client: AsyncClient) -> None:
    created = await _create(client)

    response = await client.get(f"/api/v1/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


async def test_full_lifecycle(client: AsyncClient) -> None:
    task_id = (await _create(client))["id"]
    base = f"/api/v1/tasks/{task_id}"

    renamed = await client.post(f"{base}/rename", json={"title": "Modelar agregados"})
    reprioritized = await client.post(f"{base}/reprioritize", json={"priority": "urgent"})
    assigned = await client.post(f"{base}/assign", json={"assignee_id": "ana.souza"})
    started = await client.post(f"{base}/start")
    completed = await client.post(f"{base}/complete")

    assert renamed.json()["title"] == "Modelar agregados"
    assert reprioritized.json()["priority"] == "urgent"
    assert assigned.json()["assignee_id"] == "ana.souza"
    assert started.json()["status"] == "in_progress"
    assert completed.json()["status"] == "completed"
    assert completed.json()["completed_at"] is not None
    assert completed.json()["version"] == 6


async def test_cancel(client: AsyncClient) -> None:
    task_id = (await _create(client))["id"]

    response = await client.post(f"/api/v1/tasks/{task_id}/cancel")

    assert response.json()["status"] == "cancelled"


async def test_list_filters_and_paginates(client: AsyncClient) -> None:
    first = await _create(client, title="Primeira")
    await _create(client, title="Segunda")
    await client.post(f"/api/v1/tasks/{first['id']}/assign", json={"assignee_id": "ana"})

    everything = await client.get("/api/v1/tasks", params={"limit": 1})
    for_ana = await client.get("/api/v1/tasks", params={"assignee_id": "ana", "status": "pending"})

    assert everything.json()["total"] == 2
    assert len(everything.json()["items"]) == 1
    assert [item["title"] for item in for_ana.json()["items"]] == ["Primeira"]


async def test_invariant_violation_returns_problem_details(client: AsyncClient) -> None:
    response = await client.post("/api/v1/tasks", json={"title": "   "})

    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json() == {
        "type": "about:blank",
        "title": "Unprocessable Content",
        "status": 422,
        "detail": "O título da tarefa não pode ser vazio.",
        "code": "invalid_task_title",
        "instance": "/api/v1/tasks",
    }


async def test_business_rule_violation_returns_409(client: AsyncClient) -> None:
    task_id = (await _create(client))["id"]

    response = await client.post(f"/api/v1/tasks/{task_id}/start")

    assert response.status_code == 409
    assert response.json()["code"] == "task_not_assigned"


async def test_work_in_progress_limit_is_enforced(client: AsyncClient) -> None:
    for title in ("Primeira", "Segunda"):
        task_id = (await _create(client, title=title))["id"]
        await client.post(f"/api/v1/tasks/{task_id}/assign", json={"assignee_id": "ana"})
        last = await client.post(f"/api/v1/tasks/{task_id}/start")

    assert last.status_code == 409
    assert last.json()["code"] == "work_in_progress_limit_exceeded"


async def test_unknown_task_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/tasks/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


async def test_malformed_identifier_returns_422(client: AsyncClient) -> None:
    response = await client.post("/api/v1/tasks/123/complete")

    assert response.status_code == 422
    assert response.json()["code"] == "invalid_task_id"


async def test_request_schema_is_validated(client: AsyncClient) -> None:
    response = await client.post("/api/v1/tasks", json={"title": "x", "priority": "max"})

    assert response.status_code == 422
