# Release Guide for pytest-async-benchmark

This guide explains how to release new versions of pytest-async-benchmark to PyPI using GitHub Actions and trusted publishing.

## 🚀 Quick Release (Recommended)

For most releases, follow these simple steps:

1. **Prepare the release:**
   ```bash
   # Make sure you're on main and up to date
   git checkout main
   git pull origin main
   
   # Update version in pyproject.toml and __init__.py
   # Follow semantic versioning: MAJOR.MINOR.PATCH
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

4. **Create GitHub release:**
   - Go to https://github.com/your-username/pytest-async-benchmark/releases
   - Click "Create a new release"
   - Select the tag you just pushed
   - Add release notes describing changes
   - Click "Publish release"

5. **Automated publishing:**
   - GitHub Actions will automatically test and publish to PyPI
   - Monitor the workflow progress in the Actions tab
   - Package will be available at https://pypi.org/project/pytest-async-benchmark/

## 📋 Pre-Release Checklist

Before creating a release, ensure:

- [ ] All tests pass locally and in CI
- [ ] Version numbers are updated consistently
- [ ] README.md is up to date
- [ ] CHANGELOG.md has entries for the new version (if applicable)
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
- GitHub release publication
- Manual workflow dispatch with version input

**Steps:**
1. **Validate Release:** Check version consistency and run comprehensive tests
2. **Test Matrix:** Run tests on Python 3.9-3.13
3. **Build and Publish:** Build package and publish to PyPI using trusted publishing
4. **Post-Release:** Verify availability and create summary

## 🔐 PyPI Trusted Publishing Setup

**⚠️ Important:** You must configure PyPI trusted publishing before releasing.

### 1. PyPI Configuration

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the details:
   - **PyPI Project Name:** `pytest-async-benchmark`
   - **Owner:** `your-username` (your GitHub username)
   - **Repository name:** `pytest-async-benchmark`
   - **Workflow name:** `release.yml`
   - **Environment name:** (leave blank)

### 2. Update Workflow Files

Replace `your-username` in both workflow files with your actual GitHub username:

```yaml
if: github.repository_owner == 'your-actual-username'
```

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
- Use format: `1.0.0b1`, `1.0.0rc1`
- GitHub will automatically detect as pre-release
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
- Verify trusted publishing is configured correctly
- Check that repository owner matches in workflow files
- Ensure you have the correct permissions

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
# Create GitHub release with bug fix notes
```

### Minor Release (New Feature)

```bash
# Add new feature, update version from 1.0.1 to 1.1.0
git add .
git commit -m "feat: add support for custom timeout configuration"
git tag v1.1.0
git push origin main --tags
# Create GitHub release with feature description
```

### Major Release (Breaking Changes)

```bash
# Breaking change, update version from 1.1.0 to 2.0.0
git add .
git commit -m "feat!: redesign API for better async support

BREAKING CHANGE: AsyncBenchmarkRunner.run() now returns BenchmarkResult object instead of dict"
git tag v2.0.0
git push origin main --tags
# Create GitHub release with changelog
```
