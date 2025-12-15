# CI Integration

How to use swiftui-migrate in CI/CD pipelines.

## Quick Setup

**Never use `--annotate` in CI.** It modifies source files.

```yaml
# ✅ Correct - read-only scanning
- run: swiftui-migrate scan Sources/ --json

# ❌ Wrong - modifies files
- run: swiftui-migrate scan Sources/ --annotate
```

## Exit Codes

### Default behavior

| Scenario | Exit Code | CI Result |
|----------|-----------|-----------|
| No issues | 0 | ✅ Pass |
| Only fragile patterns | 0 | ✅ Pass (warnings) |
| Any deprecated APIs | 1 | ❌ Fail |
| Both types | 1 | ❌ Fail |

### Strict mode

Fail on any issue (including fragile patterns):

```bash
swiftui-migrate scan Sources/ --fail-on-fragile
```

## GitHub Actions

### Basic setup

**.github/workflows/swiftui-check.yml:**

```yaml
name: SwiftUI Check

on:
  push:
    branches: [main]
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install click rich
      
      - name: Scan for deprecated APIs
        run: swiftui-migrate scan Sources/
```

### With JSON output

```yaml
- name: Scan Swift code
  run: |
    swiftui-migrate scan Sources/ --json > results.json
    
    # Extract metrics
    TOTAL=$(jq '.summary.total' results.json)
    DEPRECATED=$(jq '.summary.deprecated' results.json)
    
    echo "Found $TOTAL issues ($DEPRECATED deprecated)"
    
    # Fail on deprecated APIs
    swiftui-migrate scan Sources/

- name: Upload results
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: scan-results
    path: results.json
```

### With PR comments

```yaml
- name: Comment on PR
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v6
  with:
    script: |
      const fs = require('fs');
      const results = JSON.parse(fs.readFileSync('results.json'));
      
      const comment = `
      ### SwiftUI Scan Results
      - Total: ${results.summary.total}
      - Deprecated: ${results.summary.deprecated}
      - Fragile: ${results.summary.fragile}
      `;
      
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: comment
      });
```

## GitLab CI

**.gitlab-ci.yml:**

```yaml
swiftui-check:
  image: python:3.10
  stage: test
  
  before_script:
    - pip install click rich
  
  script:
    - swiftui-migrate scan Sources/ --json > results.json
    - swiftui-migrate scan Sources/  # Exit code check
  
  artifacts:
    when: always
    paths:
      - results.json
```

## CircleCI

**.circleci/config.yml:**

```yaml
version: 2.1

jobs:
  swiftui-check:
    docker:
      - image: python:3.10
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: pip install click rich
      - run:
          name: Scan Swift code
          command: |
            swiftui-migrate scan Sources/ --json > results.json
            swiftui-migrate scan Sources/
      - store_artifacts:
          path: results.json

workflows:
  version: 2
  build:
    jobs:
      - swiftui-check
```

## Pre-commit Hook

Prevent committing new deprecated APIs:

**.git/hooks/pre-commit:**

```bash
#!/bin/bash

# Scan staged Swift files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep "\.swift$")

if [ -n "$STAGED_FILES" ]; then
    for FILE in $STAGED_FILES; do
        swiftui-migrate scan "$FILE" --category deprecated --json > /dev/null
        if [ $? -ne 0 ]; then
            echo "❌ Deprecated APIs detected in staged files"
            echo "Run: swiftui-migrate scan $FILE"
            exit 1
        fi
    done
fi

echo "✅ No deprecated APIs in staged files"
```

Make executable:

```bash
chmod +x .git/hooks/pre-commit
```

## Performance Tips

### Cache dependencies

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### Exclude build artifacts

```bash
swiftui-migrate scan Sources/ \
  --exclude Pods \
  --exclude Build \
  --exclude DerivedData
```

### Scan only changed files (PR context)

```bash
# Get changed files in PR
git diff --name-only origin/main...HEAD | grep "\.swift$" > changed_files.txt

# Scan only those files
while read file; do
  swiftui-migrate scan "$file"
done < changed_files.txt
```

