#!/usr/bin/env python3
"""
Quart API Comparison Example

This example demonstrates how to use pytest-async-benchmark to compare
different API endpoints, simulating v1 vs v2 performance comparisons.
"""

import asyncio
from quart import Quart, jsonify, request
import pytest

app = Quart(__name__)
)
USER_DATA = {
    str(i): {
        "id": i,
        "name": f"User {i}",
        "email": f"user{i}@example.com",
        "age": 20 + (i % 40),
        "created_at": "2024-01-01T00:00:00Z",
    }
    for i in range(1, 1001)
}


@app.route("/api/v1/users/<user_id>")
async def get_user_v1(user_id: str):
    """Version 1: Simple user lookup with full data."""
    await asyncio.sleep(0.001)

    if user_id in USER_DATA:
        return jsonify(USER_DATA[user_id])
    return jsonify({"error": "User not found"}), 404


@app.route("/api/v2/users/<user_id>")
async def get_user_v2(user_id: str):
    """Version 2: Optimized user lookup with selective fields."""
    await asyncio.sleep(0.0005)

    if user_id in USER_DATA:
        user = USER_DATA[user_id]
        return jsonify({"id": user["id"], "name": user["name"], "email": user["email"]})
    return jsonify({"error": "User not found"}), 404


@app.route("/api/v1/users")
async def list_users_v1():
    """Version 1: List all users (inefficient)."""
    await asyncio.sleep(0.005)

    limit = int(request.args.get("limit", 50))
    users = list(USER_DATA.values())[:limit]
    return jsonify({"users": users, "total": len(USER_DATA)})


@app.route("/api/v2/users")
async def list_users_v2():
    """Version 2: Paginated user listing (optimized)."""
    await asyncio.sleep(0.002)

    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))

    users = list(USER_DATA.values())[offset : offset + limit]
    minimal_users = [{"id": u["id"], "name": u["name"]} for u in users]

    return jsonify(
        {
            "users": minimal_users,
            "total": len(USER_DATA),
            "limit": limit,
            "offset": offset,
        }
    )


class TestAPIComparison:
    """Test suite for comparing API endpoint performance."""

    @pytest.fixture(scope="session")
    async def app_server(self):
        """Start the Quart test server."""
        return app.test_client()

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=10, iterations=100)
    async def test_user_lookup_v1(self, async_benchmark, app_server):
        """Benchmark v1 user lookup endpoint."""

        async def benchmark_v1_lookup():
            async with app_server as client:
                response = await client.get("/api/v1/users/42")
                assert response.status_code == 200
                data = await response.get_json()
                assert data["id"] == 42
                assert "email" in data
                assert "created_at" in data

        await async_benchmark(benchmark_v1_lookup)

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=10, iterations=100)
    async def test_user_lookup_v2(self, async_benchmark, app_server):
        """Benchmark v2 user lookup endpoint."""

        async def benchmark_v2_lookup():
            async with app_server as client:
                response = await client.get("/api/v2/users/42")
                assert response.status_code == 200
                data = await response.get_json()
                assert data["id"] == 42
                assert "email" in data

        await async_benchmark(benchmark_v2_lookup)

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=5, iterations=50)
    async def test_user_listing_v1(self, async_benchmark, app_server):
        """Benchmark v1 user listing endpoint."""

        async def benchmark_v1_listing():
            async with app_server as client:
                response = await client.get("/api/v1/users?limit=10")
                assert response.status_code == 200
                data = await response.get_json()
                assert len(data["users"]) == 10
                assert "total" in data

        await async_benchmark(benchmark_v1_listing)

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=5, iterations=50)
    async def test_user_listing_v2(self, async_benchmark, app_server):
        """Benchmark v2 user listing endpoint."""

        async def benchmark_v2_listing():
            async with app_server as client:
                response = await client.get("/api/v2/users?limit=10&offset=0")
                assert response.status_code == 200
                data = await response.get_json()
                assert len(data["users"]) == 10
                assert "total" in data
                assert "limit" in data

        await async_benchmark(benchmark_v2_listing)


