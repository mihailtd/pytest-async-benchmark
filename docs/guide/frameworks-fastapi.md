---
title: Benchmarking FastAPI & HTTP APIs
description: High-precision in-process benchmarking for FastAPI and Starlette endpoints using httpx ASGITransport.
---

# Benchmarking FastAPI & HTTP APIs

When testing FastAPI or Starlette endpoints, launching an actual Uvicorn server over a local TCP socket (`http://127.0.0.1:8000`) introduces socket bind overhead, OS ephemeral port allocation, and network stack jitter.

Instead, you can benchmark FastAPI endpoints **in-process** using `httpx.AsyncClient` with `ASGITransport`. This communicates directly over Python async memory buffers with zero network overhead.

## Setup & Fixture Pattern

Define your FastAPI app and provide a persistent `AsyncClient` fixture so connection transport initialization isn't benchmarked:

```python
import asyncio
from collections.abc import AsyncIterator
from fastapi import FastAPI
import httpx
import pytest

app = FastAPI()

USERS = {i: {"id": i, "name": f"user_{i}"} for i in range(1, 100)}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    await asyncio.sleep(0.001)  # Simulate DB lookup
    return USERS.get(user_id)


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    # In-process ASGI transport: no server, no TCP ports, no network stack
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
```

## Latency Distribution Benchmark

Measure the full latency distribution of an endpoint:

```python
@pytest.mark.asyncio
async def test_get_user_latency(async_benchmark, client):
    async def call_endpoint():
        resp = await client.get("/users/42")
        assert resp.status_code == 200
        return resp.json()

    result = await async_benchmark(call_endpoint)

    assert result["p95"] < 0.004  # 95% of requests complete under 4ms
    assert result["ops"] > 300  # Over 300 requests per second
```

## Concurrent Load Benchmarking

Simulate concurrent traffic to find bottlenecks under load:

```python
@pytest.mark.asyncio
async def test_endpoint_concurrency(async_benchmark, client):
    # 25 requests in flight simultaneously, 200 total requests
    stats = await async_benchmark.concurrent(
        lambda: client.get("/users/42"),
        concurrency=25,
        total=200,
        leak_check=True,
    )

    assert stats.errors == 0
    assert stats.p95 < 0.010  # 95th percentile stays under 10ms under load
    assert stats.loop_lag < 0.005  # Event loop scheduler lag under 5ms
```

## Comparing API Implementations (A vs B)

Evaluate refactors (such as resolving N+1 query patterns or switching serializers):

```python
from pytest_async_benchmark import a_vs_b_comparison


@app.get("/v1/items")
async def list_items_v1():
    # N+1 fetch pattern
    items = []
    for i in range(50):
        await asyncio.sleep(0.0001)
        items.append(i)
    return items


@app.get("/v2/items")
async def list_items_v2():
    # Batched fetch pattern
    await asyncio.sleep(0.0005)
    return list(range(50))


@pytest.mark.asyncio
async def test_api_optimization(client):
    winner, diff_pct, (res_v1, res_v2) = await a_vs_b_comparison(
        lambda: client.get("/v1/items"),
        lambda: client.get("/v2/items"),
        rounds=10,
    )

    assert winner == 'lambda: client.get("/v2/items")'
    assert diff_pct > 60.0  # Batched endpoint is at least 60% faster
```
