"""Examples of pedantic mode benchmarking in pytest-async-benchmark.

Pedantic mode allows setup and teardown per iteration while excluding
their execution time from benchmark measurements.
"""

import asyncio

import pytest


class SQLiteConnectionPool:
    """Simulated SQLite connection pool for benchmarking."""

    def __init__(self):
        self.active = False

    async def open(self):
        await asyncio.sleep(0.02)  # Simulates 20ms setup
        self.active = True

    async def query(self, sql: str):
        await asyncio.sleep(0.002)  # 2ms query to benchmark
        return [{"id": 1, "value": "data"}]

    async def close(self):
        await asyncio.sleep(0.01)  # Simulates 10ms cleanup
        self.active = False


class TestPedanticExamples:
    """Examples showing how to use async_benchmark.pedantic."""

    @pytest.mark.asyncio
    async def test_database_query_with_fresh_connection(self, async_benchmark):
        """Benchmark a query where each iteration gets a fresh connection pool."""

        async def setup():
            pool = SQLiteConnectionPool()
            await pool.open()
            return pool

        async def teardown(pool: SQLiteConnectionPool):
            await pool.close()

        async def run_query(pool: SQLiteConnectionPool):
            return await pool.query("SELECT * FROM items WHERE id = 1")

        # Setup (~20ms) and teardown (~10ms) are NOT counted in the benchmark result.
        # Only run_query (~2ms) is timed.
        result = await async_benchmark.pedantic(
            run_query,
            setup=setup,
            teardown=teardown,
            rounds=5,
            iterations=1,
        )

        assert result["mean"] < 0.01  # Target is ~2ms, well under 10ms
        assert result["rounds"] == 5

    @pytest.mark.asyncio
    async def test_sync_setup_with_parameters(self, async_benchmark):
        """Pedantic mode with sync setup and custom arguments."""

        def setup():
            return list(range(1000))

        async def process_batch(prefix: str, items: list[int]):
            await asyncio.sleep(0.001)
            return f"{prefix}:{len(items)}"

        result = await async_benchmark.pedantic(
            process_batch,
            "batch-1",
            setup=setup,
            rounds=3,
        )

        assert result["rounds"] == 3


if __name__ == "__main__":
    import sys

    pytest.main([__file__, "-v", *sys.argv[1:]])
