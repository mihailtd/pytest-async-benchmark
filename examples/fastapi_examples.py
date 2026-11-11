"""Benchmarking FastAPI endpoints with pytest-async-benchmark.

The app is called in-process through httpx's ASGITransport: no server, no
network, no ports. Requires Python 3.10+ and `fastapi` + `httpx`.

Run with:
    uv run pytest examples/fastapi_examples.py -v
"""

import asyncio
from collections.abc import AsyncIterator

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

import httpx  # noqa: E402
from fastapi import FastAPI  # noqa: E402

from pytest_async_benchmark import a_vs_b_comparison  # noqa: E402

app = FastAPI()

USERS = {i: {"id": i, "name": f"user-{i}"} for i in range(1, 101)}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    await asyncio.sleep(0.001)  # simulate a ~1ms database lookup
    return USERS[user_id]


@app.get("/v1/users")
async def list_users_v1():
    # v1: one "query" per user (N+1 pattern)
    results = []
    for user in USERS.values():
        await asyncio.sleep(0)  # yield per row, like a per-row fetch
        results.append(user)
    return results


@app.get("/v2/users")
async def list_users_v2():
    # v2: single batched "query"
    await asyncio.sleep(0)
    return list(USERS.values())


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    """One client for the whole test, so connection setup isn't benchmarked."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_get_user_latency(async_benchmark, client):
    """Benchmark a single endpoint and assert a latency budget."""

    async def fetch_user():
        response = await client.get("/users/42")
        assert response.status_code == 200
        return response.json()

    result = await async_benchmark(fetch_user, rounds=20, iterations=5)

    assert result["mean"] < 0.05  # 50ms budget, generous for CI runners


@pytest.mark.asyncio
@pytest.mark.async_benchmark(rounds=10, iterations=5)
async def test_list_users_with_marker(async_benchmark, client):
    """Same idea using marker syntax to configure the benchmark."""

    async def list_users():
        response = await client.get("/v2/users")
        assert len(response.json()) == 100

    result = await async_benchmark(list_users)
    assert result["rounds"] == 10


@pytest.mark.asyncio
async def test_v1_vs_v2_endpoint(client):
    """Compare two implementations of the same endpoint side by side."""

    async def v1():
        return (await client.get("/v1/users")).json()

    async def v2():
        return (await client.get("/v2/users")).json()

    comparator = await a_vs_b_comparison(
        "GET /v1/users (N+1)",
        v1,
        "GET /v2/users (batched)",
        v2,
        rounds=5,
        iterations=10,
    )

    assert len(comparator.results) == 2
