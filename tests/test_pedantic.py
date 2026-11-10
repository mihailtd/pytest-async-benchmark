"""Tests for pedantic mode benchmarking."""

import asyncio

import pytest


class MockDB:
    """Mock database connection for testing."""

    def __init__(self):
        self.closed = False
        self.operations = 0

    async def execute(self, query: str):
        await asyncio.sleep(0.001)
        self.operations += 1
        return f"result of {query}"

    async def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_pedantic_async_setup_teardown(async_benchmark):
    """Test pedantic mode with async setup and teardown."""
    setup_count = 0
    teardown_count = 0
    closed_dbs = []

    async def setup():
        nonlocal setup_count
        setup_count += 1
        return MockDB()

    async def teardown(db: MockDB):
        nonlocal teardown_count
        teardown_count += 1
        await db.close()
        closed_dbs.append(db)

    async def target(db: MockDB):
        assert not db.closed
        await db.execute("SELECT 1")

    result = await async_benchmark.pedantic(
        target, setup=setup, teardown=teardown, rounds=3, iterations=2
    )

    assert result["rounds"] == 3
    assert result["iterations"] == 2
    assert setup_count == 6  # 3 rounds * 2 iterations
    assert teardown_count == 6
    assert all(db.closed for db in closed_dbs)


@pytest.mark.asyncio
async def test_pedantic_timing_excludes_setup_teardown(async_benchmark):
    """Test that setup and teardown time are strictly excluded from timing."""

    async def slow_setup():
        # Setup takes 30ms
        await asyncio.sleep(0.03)
        return "data"

    async def slow_teardown(data):
        # Teardown takes 30ms
        await asyncio.sleep(0.03)

    async def fast_target(data):
        # Target takes only 1ms
        await asyncio.sleep(0.001)

    result = await async_benchmark.pedantic(
        fast_target,
        setup=slow_setup,
        teardown=slow_teardown,
        rounds=3,
        iterations=1,
    )

    # If setup (30ms) and teardown (30ms) were included, mean would be > 60ms.
    # Since they are excluded, mean should be well under 15ms.
    assert result["mean"] < 0.015, (
        f"Mean time {result['mean']}s includes setup/teardown overhead!"
    )


@pytest.mark.asyncio
async def test_pedantic_sync_setup_teardown(async_benchmark):
    """Test pedantic mode with sync setup and teardown."""
    state = []

    def sync_setup():
        state.append("setup")
        return {"id": 42}

    def sync_teardown(item):
        state.append("teardown")
        assert item["id"] == 42

    async def target(item):
        await asyncio.sleep(0.001)
        assert item["id"] == 42

    result = await async_benchmark.pedantic(
        target, setup=sync_setup, teardown=sync_teardown, rounds=2, iterations=1
    )

    assert result["rounds"] == 2
    assert state == ["setup", "teardown", "setup", "teardown"]


@pytest.mark.asyncio
async def test_pedantic_tuple_unpacking(async_benchmark):
    """Test that tuple returned from setup is unpacked as positional args."""

    def setup_tuple():
        return (10, 20)

    def teardown_tuple(a, b):
        assert a == 10
        assert b == 20

    async def target(a, b):
        await asyncio.sleep(0.001)
        assert a + b == 30

    result = await async_benchmark.pedantic(
        target, setup=setup_tuple, teardown=teardown_tuple, rounds=2
    )

    assert result["rounds"] == 2


@pytest.mark.asyncio
async def test_pedantic_with_args_and_kwargs(async_benchmark):
    """Test pedantic mode with explicit target arguments."""

    def setup():
        return "setup_item"

    async def target(prefix, setup_item, multiplier=1):
        await asyncio.sleep(0.001)
        assert prefix == "prefix"
        assert setup_item == "setup_item"
        assert multiplier == 5

    # Pass args as varargs and kwargs as extra kwargs
    result = await async_benchmark.pedantic(
        target,
        "prefix",
        multiplier=5,
        setup=setup,
        rounds=2,
    )
    assert result["rounds"] == 2

    # Pass args and kwargs explicitly
    result2 = await async_benchmark.pedantic(
        target,
        args=("prefix",),
        kwargs={"multiplier": 5},
        setup=setup,
        rounds=2,
    )
    assert result2["rounds"] == 2


@pytest.mark.asyncio
async def test_pedantic_warmup_rounds(async_benchmark):
    """Test that warmup rounds run setup and teardown without being timed."""
    runs = 0

    def setup():
        nonlocal runs
        runs += 1

    async def target():
        await asyncio.sleep(0.001)

    result = await async_benchmark.pedantic(
        target, setup=setup, rounds=2, iterations=1, warmup_rounds=2
    )

    assert result["rounds"] == 2
    assert runs == 4  # 2 warmup + 2 measurement


@pytest.mark.asyncio
async def test_pedantic_raises_on_sync_target(async_benchmark):
    """Test that sync target functions raise ValueError."""

    def sync_target():
        return 42

    with pytest.raises(ValueError, match="Function must be async"):
        await async_benchmark.pedantic(sync_target)


def test_pedantic_sync_interface(async_benchmark):
    """Test pedantic mode using sync interface (without await)."""
    cleaned = False

    def setup():
        return "conn"

    def teardown(conn):
        nonlocal cleaned
        cleaned = True

    async def target(conn):
        await asyncio.sleep(0.001)
        return conn

    result = async_benchmark.pedantic(target, setup=setup, teardown=teardown, rounds=2)

    assert result["rounds"] == 2
    assert cleaned is True
    assert "mean" in result
