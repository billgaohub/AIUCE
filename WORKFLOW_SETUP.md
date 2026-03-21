# GitHub Workflows 手动添加指南

由于 GitHub 安全限制，无法通过 Personal Access Token 推送 workflow 文件。请按以下步骤手动添加：

## 步骤 1: 访问仓库

打开: https://github.com/billgaohub/AIUCE

## 步骤 2: 创建 CI Workflow

1. 点击 **Actions** 标签
2. 点击 **"set up a workflow yourself"** 或 **"New workflow"**
3. 文件名输入: `ci.yml`
4. 复制以下内容：

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8 black
    
    - name: Test with pytest
      run: |
        pytest tests/ -v || true
```

5. 点击 **"Commit changes..."**
6. 选择 **"Commit directly to the main branch"**
7. 点击 **"Commit changes"**

## 步骤 3: 创建 Release Workflow

1. 再次点击 **Actions** → **"New workflow"**
2. 文件名输入: `release.yml`
3. 复制以下内容：

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        draft: false
        prerelease: false
```

4. 点击 **"Commit changes..."**
5. 点击 **"Commit changes"**

## 完成！

现在你的 AIUCE 仓库拥有完整的 CI/CD 工作流了！

---

**或者**，你可以创建一个具有 workflow 权限的 Token：

1. 访问: https://github.com/settings/tokens/new
2. 勾选 **repo** 和 **workflow** 权限
3. 使用新 Token 推送
