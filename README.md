# pytest-async-benchmark 🚀

Modern pytest benchmarking for async code with beautiful terminal output and advanced comparison tools.

## ✨ Features

- 🎯 **Async-First**: Designed specifically for benchmarking `async def` functions
- 🔌 **Pytest Integration**: Seamless integration as a pytest plugin
- 🎨 **Rich Output**: Beautiful terminal reporting!
- 📊 **Comprehensive Stats**: Min, max, mean, median, std dev, percentiles, and more
- ⚖️ **A vs B Comparisons**: Compare different implementations side-by-side
- 📈 **Multi-Scenario Analysis**: Benchmark multiple scenarios with detailed comparison tables
- 🎯 **Performance Grading**: Automatic performance scoring and analysis
- ⚡ **Auto Calibration**: Intelligent round and iteration detection
- 🔄 **Quick Compare**: One-line comparison utilities
- 🏆 **Winner Detection**: Automatic identification of best-performing implementation
- 🚀 **Easy to Use**: Simple fixture-based API

## 📦 Installation

```bash
uv add pytest-async-benchmark
# or
pip install pytest-async-benchmark
```

## 🚀 Quick Start

```python
import asyncio
import pytest

async def slow_async_operation():
    await asyncio.sleep(0.01)  # 10ms
    return "result"

def test_async_performance(async_benchmark):
    result = async_benchmark(slow_async_operation, rounds=5)
    
    # Your assertions here
    assert result['mean'] < 0.02  # Should complete in under 20ms
```

## 🎯 Core Usage Examples

### Basic Benchmarking

```python
def test_my_async_function(async_benchmark):
    async def my_function():
        # Your async code here
        await some_async_operation()
        return result
    
    # Benchmark with default settings (5 rounds, 1 iteration each)
    stats = async_benchmark(my_function)
    
    # Access comprehensive timing statistics
    print(f"Mean execution time: {stats['mean']:.3f}s")
    print(f"Standard deviation: {stats['stddev']:.3f}s")
    print(f"95th percentile: {stats['p95']:.3f}s")
```

### Advanced Configuration

```python
def test_with_custom_settings(async_benchmark):
    result = async_benchmark(
        my_async_function,
        rounds=10,        # Number of rounds to run
        iterations=5,     # Iterations per round
        warmup_rounds=2   # Warmup rounds before measurement
    )
```

### With Function Arguments

```python
def test_with_args(async_benchmark):
    async def process_data(data, multiplier=1):
        # Process the data
        await asyncio.sleep(0.01)
        return len(data) * multiplier
    
    result = async_benchmark(
        process_data,
        "test_data",      # positional arg
        multiplier=2,     # keyword arg
        rounds=3
    )
```

## ⚖️ A vs B Comparison Features

### Quick Comparison

```python
from pytest_async_benchmark import quick_compare

async def algorithm_v1():
    await asyncio.sleep(0.002)  # 2ms
    return "v1_result"

async def algorithm_v2():
    await asyncio.sleep(0.0015)  # 1.5ms - optimized
    return "v2_result"

# Quick one-liner comparison
def test_algorithm_comparison():
    winner, results = quick_compare(algorithm_v1, algorithm_v2, rounds=5)
    assert winner == "algorithm_v2"  # v2 should be faster
```

### Detailed A vs B Analysis

```python
from pytest_async_benchmark import a_vs_b_comparison

def test_detailed_comparison():
    # Compare with beautiful terminal output
    a_vs_b_comparison(
        "Original Algorithm", algorithm_v1,
        "Optimized Algorithm", algorithm_v2,
        rounds=8, iterations=20
    )
```

### Multi-Scenario Benchmarking

```python
from pytest_async_benchmark import BenchmarkComparator

def test_multi_scenario():
    comparator = BenchmarkComparator()
    
    # Add multiple scenarios
    comparator.add_scenario(
        "Database Query v1", db_query_v1,
        rounds=5, iterations=10,
        description="Original database implementation"
    )
    
    comparator.add_scenario(
        "Database Query v2", db_query_v2,
        rounds=5, iterations=10,
        description="Optimized with connection pooling"
    )
    
    # Run comparison and get results
    results = comparator.run_comparison()
    
    # Beautiful comparison table automatically displayed
    # Access programmatic results
    fastest = results.get_fastest_scenario()
    assert fastest.name == "Database Query v2"
```

## 📊 Comprehensive Statistics

Each benchmark returns detailed statistics:

