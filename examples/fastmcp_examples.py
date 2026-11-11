"""Benchmarking FastMCP servers (MCP tools and resources) with pytest-async-benchmark.

`fastmcp.Client(server)` talks to the server object in memory: no subprocess,
no stdio, no HTTP. You measure your tool's code plus the MCP protocol layer.
Requires Python 3.10+ and `fastmcp`.

Run with:
    uv run pytest examples/fastmcp_examples.py -v
"""

import asyncio
from collections.abc import AsyncIterator

import pytest

pytest.importorskip("fastmcp")

from fastmcp import Client, FastMCP  # noqa: E402

from pytest_async_benchmark import a_vs_b_comparison  # noqa: E402

mcp = FastMCP("benchmark-demo")

DOCS = {f"doc-{i}": f"Document {i} about async benchmarking" for i in range(500)}


@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool
async def search_linear(query: str) -> list[str]:
    """Search documents by scanning every one."""
    await asyncio.sleep(0)
    return [key for key, text in DOCS.items() if query in text][:10]


INDEX: dict[str, list[str]] = {}
for _key, _text in DOCS.items():
    for _word in _text.split():
        INDEX.setdefault(_word, []).append(_key)


@mcp.tool
async def search_indexed(query: str) -> list[str]:
    """Search documents using a prebuilt inverted index."""
    await asyncio.sleep(0)
    return INDEX.get(query, [])[:10]


@mcp.resource("config://version")
def version() -> str:
    return "1.0.0"


@pytest.fixture
async def mcp_client() -> AsyncIterator[Client]:
    """One connected client per test, so the MCP handshake isn't benchmarked."""
    async with Client(mcp) as client:
        yield client


@pytest.mark.asyncio
async def test_tool_call_latency(async_benchmark, mcp_client):
    """Benchmark a full MCP tool call round trip."""

    async def call_add():
        result = await mcp_client.call_tool("add", {"a": 2, "b": 3})
        assert result.data == 5

    result = await async_benchmark(call_add, rounds=20, iterations=5)

    assert result["mean"] < 0.05  # 50ms budget, generous for CI runners


@pytest.mark.asyncio
async def test_resource_read_latency(async_benchmark, mcp_client):
    """Resources can be benchmarked the same way."""

    async def read_version():
        contents = await mcp_client.read_resource("config://version")
        assert contents

    result = await async_benchmark(read_version, rounds=10, iterations=5)
    assert result["mean"] < 0.05


@pytest.mark.asyncio
async def test_linear_vs_indexed_search(mcp_client):
    """Compare two tool implementations behind the same MCP interface."""

    async def linear():
        return await mcp_client.call_tool("search_linear", {"query": "async"})

    async def indexed():
        return await mcp_client.call_tool("search_indexed", {"query": "async"})

    comparator = await a_vs_b_comparison(
        "search_linear", linear, "search_indexed", indexed, rounds=5, iterations=10
    )

    assert len(comparator.results) == 2


@pytest.mark.asyncio
async def test_many_agents_calling_tools(async_benchmark, mcp_client):
    """Simulate 25 agents calling a tool at once through one MCP session."""

    async def call_search():
        await mcp_client.call_tool("search_indexed", {"query": "async"})

    result = await async_benchmark.concurrent(call_search, concurrency=25, total=250)

    assert result["errors"] == 0
    assert result["completed"] == 250
