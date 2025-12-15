# CI/CD Integration Guide

## Overview

`swiftui-migrate` is designed for CI/CD pipelines with:
- **Deterministic output** - Same results every run
- **Predictable exit codes** - Deprecated = fail, fragile = warn
- **Fast execution** - No compilation required
- **JSON output** - Machine-readable results

## Exit Code Behavior

### Default (Developer-Friendly)

| Scenario | Exit Code | CI Result |
|----------|-----------|-----------|
| No issues | 0 | ✅ Pass |
| Only fragile patterns | 0 | ✅ Pass (warnings) |
| Any deprecated APIs | 1 | ❌ Fail |
| Both deprecated + fragile | 1 | ❌ Fail |

### Strict Mode (`--fail-on-fragile`)

| Scenario | Exit Code | CI Result |
|----------|-----------|-----------|
| No issues | 0 | ✅ Pass |
| Any issues (deprecated or fragile) | 1 | ❌ Fail |

## GitHub Actions

### Basic Setup

**.github/workflows/swiftui-check.yml:**
```yaml
name: SwiftUI Check

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  scan:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install click rich
      
      - name: Scan for deprecated APIs
        run: |
          # This will fail CI if deprecated APIs found
          python -m swiftui_migrate.cli scan Sources/
```

### With JSON Output and Artifacts

```yaml
name: SwiftUI Check

on: [pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install swiftui-migrate
        run: pip install click rich
      
      - name: Scan Swift code
        id: scan
        run: |
          # Generate JSON report
          python -m swiftui_migrate.cli scan Sources/ --json > scan-results.json
          
          # Extract metrics
          TOTAL=$(jq '.summary.total' scan-results.json)
          DEPRECATED=$(jq '.summary.deprecated' scan-results.json)
          FRAGILE=$(jq '.summary.fragile' scan-results.json)
          
          echo "total=$TOTAL" >> $GITHUB_OUTPUT
          echo "deprecated=$DEPRECATED" >> $GITHUB_OUTPUT
          echo "fragile=$FRAGILE" >> $GITHUB_OUTPUT
          
          echo "### SwiftUI Scan Results" >> $GITHUB_STEP_SUMMARY
          echo "- Total issues: $TOTAL" >> $GITHUB_STEP_SUMMARY
          echo "- Deprecated APIs: $DEPRECATED" >> $GITHUB_STEP_SUMMARY
          echo "- Fragile patterns: $FRAGILE" >> $GITHUB_STEP_SUMMARY
      
      - name: Upload scan results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: swiftui-scan-results
          path: scan-results.json
      
      - name: Fail on deprecated APIs
        run: |
          # Run scan again to get proper exit code
          python -m swiftui_migrate.cli scan Sources/
```

### With PR Comments

```yaml
- name: Comment on PR
  if: github.event_name == 'pull_request' && steps.scan.outputs.total > 0
  uses: actions/github-script@v6
  with:
    script: |
      const fs = require('fs');
      const results = JSON.parse(fs.readFileSync('scan-results.json', 'utf8'));
      
      let comment = '### SwiftUI Migration Issues\n\n';
      comment += `Found ${results.summary.total} issues:\n`;
      comment += `- 🔴 Deprecated APIs: ${results.summary.deprecated}\n`;
      comment += `- 🟡 Fragile patterns: ${results.summary.fragile}\n\n`;
      
      if (results.summary.deprecated > 0) {
        comment += '#### Deprecated APIs (blocking):\n';
        results.findings
          .filter(f => f.category === 'deprecated')
          .slice(0, 5)
          .forEach(f => {
            comment += `- \`${f.rule_id}\` in ${f.file_path}:${f.line_number}\n`;
          });
      }
      
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: comment
      });
```

### Strict Mode (Fail on Everything)

```yaml
- name: Strict SwiftUI check
  run: |
    # Fail on any issues (deprecated + fragile)
    python -m swiftui_migrate.cli scan Sources/ --fail-on-fragile
```

### Target Specific iOS Version

```yaml
- name: Check iOS 17 migration readiness
  run: |
    python -m swiftui_migrate.cli scan Sources/ --min-ios 17
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
    - python -m swiftui_migrate.cli scan Sources/ --json > scan-results.json
    - python -m swiftui_migrate.cli scan Sources/  # Exit code check
  
  artifacts:
    when: always
    paths:
      - scan-results.json
    reports:
      junit: scan-results.json
```

## Bitbucket Pipelines

**bitbucket-pipelines.yml:**
```yaml
pipelines:
  default:
    - step:
        name: SwiftUI Check
        image: python:3.10
        script:
          - pip install click rich
          - python -m swiftui_migrate.cli scan Sources/ --json > scan-results.json
          - python -m swiftui_migrate.cli scan Sources/
        artifacts:
          - scan-results.json
```

## Jenkins

**Jenkinsfile:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('SwiftUI Check') {
            steps {
                sh '''
                    pip install click rich
                    python -m swiftui_migrate.cli scan Sources/ --json > scan-results.json
                    python -m swiftui_migrate.cli scan Sources/
                '''
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'scan-results.json', fingerprint: true
        }
    }
}
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
            python -m swiftui_migrate.cli scan Sources/ --json > scan-results.json
            python -m swiftui_migrate.cli scan Sources/
      
      - store_artifacts:
          path: scan-results.json

workflows:
  version: 2
  check:
    jobs:
      - swiftui-check
```

## Pre-commit Hook

