# SwiftUI Migration Rule Engine - Quick Reference

## Installation
```bash
pip install -e .
```

## CLI Usage
```bash
# Scan project
swiftui-migrate scan ./Sources

# Get summary
swiftui-migrate scan ./Sources --format summary

# Export JSON
swiftui-migrate scan ./Sources --format json > report.json

# List all rules
swiftui-migrate rules
```

## Python API
```python
from pathlib import Path
from swiftui_migrate.scanner import SwiftScanner

# Scan files
scanner = SwiftScanner()
findings = scanner.scan_file(Path("MyView.swift"))

# Get structured data
for finding in findings:
    data = finding.to_dict()
    print(f"{data['rule_id']}: {data['migration_suggestion']}")
```

## 5 Detection Rules (V1)

| ID | Deprecated API | Replacement | iOS |
|----|---------------|-------------|-----|
| NAV001 | NavigationView | NavigationStack | 16.0+ |
| ENV001 | @Environment(\.presentationMode) | @Environment(\.dismiss) | 15.0+ |
| MOD001 | .navigationBarTitle() | .navigationTitle() | 14.0+ |
| MOD002 | .navigationBarItems() | .toolbar{} | 14.0+ |
| MOD003 | .edgesIgnoringSafeArea() | .ignoresSafeArea() | 14.0+ |

## Finding Structure
```python
{
    "rule_id": "NAV001",
    "rule_name": "NavigationView deprecated",
    "file_path": "/path/to/file.swift",
    "line_number": 10,
    "column": 8,
    "matched_snippet": "NavigationView {",
    "message": "NavigationView is deprecated in iOS 16+.",
    "severity": "warning",
    "deprecated_in": "iOS 16",
    "migration_suggestion": "Replace with NavigationStack...",
    "minimum_ios_version": "iOS 16.0"
}
```

## Common Workflows

### CI/CD Integration
```python
import sys
from swiftui_migrate.scanner import SwiftScanner
from pathlib import Path

scanner = SwiftScanner()
findings = scanner.scan_directory(Path("./Sources"))

if findings:
    for f in findings:
        print(f"{f.file_path}:{f.line_number} {f.rule.id}: {f.rule.message}")
    sys.exit(1)
else:
    print("✓ No migration issues")
    sys.exit(0)
```

### Generate Report
```python
from swiftui_migrate.scanner import SwiftScanner, group_findings_by_rule
from pathlib import Path

scanner = SwiftScanner()
findings = scanner.scan_directory(Path("./Sources"))
grouped = group_findings_by_rule(findings)

for rule_id, rule_findings in grouped.items():
    rule = rule_findings[0].rule
    print(f"{rule_id}: {len(rule_findings)} occurrences")
    print(f"  → {rule.suggestion}")
```

### Export for Analysis
```python
import json
from swiftui_migrate.scanner import SwiftScanner
from pathlib import Path

scanner = SwiftScanner()
findings = scanner.scan_directory(Path("./Sources"))

report = {
    "total": len(findings),
    "findings": [f.to_dict() for f in findings]
}

with open("report.json", "w") as f:
    json.dump(report, f, indent=2)
```

## Key Features
- ✅ **Fast**: Regex-based, no Swift compilation
- ✅ **Structured**: Finding.to_dict() for programmatic use
- ✅ **Migration-focused**: Actionable suggestions
- ✅ **CI-ready**: Exit codes, JSON output
- ✅ **Read-only**: No file modifications

## Documentation
- [README.md](../README.md) - User guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Design docs
- [examples/](../examples/) - Code examples
- [tests/](../tests/) - Test suite
