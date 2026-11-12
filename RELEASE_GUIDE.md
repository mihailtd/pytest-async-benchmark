# Release Guide for pytest-async-benchmark

This guide explains how to release new versions of pytest-async-benchmark to PyPI using GitHub Actions and trusted publishing.

## 🚀 Quick Release (Recommended)

For most releases, follow these simple steps:

1. **Prepare the release:**
   ```bash
   # Make sure you're on main and up to date
   git checkout main
   git pull origin main

   # Update version in pyproject.toml and src/pytest_async_benchmark/__init__.py
   # Follow semantic versioning: MAJOR.MINOR.PATCH
   # Rename "## [Unreleased]" in CHANGELOG.md to "## [1.0.0] - YYYY-MM-DD"
   ```

2. **Run release check:**
   ```bash
   python scripts/release-check.py
   ```

3. **Commit and tag:**
   ```bash
   git add .
   git commit -m "chore: bump version to v1.0.0"
   git tag v1.0.0
   git push origin main --tags
   ```

4. **Automated publishing:** pushing the tag is the whole release.
   - GitHub Actions tests the tag, publishes to PyPI, and creates the GitHub
     release, using that version's CHANGELOG.md section as the release notes
   - Don't create the GitHub release by hand: the workflow does it
   - Monitor the workflow progress in the [Actions tab](https://github.com/mihailtd/pytest-async-benchmark/actions)
   - Package will be available at https://pypi.org/project/pytest-async-benchmark/

## 📋 Pre-Release Checklist

Before creating a release, ensure:

- [ ] All tests pass locally and in CI
- [ ] Version numbers are updated consistently
- [ ] README.md is up to date
- [ ] CHANGELOG.md has a `## [X.Y.Z] - YYYY-MM-DD` section (it becomes the release notes)
- [ ] All example code works with the new version
- [ ] Documentation reflects any API changes
- [ ] No uncommitted changes in the repository

## 🔄 Workflow Overview

### 1. Test Publish Workflow (`test-publish.yml`)

**Triggers:**
- Push to main branch (when src/ or pyproject.toml changes)
- Manual workflow dispatch

**Purpose:**
- Tests package building and publishing to TestPyPI
- Validates installation from TestPyPI
- Provides a safe environment to test release process

**Usage:**
```bash
# Trigger manually from GitHub Actions tab
# or push changes to main branch
```

### 2. Release Workflow (`release.yml`)

**Triggers:**
- Pushing a `v*` tag
- Manual workflow dispatch with version input (publishes to PyPI, no GitHub release)

**Steps:**
1. **Validate Release:** Check version consistency and run tests, lint and type checks
2. **Test Matrix:** Run tests on Python 3.10-3.14
3. **Build and Publish:** Build package and publish to PyPI using trusted publishing
4. **GitHub Release:** Create the release with notes from CHANGELOG.md
5. **Post-Release:** Verify availability on PyPI and create summary

## 🔐 PyPI Trusted Publishing Setup

**⚠️ Important:** You must configure PyPI trusted publishing before releasing.

### 1. PyPI Configuration

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the details:
   - **PyPI Project Name:** `pytest-async-benchmark`
   - **Owner:** `mihailtd`
   - **Repository name:** `pytest-async-benchmark`
   - **Workflow name:** `release.yml`
   - **Environment name:** `release`

TestPyPI needs the same setup at https://test.pypi.org/manage/account/publishing/
with workflow `test-publish.yml` and no environment.

## 📦 Version Management

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/):

- **PATCH** (0.1.1): Bug fixes, no API changes
- **MINOR** (0.2.0): New features, backward compatible
- **MAJOR** (1.0.0): Breaking changes

### Version Update Locations

Update version in these files:
1. `pyproject.toml` - `version = "x.y.z"`
2. `src/pytest_async_benchmark/__init__.py` - `__version__ = "x.y.z"`

### Pre-release Versions

For beta/RC releases:
- Use [PEP 440](https://peps.python.org/pep-0440/) format: `1.0.0b1`, `1.0.0rc1` (not `1.0.0-rc1`)
- The workflow marks the GitHub release as a pre-release
- Will be marked as "Pre-release" on PyPI

## 🧪 Testing Releases

### Test PyPI

Test releases are automatically published to TestPyPI on main branch pushes:

```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pytest-async-benchmark
```

### Local Testing

Before releasing, test the package locally:

```bash
# Build package
uv build

# Install locally
pip install dist/pytest_async_benchmark-*.whl

# Test basic functionality
python -c "import pytest_async_benchmark; print(pytest_async_benchmark.__version__)"
```

## 🔧 Manual Release Process

If you need to release manually (not recommended):

1. **Build package:**
   ```bash
   uv build
   ```

2. **Upload to TestPyPI:**
   ```bash
   uv publish --repository testpypi
   ```

3. **Upload to PyPI:**
   ```bash
   uv publish
   ```

## 🐛 Troubleshooting

### Common Issues

**Version mismatch errors:**
- Ensure version is updated in both `pyproject.toml` and `__init__.py`
- Check that git tag matches the version

**PyPI upload fails:**
- Verify trusted publishing is configured correctly (owner, workflow and environment names)
- A version can only be uploaded once: bump the version instead of re-tagging

**Tests fail in CI:**
- Run `python scripts/release-check.py` locally first
- Fix any linting or formatting issues with `uv run ruff format .`

**Package not available after release:**
- PyPI indexing can take a few minutes
- Check the Actions tab for workflow status
- Verify the package exists at https://pypi.org/project/pytest-async-benchmark/

### Getting Help

- Check GitHub Actions logs for detailed error messages
- Review PyPI trusted publishing documentation
- Open an issue in the repository for persistent problems

## 📈 Post-Release Tasks

After a successful release:

1. **Announce the release:**
   - Update project README if needed
   - Share on relevant forums/social media
   - Update any dependent projects

2. **Monitor for issues:**
   - Watch for bug reports related to the new version
   - Monitor PyPI download statistics
   - Check for compatibility issues

3. **Plan next release:**
   - Review feedback and feature requests
   - Update project roadmap
   - Begin work on next version

## 🎯 Release Automation Benefits

Using GitHub Actions for releases provides:

- **Consistency:** Same process every time
- **Security:** No need to store PyPI tokens locally
- **Validation:** Comprehensive testing before release
- **Transparency:** All release steps are logged and visible
- **Rollback:** Easy to identify and fix issues
- **Multi-Python:** Automatic testing on all supported Python versions

## 📝 Examples

### Patch Release (Bug Fix)

```bash
# Fix a bug, update version from 1.0.0 to 1.0.1
git add .
git commit -m "fix: resolve issue with async timeout handling"
git tag v1.0.1
git push origin main --tags
# The workflow publishes to PyPI and creates the GitHub release
```

### Minor Release (New Feature)

```bash
# Add new feature, update version from 1.0.1 to 1.1.0
git add .
git commit -m "feat: add support for custom timeout configuration"
git tag v1.1.0
git push origin main --tags
# The workflow publishes to PyPI and creates the GitHub release
```

### Major Release (Breaking Changes)

```bash
# Breaking change, update version from 1.1.0 to 2.0.0
git add .
git commit -m "feat!: redesign API for better async support

BREAKING CHANGE: AsyncBenchmarkRunner.run() now returns BenchmarkResult object instead of dict"
git tag v2.0.0
git push origin main --tags
# The workflow publishes to PyPI and creates the GitHub release
```