```python
{
    'min': 0.001234,      # Minimum execution time
    'max': 0.005678,      # Maximum execution time  
    'mean': 0.002456,     # Mean execution time
    'median': 0.002123,   # Median execution time
    'stddev': 0.000234,   # Standard deviation
    'p50': 0.002123,      # 50th percentile (median)
    'p90': 0.003456,      # 90th percentile
    'p95': 0.004123,      # 95th percentile
    'p99': 0.004789,      # 99th percentile
    'rounds': 5,          # Number of rounds executed
    'iterations': 1,      # Number of iterations per round
    'raw_times': [...],   # List of raw timing measurements
    'grade': 'A',         # Performance grade (A-F)
    'grade_score': 87.5   # Numeric grade score (0-100)
}
```

## 🎨 Beautiful Terminal Output

### Basic Benchmark Output

```
🚀 Async Benchmark Results: test_my_function
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Metric      ┃ Value      ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Min         │ 10.234ms   │
│ Max         │ 15.678ms   │
│ Mean        │ 12.456ms   │
│ Median      │ 12.123ms   │
│ Std Dev     │ 1.234ms    │
│ 95th %ile   │ 14.567ms   │
│ 99th %ile   │ 15.234ms   │
│ Grade       │ A (87.5)   │
│ Rounds      │ 5          │
│ Iterations  │ 1          │
└─────────────┴────────────┘
✅ Benchmark completed successfully!
```

### A vs B Comparison Output

```
⚖️  A vs B Comparison Results
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Scenario                ┃ Algorithm A ┃ Algorithm B ┃ Winner    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Mean Time              │ 2.456ms     │ 1.789ms     │ B 🏆      │
│ Median Time            │ 2.234ms     │ 1.678ms     │ B 🏆      │
│ 95th Percentile        │ 3.456ms     │ 2.345ms     │ B 🏆      │
│ Standard Deviation     │ 0.567ms     │ 0.234ms     │ B 🏆      │
│ Performance Grade      │ B (76.2)    │ A (89.1)    │ B 🏆      │
│ Improvement            │ -           │ 27.2%       │ -         │
└─────────────────────────┴─────────────┴─────────────┴───────────┘
🏆 Winner: Algorithm B (27.2% faster)
```

## 🏗️ Project Structure

```
pytest-async-benchmark/
├── src/
│   └── pytest_async_benchmark/
│       ├── __init__.py          # Main exports and API
│       ├── plugin.py            # Pytest plugin and fixtures
│       ├── runner.py            # Core benchmarking engine
│       ├── display.py           # Rich terminal output formatting
│       ├── stats.py             # Statistical calculations
│       ├── utils.py             # Utility functions
│       ├── analytics.py         # Performance analysis tools
│       └── comparison.py        # A vs B comparison functionality
├── examples/
│   ├── pytest_examples.py      # Comprehensive pytest usage examples
│   ├── quart_api_comparison.py  # Real-world API endpoint comparison
│   └── comparison_examples.py   # Advanced comparison features demo
├── tests/
│   ├── test_async_bench.py      # Core functionality tests
│   ├── test_comparison.py       # Comparison feature tests
│   ├── test_demo.py             # Demo test cases
│   └── conftest.py              # Test configuration
├── pyproject.toml               # Package configuration
└── README.md                    # This file
```

## 📚 Example Files Guide

### 🔧 [`examples/pytest_examples.py`](examples/pytest_examples.py)
Comprehensive pytest usage examples including:
- Basic benchmarking with the `async_benchmark` fixture
- Advanced configuration options
- Performance assertions and testing patterns
- Using markers for benchmark organization

### 🌐 [`examples/quart_api_comparison.py`](examples/quart_api_comparison.py)
Real-world API endpoint comparison demo featuring:
- Quart web framework setup
- API v1 vs v2 endpoint benchmarking
- Live server testing with actual HTTP requests
- Performance regression detection

### ⚖️ [`examples/comparison_examples.py`](examples/comparison_examples.py)
Advanced comparison features showcase:
- Multi-scenario benchmark comparisons
- A vs B testing with detailed analysis
- Performance grading and scoring
- Statistical comparison utilities

## 🌐 Real-World Examples

### FastAPI Endpoint Benchmarking

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

app = FastAPI()

@app.get("/api/data")
async def get_data():
    # Simulate database query
    await asyncio.sleep(0.005)
    return {"data": "example"}

def test_fastapi_endpoint_performance(async_benchmark):
    async def make_request():
        with TestClient(app) as client:
            response = client.get("/api/data")
            return response.json()
    
    result = async_benchmark(make_request, rounds=10)
    assert result['mean'] < 0.1  # Should respond within 100ms
    assert result['grade'] in ['A', 'B']  # Should have good performance grade
