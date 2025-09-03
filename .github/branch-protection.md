# Branch Protection Rules

Configure these branch protection rules in your GitHub repository settings:

## Main Branch Protection

Navigate to: Settings → Branches → Add rule

### Branch name pattern: `main`

#### ✅ Require a pull request before merging
- **Require approvals**: 1
- **Dismiss stale pull request approvals when new commits are pushed**: ✓
- **Require review from CODEOWNERS**: ✓ (if using CODEOWNERS)

#### ✅ Require status checks to pass before merging
- **Require branches to be up to date before merging**: ✓
- **Required status checks**:
  - `Validate Poetry Lock`
  - `Lint & Format Check`
  - `Type Checking`
  - `Security Scan`
  - `Test & Coverage`
  - `All Checks Passed`

#### ✅ Require conversation resolution before merging

#### ✅ Require signed commits (optional but recommended)

#### ✅ Require linear history (optional)

#### ✅ Include administrators (recommended for consistency)

#### ✅ Restrict who can push to matching branches
- Add specific users/teams who can push directly (emergency fixes only)

#### ❌ Allow force pushes (keep disabled)

#### ❌ Allow deletions (keep disabled)

## Develop Branch Protection (if using git-flow)

### Branch name pattern: `develop`

Similar to main but with relaxed rules:
- **Require approvals**: 0 (or 1 for larger teams)
- Same status checks as main
- Allow force pushes from administrators only

## Feature Branch Pattern

### Branch name pattern: `feature/*`

Minimal protection:
- No required reviews
- Basic status checks (lint, test)
- Allow deletions after merge

## Release Branch Pattern

### Branch name pattern: `release/*`

- **Require approvals**: 1
- All status checks required
- No force pushes
- Restrict push access to release managers

## Additional GitHub Settings

### General Repository Settings

1. **Default branch**: Set to `main`
2. **Allow merge commits**: ✓
3. **Allow squash merging**: ✓ (recommended)
4. **Allow rebase merging**: ✓
5. **Automatically delete head branches**: ✓

### Actions Settings

1. **Fork pull request workflows**: Require approval for first-time contributors
2. **Workflow permissions**: Read repository contents and write pull requests

### Security Settings

1. **Dependency graph**: Enable
2. **Dependabot alerts**: Enable
3. **Dependabot security updates**: Enable
4. **Secret scanning**: Enable
5. **Code scanning**: Set up with CodeQL

## Automation Rules

### Auto-merge (if enabled)

For dependabot PRs with passing checks:
```yaml
# .github/auto-merge.yml
- match:
    dependency_type: "development"
    update_type: "semver:patch"
```

### CODEOWNERS (optional)

Create `.github/CODEOWNERS`:
```
# Global owners
* @teamname

# Python files
*.py @python-team

# CI/CD
.github/ @devops-team

# Documentation
*.md @docs-team
```

## Enforcement

These rules ensure:
- ✅ No direct pushes to main
- ✅ All code is reviewed
- ✅ All checks pass before merge
- ✅ Consistent code quality
- ✅ Security vulnerabilities caught early
- ✅ Reproducible builds
- ✅ Clean git history

## Emergency Override

In case of critical production issues:
1. Create hotfix branch from main
2. Admin can temporarily disable protection
3. Apply fix with expedited review
4. Re-enable protection immediately after

## Monitoring

Set up notifications for:
- Failed CI/CD runs
- Security alerts
- Branch protection bypasses
- Force pushes (if any occur)