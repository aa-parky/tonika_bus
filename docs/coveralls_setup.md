# Setting Up Coveralls for tonika_bus

This guide explains how to integrate Coveralls.io with your GitHub repository to track test coverage over time.

## What is Coveralls?

Coveralls is a web service that tracks your code coverage over time. It integrates with your CI pipeline to automatically receive coverage reports and provides:

- **Coverage badges** for your README
- **Historical tracking** of coverage changes
- **Pull request comments** showing coverage impact
- **Visual reports** of which lines are covered

## Important: No Impact on Local Development

**Coveralls only runs in CI—it will NOT affect your local testing workflow at all.**

Your local commands remain exactly the same:
```bash
pytest                    # Run tests locally
pytest --cov             # Generate coverage locally
```

Coveralls only receives coverage data when tests run on GitHub Actions.

## Setup Steps

### 1. Sign Up for Coveralls

1. Go to [https://coveralls.io](https://coveralls.io)
2. Click "Sign in with GitHub"
3. Authorize Coveralls to access your repositories

### 2. Add Your Repository

1. In Coveralls dashboard, click "Add Repos"
2. Find `aa-parky/tonika_bus` in the list
3. Toggle it ON
4. Click on the repo name to view settings

### 3. Get Your Repo Token (Optional)

For public repos, the GitHub token is sufficient. For private repos:

1. In Coveralls, go to your repo settings
2. Copy the "Repo Token"
3. Add it to GitHub Secrets:
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `COVERALLS_REPO_TOKEN`
   - Value: (paste the token)

### 4. Push Your Changes

Once you push the `.github/workflows/ci.yml` file, GitHub Actions will:

1. Run your tests
2. Generate coverage report (`coverage.xml`)
3. Upload it to Coveralls automatically

### 5. Add Coverage Badge to README

After your first CI run, add this badge to your `README.md`:

```markdown
[![Coverage Status](https://coveralls.io/repos/github/aa-parky/tonika_bus/badge.svg?branch=main)](https://coveralls.io/github/aa-parky/tonika_bus?branch=main)
```

Place it near the top with your other badges.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. You push code to GitHub                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  2. GitHub Actions runs CI workflow                         │
│     - Runs pytest with --cov flag                           │
│     - Generates coverage.xml                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Coveralls GitHub Action uploads coverage.xml            │
│     - Uses GITHUB_TOKEN (automatic)                         │
│     - Sends to Coveralls API                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Coveralls processes and displays coverage               │
│     - Updates coverage percentage                           │
│     - Shows line-by-line coverage                           │
│     - Comments on PRs with coverage changes                 │
└─────────────────────────────────────────────────────────────┘
```

## Local vs CI Coverage

| Aspect                | Local (`pytest --cov`)       | CI + Coveralls                    |
|-----------------------|------------------------------|-----------------------------------|
| **Runs where**        | Your machine                 | GitHub Actions servers            |
| **Output**            | Terminal + htmlcov/          | Coveralls.io dashboard            |
| **Tracking**          | One-time snapshot            | Historical tracking over time     |
| **PR integration**    | None                         | Automatic PR comments             |
| **Badge**             | No                           | Yes, for README                   |

## Troubleshooting

### Coverage not uploading

Check the GitHub Actions log:
1. Go to your repo → Actions tab
2. Click on the latest workflow run
3. Look for the "Upload coverage to Coveralls" step
4. Check for error messages

### Coverage shows 0%

Make sure:
- Tests are actually running (`pytest` step succeeds)
- `coverage.xml` is being generated
- The `source` in `.coveragerc` matches your package name

### Private repo issues

If you have a private repo, you need to:
1. Get the Coveralls repo token
2. Add it as `COVERALLS_REPO_TOKEN` in GitHub Secrets
3. Update the workflow to use it:
   ```yaml
   - name: Upload coverage to Coveralls
     uses: coverallsapp/github-action@v2
     with:
       github-token: ${{ secrets.COVERALLS_REPO_TOKEN }}
   ```

## Benefits for Your Project

1. **Confidence**: See exactly what code is tested
2. **Accountability**: Coverage changes are visible in PRs
3. **Professionalism**: Coverage badge shows quality commitment
4. **Community**: Contributors can see test coverage easily
5. **History**: Track coverage trends over time

## Next Steps

After Coveralls is set up:

1. Monitor coverage on each PR
2. Aim to maintain or improve coverage
3. Use Coveralls reports to find untested code
4. Add coverage requirements to CONTRIBUTING.md

---

**Remember**: Coveralls is a tool for visibility and accountability, not a replacement for good testing practices. High coverage is great, but meaningful tests are what really matter!
