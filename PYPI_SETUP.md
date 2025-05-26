# 🚀 PyPI Trusted Publishing Setup Guide

This guide will help you set up trusted publishing for the `pytest-async-benchmark` package.

## 📋 Prerequisites

1. ✅ GitHub repository with the workflows
2. ✅ PyPI account: https://pypi.org/account/register/
3. ✅ TestPyPI account: https://test.pypi.org/account/register/

## 🔐 Step 1: Set Up Trusted Publishing on PyPI

### For Production Releases (PyPI)

1. **Go to PyPI**: https://pypi.org/
2. **Log in** to your account
3. **Navigate to**: Your account → Publishing → "Add a new pending publisher"
4. **Fill in the form**:
   ```
   PyPI Project Name: pytest-async-benchmark
   Owner: YOUR_GITHUB_USERNAME
   Repository name: pytest-async-benchmark
   Workflow name: release.yml
   Environment name: release
   ```
5. **Click "Add"**

### For Test Releases (TestPyPI)

1. **Go to TestPyPI**: https://test.pypi.org/
2. **Log in** to your account
3. **Navigate to**: Your account → Publishing → "Add a new pending publisher"
4. **Fill in the form**:
   ```
   PyPI Project Name: pytest-async-benchmark
   Owner: YOUR_GITHUB_USERNAME
   Repository name: pytest-async-benchmark
   Workflow name: test-publish.yml
   Environment name: (leave empty)
   ```
5. **Click "Add"**

## 🛡️ Step 2: Create GitHub Environment (Recommended)

1. **Go to your GitHub repository**
2. **Settings** → **Environments**
3. **Click "New environment"**
4. **Name**: `release`
5. **Configure protection rules**:
   - ✅ **Required reviewers**: Add yourself
   - ✅ **Deployment branches**: Selected branches → `main`
   - ⚙️ **Wait timer**: 5 minutes (optional)

## 🔧 Step 3: Update Workflow Configuration

Replace placeholders in the workflow files:

### Option A: Remove the restriction (allows anyone to trigger)
Remove or comment out these lines:
```yaml
# if: github.repository_owner == 'your-username'
```

### Option B: Add your GitHub username
Replace `your-username` with your actual GitHub username:
```yaml
if: github.repository_owner == 'your-actual-username'
```

## 🧪 Step 4: Test the Setup

### Test Publish Workflow
1. **Push changes** to the `main` branch
2. **Go to**: GitHub → Actions → "Test Publish to TestPyPI"
3. **Check the workflow** runs successfully
4. **Verify** the package appears on TestPyPI

### Manual Test Publish
1. **Go to**: GitHub → Actions → "Test Publish to TestPyPI"
2. **Click "Run workflow"**
3. **Enter test suffix** (e.g., "rc1")
4. **Click "Run workflow"**

## 🚀 Step 5: Create Your First Release

### Automatic Release (Recommended)
1. **Create a git tag**:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
2. **Create GitHub Release**:
   - Go to GitHub → Releases → "Create a new release"
   - Choose tag: `v0.1.0`
   - Release title: `v0.1.0`
   - Add release notes
   - Click "Publish release"

### Manual Release
1. **Go to**: GitHub → Actions → "Release to PyPI"
2. **Click "Run workflow"**
3. **Enter version**: `0.1.0`
4. **Click "Run workflow"**

## 🔍 Verification Checklist

- [ ] PyPI trusted publisher configured
- [ ] TestPyPI trusted publisher configured
- [ ] GitHub environment `release` created
- [ ] Workflow username updated or restriction removed
- [ ] Test publish workflow runs successfully
- [ ] Package appears on TestPyPI
- [ ] Release workflow ready for production

## 🆘 Troubleshooting

### "Trusted publishing exchange failure"
- ✅ Verify the project name matches exactly
- ✅ Check the repository owner/name is correct
- ✅ Ensure the workflow name is correct
- ✅ Verify the environment name matches (if used)

### "Permission denied"
- ✅ Check the workflow has `id-token: write` permission
- ✅ Verify the environment protection rules
- ✅ Ensure you're the repository owner or have admin access

### "Package already exists"
- ✅ Version conflicts: Update version in `pyproject.toml`
- ✅ TestPyPI conflicts: Use different test version suffix

## 📞 Support

If you encounter issues:
1. Check the [GitHub Actions logs](../../actions)
2. Review the [PyPI publishing guide](https://docs.pypi.org/trusted-publishing/using-a-publisher/)
3. Check the [workflow documentation](RELEASE_GUIDE.md)

---

**Happy Publishing! 🎉**