**.git/hooks/pre-commit:**
```bash
#!/bin/bash

# Get staged Swift files
SWIFT_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.swift$')

if [ -z "$SWIFT_FILES" ]; then
    exit 0
fi

# Scan staged files
echo "Scanning Swift files for deprecated APIs..."
python -m swiftui_migrate.cli scan $SWIFT_FILES --category deprecated

# Exit with scan result
exit $?
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Performance Tips

### Large Repositories

For repos with 1000+ files:

```yaml
- name: Cache scan results
  uses: actions/cache@v3
  with:
    path: scan-results.json
    key: swiftui-scan-${{ hashFiles('**/*.swift') }}
    restore-keys: swiftui-scan-
```

### Exclude Directories

```bash
# Exclude common build artifacts
swiftui-migrate scan . --exclude Pods --exclude Build --exclude DerivedData
```

### Incremental Scans

Scan only changed files:

```bash
# Get changed files in PR
CHANGED_FILES=$(git diff --name-only origin/main...HEAD | grep '\.swift$')

if [ -n "$CHANGED_FILES" ]; then
    swiftui-migrate scan $CHANGED_FILES
fi
```

## Parsing JSON Output

### Extract Metrics

```bash
# Get counts
TOTAL=$(jq '.summary.total' scan-results.json)
DEPRECATED=$(jq '.summary.deprecated' scan-results.json)
FRAGILE=$(jq '.summary.fragile' scan-results.json)

echo "Found $DEPRECATED deprecated APIs and $FRAGILE fragile patterns"
```

### Filter by Category

```bash
# Get only deprecated API findings
jq '.findings[] | select(.category == "deprecated")' scan-results.json

# Get only fragile pattern findings
jq '.findings[] | select(.category == "fragile")' scan-results.json
```

### Group by File

```bash
# Count issues per file
jq -r '.findings[] | .file_path' scan-results.json | sort | uniq -c | sort -rn
```

### Group by Rule

```bash
# Count occurrences of each rule
jq -r '.findings[] | .rule_id' scan-results.json | sort | uniq -c | sort -rn
```

## Integration Examples

### Slack Notification

```bash
#!/bin/bash

# Run scan
python -m swiftui_migrate.cli scan Sources/ --json > results.json

DEPRECATED=$(jq '.summary.deprecated' results.json)
FRAGILE=$(jq '.summary.fragile' results.json)

if [ "$DEPRECATED" -gt 0 ] || [ "$FRAGILE" -gt 0 ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{
            \"text\": \"SwiftUI scan found $DEPRECATED deprecated APIs and $FRAGILE fragile patterns\"
        }" \
        $SLACK_WEBHOOK_URL
fi
```

### Email Report

```bash
#!/bin/bash

python -m swiftui_migrate.cli scan Sources/ --json > results.json

TOTAL=$(jq '.summary.total' results.json)

if [ "$TOTAL" -gt 0 ]; then
    echo "SwiftUI scan results attached" | \
        mail -s "SwiftUI Migration Report" \
        -a results.json \
        team@example.com
fi
```

## Troubleshooting

### Exit Code Not Propagating

```yaml
# ❌ Wrong - exit code lost
- run: swiftui-migrate scan Sources/ | tee results.txt

# ✅ Correct - preserve exit code
- run: |
    set -o pipefail
    swiftui-migrate scan Sources/ | tee results.txt
```

### Python Not Found

```yaml
- name: Ensure Python 3.10+
  uses: actions/setup-python@v4
  with:
    python-version: '3.10'
```

### Dependencies Not Installed

```yaml
- name: Install with cache
  uses: actions/setup-python@v4
  with:
    python-version: '3.10'
    cache: 'pip'
- run: pip install click rich
```

## Best Practices

1. **Use JSON output for parsing** - Human output may change
2. **Cache dependencies** - Speed up CI runs
3. **Fail fast on deprecated** - Default behavior is correct
4. **Warn on fragile** - Don't block PRs for fragile patterns
5. **Upload artifacts** - Keep scan results for review
6. **Add to PR checks** - Catch issues before merge
7. **Scan incrementally** - Only changed files for speed

## Example: Complete GitHub Actions Workflow

```yaml
name: SwiftUI Quality Check

on:
  pull_request:
  push:
    branches: [main]

jobs:
  swiftui-scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
      
      - name: Install swiftui-migrate
        run: pip install click rich
      
      - name: Scan (JSON)
        run: |
          python -m swiftui_migrate.cli scan Sources/ --json > results.json
      
      - name: Parse results
        id: results
        run: |
          echo "total=$(jq '.summary.total' results.json)" >> $GITHUB_OUTPUT
          echo "deprecated=$(jq '.summary.deprecated' results.json)" >> $GITHUB_OUTPUT
          echo "fragile=$(jq '.summary.fragile' results.json)" >> $GITHUB_OUTPUT
      
      - name: Add summary
        run: |
          echo "### SwiftUI Scan Results" >> $GITHUB_STEP_SUMMARY
          echo "- Total: ${{ steps.results.outputs.total }}" >> $GITHUB_STEP_SUMMARY
          echo "- Deprecated: ${{ steps.results.outputs.deprecated }}" >> $GITHUB_STEP_SUMMARY
          echo "- Fragile: ${{ steps.results.outputs.fragile }}" >> $GITHUB_STEP_SUMMARY
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: scan-results
          path: results.json
      
      - name: Check for deprecated APIs
        run: python -m swiftui_migrate.cli scan Sources/
```

This workflow:
- Generates JSON report
- Extracts metrics
- Adds summary to PR
- Uploads results
- Fails on deprecated APIs only
