---
title: Benchmarking FastMCP & AI Tool Servers
description: In-memory performance benchmarking for Model Context Protocol (MCP) tools and AI agent servers with FastMCP.
---

# Benchmarking FastMCP & AI Tool Servers

When building AI agents and Model Context Protocol (MCP) tool servers with [FastMCP](https://github.com/jlowin/fastmcp), tool execution latency directly limits agent decision loops.

Benchmarking tools through subprocesses or stdio pipes introduces shell spawn jitter. With `fastmcp.Client(server)`, you can benchmark MCP tools and resources **in-memory**, isolating schema parsing, Pydantic validation, and tool business logic.

## Setup Pattern

Define your FastMCP server and create an in-memory client fixture:

```python
import asyncio
from collections.abc import AsyncIterator
from fastmcp import Client, FastMCP
import pytest

mcp = FastMCP("agent-tools")

DOCS = {f"doc_{i}": f"Content for document {i} with details" for i in range(500)}


@mcp.tool
async def search_documents(query: str) -> list[str]:
    """Search documents matching query."""
    await asyncio.sleep(0.001)
    return [doc for doc in DOCS.values() if query in doc][:5]


@pytest.fixture
async def mcp_client() -> AsyncIterator[Client]:
    """In-memory client connection: zero subprocess or network overhead."""
    async with Client(mcp) as client:
        yield client
```

## Tool Execution Benchmark

Measure how fast an AI agent can invoke your tool:

```python
@pytest.mark.asyncio
async def test_tool_latency(async_benchmark, mcp_client):
    async def invoke_tool():
        return await mcp_client.call_tool("search_documents", {"query": "details"})

    result = await async_benchmark(invoke_tool)

    # Tool execution + MCP schema serialization
    assert result["p95"] < 0.005  # Under 5ms
    assert result["ops"] > 250
```

## Concurrent Tool Execution Under Load

When autonomous multi-agent systems run parallel tool calls, tool servers can face bursty concurrency:

```python
@pytest.mark.asyncio
async def test_concurrent_tool_burst(async_benchmark, mcp_client):
    stats = await async_benchmark.concurrent(
        lambda: mcp_client.call_tool("search_documents", {"query": "document"}),
        concurrency=15,
        total=150,
        leak_check=True,
    )

    assert stats.errors == 0
    assert stats.p95 < 0.012
    assert stats.loop_lag < 0.003
```

## Comparing Search Approaches (Linear vs Inverted Index)

Compare algorithmic approaches inside your MCP tools:

```python
from pytest_async_benchmark import a_vs_b_comparison

INDEX = {}
for doc_id, text in DOCS.items():
    for word in text.split():
        INDEX.setdefault(word, []).append(doc_id)


@mcp.tool
async def search_linear(query: str) -> list[str]:
    await asyncio.sleep(0)
    return [k for k, v in DOCS.items() if query in v][:10]


@mcp.tool
async def search_indexed(query: str) -> list[str]:
    await asyncio.sleep(0)
    return INDEX.get(query, [])[:10]


@pytest.mark.asyncio
async def test_compare_search_tools(mcp_client):
    winner, diff_pct, _ = await a_vs_b_comparison(
        lambda: mcp_client.call_tool("search_linear", {"query": "document"}),
        lambda: mcp_client.call_tool("search_indexed", {"query": "document"}),
        rounds=10,
    )

    assert (
        winner
        == 'lambda: mcp_client.call_tool("search_indexed", {"query": "document"})'
    )
    assert diff_pct > 80.0  # Indexed lookup is drastically faster
```