## Parsing JSON Output

### Extract specific metrics

```bash
# Total issues
jq '.summary.total' results.json

# Deprecated count
jq '.summary.deprecated' results.json

# List all deprecated findings
jq '.findings[] | select(.category == "deprecated") | .file_path' results.json

# Group by rule
jq '[.findings | group_by(.rule_id)[] | {rule: .[0].rule_id, count: length}]' results.json
```

### Example output

```json
{
  "version": "0.1.0",
  "files_scanned": 42,
  "summary": {
    "total": 15,
    "deprecated": 10,
    "fragile": 5
  },
  "findings": [
    {
      "rule_id": "NAV001",
      "file_path": "/path/to/file.swift",
      "line_number": 15,
      "column": 8,
      "message": "NavigationView is deprecated",
      "category": "deprecated",
      "severity": "warning"
    }
  ]
}
```

## Common Patterns

### Fail only on deprecated APIs

```bash
swiftui-migrate scan Sources/ --category deprecated
```

Exit code 1 if any deprecated APIs found.

### Warn on everything, fail on nothing

```bash
swiftui-migrate scan Sources/ --json
```

Always exits 0. Parse JSON to extract issues.

### Strict mode (fail on anything)

```bash
swiftui-migrate scan Sources/ --fail-on-fragile
```

Exit code 1 if any issues found (deprecated or fragile).

### iOS version-specific checks

```bash
# Check iOS 17 readiness
swiftui-migrate scan Sources/ --min-ios 17
```

## Troubleshooting

**"Command not found" in CI**

Use module syntax:

```bash
python -m swiftui_migrate.cli scan Sources/
```

**Exit code always 0**

You might be using `--json` only. Add a second scan for exit code:

```bash
# Generate JSON
swiftui-migrate scan Sources/ --json > results.json

# Get exit code
swiftui-migrate scan Sources/
```

**Too slow in CI**

Exclude unnecessary directories:

```bash
swiftui-migrate scan . \
  --exclude Tests \
  --exclude Pods \
  --exclude Build
```

## Best Practices

1. **Run on PR, not every commit** - Saves CI time
2. **Fail on deprecated only** - Don't block on warnings
3. **Upload JSON artifacts** - Track issues over time
4. **Use caching** - Faster pip installs
5. **Scan changed files only** - Faster PR checks
6. **Never use --annotate** - Keep CI read-only

## Example: Complete GitHub Actions Workflow

```yaml
name: SwiftUI Migration Check

on:
  pull_request:
    paths:
      - '**.swift'

jobs:
  scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: pip-${{ hashFiles('**/requirements.txt') }}
      
      - name: Install swiftui-migrate
        run: pip install click rich
      
      - name: Scan Swift code
        id: scan
        run: |
          swiftui-migrate scan Sources/ --json > results.json
          
          TOTAL=$(jq '.summary.total' results.json)
          DEPRECATED=$(jq '.summary.deprecated' results.json)
          FRAGILE=$(jq '.summary.fragile' results.json)
          
          echo "total=$TOTAL" >> $GITHUB_OUTPUT
          echo "deprecated=$DEPRECATED" >> $GITHUB_OUTPUT
          echo "fragile=$FRAGILE" >> $GITHUB_OUTPUT
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: swiftui-scan-results
          path: results.json
      
      - name: Check for deprecated APIs
        run: swiftui-migrate scan Sources/ --category deprecated
      
      - name: Summary
        run: |
          echo "### SwiftUI Scan Results" >> $GITHUB_STEP_SUMMARY
          echo "- Total: ${{ steps.scan.outputs.total }}" >> $GITHUB_STEP_SUMMARY
          echo "- Deprecated: ${{ steps.scan.outputs.deprecated }}" >> $GITHUB_STEP_SUMMARY
          echo "- Fragile: ${{ steps.scan.outputs.fragile }}" >> $GITHUB_STEP_SUMMARY
```

This workflow:
- Runs on Swift file changes
- Caches pip dependencies
- Generates JSON output
- Uploads scan results
- Fails on deprecated APIs only
- Shows summary in GitHub UI
