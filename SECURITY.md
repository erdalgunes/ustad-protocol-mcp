# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

1. **DO NOT** create a public GitHub issue
2. Email security details to: [security@example.com] (replace with actual email)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Measures

This project implements several security measures:

### Automated Security Scanning
- **Bandit**: Static security analysis on every commit
- **pip-audit**: Vulnerability scanning for dependencies
- **Safety**: Known security vulnerabilities check
- **Dependabot**: Automated dependency updates

### CI/CD Security
- Branch protection rules enforce code review
- All dependencies are pinned via `poetry.lock`
- Security scans run on every pull request
- Secrets are never logged or exposed

### Development Practices
- Type hints enforced via MyPy (reduces runtime errors)
- 80% minimum test coverage requirement
- Pre-commit hooks prevent sensitive data commits
- Regular dependency updates via Dependabot

## Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 5 business days
- **Resolution Target**: Based on severity:
  - Critical: 7 days
  - High: 14 days
  - Medium: 30 days
  - Low: 90 days

## Disclosure Policy

- Security issues are disclosed after a fix is available
- Credit given to reporters (unless anonymity requested)
- CVE assignment for significant vulnerabilities

## Security Checklist for Contributors

Before submitting code:
- [ ] Run `make security` locally
- [ ] No hardcoded secrets or credentials
- [ ] Input validation on all user data
- [ ] Dependencies updated to latest secure versions
- [ ] No use of deprecated or unsafe functions

## Contact

For security concerns, contact: [security@example.com]

For general issues, use GitHub Issues.