---
title: Pedantic Mode (Setup & Teardown)
description: Isolate target execution time from database transactions, cache resets, and test fixture setup with async_benchmark.pedantic.
---

# Pedantic Mode (Setup & Teardown)

Many real-world asynchronous operations mutate state: inserting records into a database, writing to a message broker, or modifying in-memory caches.

Benchmarking these operations requires resetting state before and after each iteration. If you include the setup and teardown logic inside the measured block, your benchmark measures fixture churn rather than the performance of your business logic.

`async_benchmark.pedantic()` isolates execution timing: **setup and teardown hooks run on every iteration but their durations are completely excluded from measured statistics**.

## Basic Example: Database Inserts

```python
import asyncio
import pytest


# Simulated database connection
class MockDatabase:
    def __init__(self):
        self.rows = []

    async def insert(self, record_id: int, payload: dict):
        await asyncio.sleep(0.001)
        self.rows.append((record_id, payload))

    async def truncate(self):
        await asyncio.sleep(0.002)
        self.rows.clear()


db = MockDatabase()


@pytest.mark.asyncio
async def test_insert_performance(async_benchmark):
    # Setup runs before each iteration, teardown runs after each iteration
    async def setup_iteration():
        await db.truncate()
        return 42, {"name": "test_payload"}  # Returns arguments for the target

    async def teardown_iteration(record_id, payload):
        await db.truncate()

    result = await async_benchmark.pedantic(
        db.insert,
        setup=setup_iteration,
        teardown=teardown_iteration,
        rounds=10,
        iterations=1,
    )

    # Only db.insert was measured!
    # Truncate time (2ms per setup + 2ms per teardown) was excluded.
    assert result["p95"] < 0.003
```

## Argument Passing from Setup

Values returned by `setup` are automatically passed as positional arguments to both the target function and `teardown`:

1. **Single return value**: Passed as the first argument:
   ```python
   def setup():
       return "my-token"


   async def target(token): ...
   async def teardown(token): ...
   ```

2. **Tuple return value**: Automatically unpacked into multiple arguments:
   ```python
   def setup():
       return (101, "customer_name", True)


   async def target(id, name, active): ...
   async def teardown(id, name, active): ...
   ```

## Flexible Sync and Async Hooks

Setup and teardown functions can be synchronous or asynchronous in any combination:

| Target Function | Setup Hook | Teardown Hook | Supported? |
|---|---|---|---|
| `async def` | `async def` | `async def` | ✅ |
| `async def` | `def` (sync) | `async def` | ✅ |
| `async def` | `async def` | `def` (sync) | ✅ |
| `async def` | `def` (sync) | `def` (sync) | ✅ |

```python
def sync_setup():
    # Fast synchronous memory reset
    return {"counter": 0}


async def async_target(state):
    await asyncio.sleep(0.001)
    state["counter"] += 1


def sync_teardown(state):
    state.clear()


@pytest.mark.asyncio
async def test_mixed_hooks(async_benchmark):
    result = await async_benchmark.pedantic(
        async_target,
        setup=sync_setup,
        teardown=sync_teardown,
        rounds=5,
    )
    assert result["mean"] < 0.002
```

## Synchronous Interface Support

Pedantic mode works seamlessly in synchronous test functions without requiring `pytest-asyncio`:

```python
def test_pedantic_sync(async_benchmark):
    # Notice: def test_... and synchronous invocation
    result = async_benchmark.pedantic(
        async_target,
        setup=sync_setup,
        teardown=sync_teardown,
        rounds=5,
    )
    assert result["mean"] < 0.002
```
