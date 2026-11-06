from httpx import AsyncClient


async def test_liveness(client: AsyncClient) -> None:
    response = await client.get("/health/live")

    assert response.json() == {"status": "ok"}


async def test_readiness_checks_the_database(client: AsyncClient) -> None:
    response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "up"}


async def test_request_id_is_propagated(client: AsyncClient) -> None:
    response = await client.get("/health/live", headers={"X-Request-ID": "abc-123"})

    assert response.headers["X-Request-ID"] == "abc-123"


async def test_request_id_is_generated_when_missing(client: AsyncClient) -> None:
    response = await client.get("/health/live")

    assert response.headers["X-Request-ID"]
