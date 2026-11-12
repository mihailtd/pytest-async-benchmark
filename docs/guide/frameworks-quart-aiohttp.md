---
title: Benchmarking Quart & Aiohttp
description: Performance testing for Quart microframeworks and Aiohttp server/client architectures.
---

# Benchmarking Quart & Aiohttp

`pytest-async-benchmark` works with any ASGI, WSGI, or native coroutine architecture. Here is how to benchmark Quart and Aiohttp applications.

## Quart Benchmarking

Quart provides an asynchronous test client (`app.test_client()`) that executes endpoints directly on the asyncio event loop:

```python
import asyncio
import pytest
from quart import Quart, jsonify

app = Quart(__name__)


@app.route("/items/<int:item_id>")
async def get_item(item_id: int):
    await asyncio.sleep(0.001)
    return jsonify({"item_id": item_id, "status": "ok"})


@pytest.fixture
async def quart_client():
    async with app.test_client() as client:
        yield client


@pytest.mark.asyncio
async def test_quart_endpoint(async_benchmark, quart_client):
    async def request():
        response = await quart_client.get("/items/123")
        assert response.status_code == 200
        return await response.get_json()

    result = await async_benchmark(request)

    assert result["p95"] < 0.005
    assert result["ops"] > 250
```

## Aiohttp Client Benchmarking

When testing external upstream API integrations with `aiohttp.ClientSession`, pass the persistent session to your benchmark to avoid measuring TCP connection handshake setup:

```python
import aiohttp
import pytest


@pytest.fixture
async def http_session():
    connector = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=connector) as session:
        yield session


@pytest.mark.asyncio
async def test_aiohttp_fetch(async_benchmark, http_session):
    async def fetch():
        async with http_session.get("http://localhost:8080/health") as resp:
            assert resp.status == 200
            return await resp.text()

    result = await async_benchmark(fetch)
    assert result["mean"] < 0.010
```

For concurrent load testing against a mock server:

```python
@pytest.mark.asyncio
async def test_aiohttp_concurrency(async_benchmark, http_session):
    stats = await async_benchmark.concurrent(
        lambda: http_session.get("http://localhost:8080/health"),
        concurrency=30,
        total=300,
        timeout=1.0,
    )

    assert stats.errors == 0
    assert stats.p99 < 0.020
```
