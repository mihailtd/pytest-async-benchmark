# Changelog

All notable changes to pytest-async-benchmark will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-05-28

### 🚀 Major Features
- **Backwards Compatibility**: Automatic interface detection supporting both sync and async usage patterns
- **pytest-asyncio Integration**: Full compatibility with pytest-asyncio plugin when available
- **Dual Interface Support**: Works with `await async_benchmark(...)` (with pytest-asyncio) or `result = async_benchmark(...)` (without)
- **Smart Detection**: Automatically detects pytest-asyncio availability and provides appropriate interface

### ✨ Added
- Automatic pytest-asyncio detection and interface switching
- Legacy sync interface support for backwards compatibility with v0.1.x
- Optional dependency configuration for pytest-asyncio
- Comprehensive backwards compatibility test suite
- `_SyncResultWrapper` class for seamless sync interface
- Enhanced documentation covering both usage patterns

### 🔧 Changed
- **NON-BREAKING**: pytest-asyncio moved from required to optional dependency
- `AsyncBenchmarkFixture.__call__` now returns different types based on environment
- Enhanced fixture to support both sync and async interfaces automatically
- Updated examples to show both usage patterns
- README updated with backwards compatibility documentation

### 🛠️ Fixed
- RuntimeError issues when pytest-asyncio not available
- Event loop management conflicts in different environments
- Compatibility issues with projects not using pytest-asyncio

### 📚 Documentation
- Added pytest-asyncio compatibility section to README
- Updated all code examples to demonstrate async/await usage
- Created dedicated pytest-asyncio showcase example
- Enhanced Quick Start guide with modern async patterns

### 🧪 Testing
- All 40 tests passing with pytest-asyncio integration
- Examples thoroughly tested and validated
- Comprehensive test coverage maintained

---

## [0.1.1] - 2025-05-27

### Initial Features
- Core async benchmarking functionality
- Rich console output with beautiful formatting
- Statistical analysis and comparison tools
- Multiple examples and comprehensive testing

### Core Components
- `AsyncBenchmarkFixture` for pytest integration
- `AsyncBenchmarkRunner` for timing execution
- `BenchmarkComparator` for performance analysis
- Rich-based display formatting

### Examples
- Basic pytest examples
- Quart API comparison
- Comparison analysis tools
- Statistical benchmarking patterns
