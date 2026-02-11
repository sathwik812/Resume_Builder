# GitHub Upload Guide

## Quick Steps to Upload Your Code to GitHub

### Option 1: Using the Batch Script (Easiest)

1. Double-click `setup_git.bat` in your project folder
2. Follow the on-screen instructions
3. Create a new repository on GitHub.com
4. Copy the repository URL
5. Run these commands:
   ```bash
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

### Option 2: Manual Steps

1. **Initialize Git** (if not already done):
   ```bash
   git init
   ```

2. **Stage all files**:
   ```bash
   git add .
   ```

3. **Commit changes**:
   ```bash
   git commit -m "Initial commit: RAG-Powered Resume Builder"
   ```

4. **Create GitHub repository**:
   - Go to https://github.com/new
   - Enter repository name (e.g., "resume-builder")
   - Choose Public or Private
   - DO NOT initialize with README (we already have one)
   - Click "Create repository"

5. **Connect to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

### Important Security Notes

✅ **Safe to commit**:
- All Python code files
- README.md
- requirements.txt
- .gitignore
- .env.example

❌ **NEVER commit**:
- .env (contains your actual API keys)
- myenv/ folder (virtual environment)
- __pycache__/ folders

The `.gitignore` file is already configured to exclude these sensitive files.

### Verify Before Pushing

Check what will be committed:
```bash
git status
```

Make sure `.env` is NOT listed in the files to be committed!

### After Pushing

1. Your code will be visible on GitHub
2. Share the repository URL with others
3. Others can clone it using:
   ```bash
   git clone YOUR_REPO_URL
   ```

### Updating Code Later

When you make changes:
```bash
git add .
git commit -m "Description of changes"
git push
```

## Need Help?

- Git Documentation: https://git-scm.com/doc
- GitHub Guides: https://guides.github.com/
- Create GitHub Account: https://github.com/join