async def manual_comparison_example():
    """Example of manually running and comparing benchmarks."""
    from pytest_async_benchmark.comparison import BenchmarkComparator
    from rich.console import Console

    console = Console()
    console.print("🚀 Starting Manual API Comparison\n")

    client = app.test_client()
    comparator = BenchmarkComparator(console)

    async def benchmark_v1():
        async with client as c:
            response = await c.get("/api/v1/users/123")
            return response.status_code == 200

    async def benchmark_v2():
        async with client as c:
            response = await c.get("/api/v2/users/123")
            return response.status_code == 200

    await comparator.add_scenario(
        "API v1 User Lookup",
        benchmark_v1,
        rounds=10,
        iterations=50,
        description="Legacy user lookup with full data",
    )

    await comparator.add_scenario(
        "API v2 User Lookup",
        benchmark_v2,
        rounds=10,
        iterations=50,
        description="Optimized user lookup with selective fields",
    )

    comparator.display_pairwise_comparison(
        "API v1 User Lookup",
        "API v2 User Lookup",
        title="🔥 API Version Performance Comparison",
    )

    comparator.display_performance_grades()

    fastest = comparator.get_fastest_scenario()
    console.print(f"\n🏆 Fastest: [green]{fastest['name']}[/green]")


async def comprehensive_api_comparison():
    """Compare multiple endpoints across versions using the new comparator."""
    from pytest_async_benchmark.comparison import BenchmarkScenario, quick_compare
    from rich.console import Console

    console = Console()
    console.print("🏁 Comprehensive API Performance Analysis\n")

    client = app.test_client()

    async def single_user_v1():
        async with client as c:
            response = await c.get("/api/v1/users/100")
            return response.status_code == 200

    async def single_user_v2():
        async with client as c:
            response = await c.get("/api/v2/users/100")
            return response.status_code == 200

    async def user_list_v1():
        async with client as c:
            response = await c.get("/api/v1/users?limit=20")
            return response.status_code == 200

    async def user_list_v2():
        async with client as c:
            response = await c.get("/api/v2/users?limit=20&offset=0")
            return response.status_code == 200

    scenarios = [
        BenchmarkScenario(
            "Single User v1",
            single_user_v1,
            rounds=10,
            iterations=100,
            description="v1 endpoint with full user data",
        ),
        BenchmarkScenario(
            "Single User v2",
            single_user_v2,
            rounds=10,
            iterations=100,
            description="v2 endpoint with selective fields",
        ),
        BenchmarkScenario(
            "User List v1",
            user_list_v1,
            rounds=5,
            iterations=30,
            description="v1 listing with complete user objects",
        ),
        BenchmarkScenario(
            "User List v2",
            user_list_v2,
            rounds=5,
            iterations=30,
            description="v2 listing with pagination and minimal data",
        ),
    ]

    comparator = await quick_compare(
        scenarios, title="🚀 Complete API Performance Analysis", console=console
    )

    console.print("\n")
    comparator.display_pairwise_comparison(
        "Single User v1", "Single User v2", title="👤 Single User Endpoint Comparison"
    )

    console.print("\n")
    comparator.display_pairwise_comparison(
        "User List v1", "User List v2", title="📋 User Listing Endpoint Comparison"
    )

    results = comparator.export_results()
    console.print(f"\n📊 Exported {len(results)} benchmark results for analysis")


async def load_testing_simulation():
    """Simulate load testing with different concurrency levels."""
    from pytest_async_benchmark.comparison import a_vs_b_comparison
    from rich.console import Console

    console = Console()
    console.print("⚡ Load Testing Simulation\n")

    client = app.test_client()

    async def light_load():
        tasks = []
        async with client as c:
            for _ in range(5):
                task = asyncio.create_task(c.get("/api/v2/users/100"))
                tasks.append(task)

            responses = await asyncio.gather(*tasks)
            return all(r.status_code == 200 for r in responses)

    async def heavy_load():
        tasks = []
        async with client as c:
            for _ in range(20):
                task = asyncio.create_task(c.get("/api/v2/users/100"))
                tasks.append(task)

            responses = await asyncio.gather(*tasks)
            return all(r.status_code == 200 for r in responses)

    await a_vs_b_comparison(
        "Light Load (5 concurrent)",
        light_load,
        "Heavy Load (20 concurrent)",
        heavy_load,
        rounds=5,
        iterations=10,
        console=console,
    )


if __name__ == "__main__":
    print("🔥 Quart API Comparison Examples")
    print("================================")
    print()
    print("To run the pytest benchmarks:")
    print("  pytest examples/quart_api_comparison.py -v")
    print()
    print("Running manual comparison examples...")

    asyncio.run(manual_comparison_example())
    print("\n" + "=" * 50 + "\n")
    asyncio.run(comprehensive_api_comparison())
    print("\n" + "=" * 50 + "\n")
    asyncio.run(load_testing_simulation())