```

### Quart API Endpoint Comparison

See the complete example in [`examples/quart_api_comparison.py`](examples/quart_api_comparison.py):

```python
from pytest_async_benchmark import a_vs_b_comparison
import asyncio
import aiohttp

async def test_api_v1():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5000/api/v1/data') as resp:
            return await resp.json()

async def test_api_v2():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5000/api/v2/data') as resp:
            return await resp.json()

# Compare API versions
a_vs_b_comparison(
    "API v1", test_api_v1,
    "API v2 (Optimized)", test_api_v2,
    rounds=10, iterations=5
)
```

### Database Query Benchmarking

```python
async def test_database_query_performance(async_benchmark):
    async def fetch_user_data(user_id):
        async with database.connection() as conn:
            return await conn.fetch_one(
                "SELECT * FROM users WHERE id = ?", user_id
            )
    
    result = async_benchmark(fetch_user_data, 123, rounds=5)
    assert result['mean'] < 0.05  # Should complete within 50ms
    assert result['p95'] < 0.1    # 95% of queries under 100ms
```

## 🎯 Using Markers

```python
@pytest.mark.async_benchmark
def test_performance(async_benchmark):
    # Your benchmark test
    result = async_benchmark(my_async_function)
    assert result is not None
```

## 📋 API Reference

### `async_benchmark(func, *args, rounds=None, iterations=None, warmup_rounds=1, **kwargs)`

**Parameters:**
- `func`: The async function to benchmark
- `*args`: Positional arguments to pass to the function
- `rounds`: Number of measurement rounds (default: 5)
- `iterations`: Number of iterations per round (default: 1)
- `warmup_rounds`: Number of warmup rounds before measurement (default: 1)
- `**kwargs`: Keyword arguments to pass to the function

**Returns:**
A dictionary with comprehensive statistics including min, max, mean, median, stddev, percentiles, performance grade, and raw measurements.

### Comparison Functions

- `quick_compare(func_a, func_b, **kwargs)`: Quick comparison returning winner and results
- `a_vs_b_comparison(name_a, func_a, name_b, func_b, **kwargs)`: Detailed comparison with terminal output
- `BenchmarkComparator`: Class for multi-scenario benchmarking and analysis

## 📋 Requirements

- Python ≥ 3.9
- pytest ≥ 8.3.5

Note: Rich (for beautiful terminal output) is automatically installed as a dependency.

## 🚀 Development

```bash
# Clone the repository
git clone https://github.com/yourusername/pytest-async-benchmark.git
cd pytest-async-benchmark

# Install dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run examples
uv run pytest examples/pytest_examples.py -v

# Test real-world Quart API comparison
uv run python examples/quart_api_comparison.py

# See advanced comparison features
uv run python examples/comparison_examples.py
```

### 🛠️ Code Quality and Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting:

```bash
# Check code for linting issues
uv run ruff check .

# Fix auto-fixable linting issues
uv run ruff check . --fix

# Check code formatting
uv run ruff format --check .

# Format code automatically
uv run ruff format .

# Run both linting and formatting in one go
uv run ruff check . --fix && uv run ruff format .

# Run all quality checks at once (linting, formatting, and tests)
uv run python scripts/quality-check.py
```

### 📋 Release Readiness Check

Before creating a release, verify everything is ready:

```bash
# Run comprehensive release check
uv run python scripts/release-check.py

# This checks:
# ✅ Git repository status
# ✅ Version consistency 
# ✅ Code formatting and linting
# ✅ Test suite passes
# ✅ Package builds successfully
# ✅ All required files exist
```

### 🚀 Quick Quality Check

Run all quality checks at once:

```bash
# Run linting, formatting, tests, and release checks
python scripts/quality-check.py

# This will:
# 🔧 Fix linting issues automatically
# 🎨 Format code with Ruff
# 🧪 Run the full test suite
# 📋 Check release readiness
```

## 🚀 Automated Releases

This project uses GitHub Actions for automated testing and publishing to PyPI:

- **Continuous Integration**: Tests run on every push for Python 3.9-3.13
- **Test Publishing**: Automatic uploads to TestPyPI for testing releases
- **Production Releases**: Secure publishing to PyPI using trusted publishing
- **Release Validation**: Comprehensive checks ensure package quality

### Creating a Release

1. Update version in `pyproject.toml` and `src/pytest_async_benchmark/__init__.py`
2. Run `uv run python scripts/release-check.py` to verify readiness
3. Create a git tag: `git tag v1.0.0 && git push origin v1.0.0`
4. Create a GitHub release to trigger automated PyPI publishing

See [RELEASE_GUIDE.md](RELEASE_GUIDE.md) for detailed release instructions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

*Built with ❤️ for the async Python community*
