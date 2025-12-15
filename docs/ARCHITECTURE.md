# SwiftUI Migration Rule Engine Architecture

## Overview

The rule engine is designed to detect high-confidence SwiftUI migration cases with structured output independent of presentation.

## Core Components

### 1. Rule Definition (`rules.py`)

Each rule is a `@dataclass` with:
- `id`: Unique identifier (e.g., "NAV001")
- `name`: Human-readable name
- `pattern`: Regex pattern to match deprecated API
- `message`: Description of the issue
- `severity`: "warning" or "error"
- `ios_version`: When the API was deprecated
- `suggestion`: Migration guidance
- `min_ios_version`: Minimum iOS version for replacement

**Example:**
```python
Rule(
    id="NAV001",
    name="NavigationView deprecated",
    pattern=r"\bNavigationView\s*\{",
    message="NavigationView is deprecated in iOS 16+.",
    severity="warning",
    ios_version="iOS 16",
    suggestion="Replace with NavigationStack for simple navigation or NavigationSplitView for multi-column layouts",
    min_ios_version="iOS 16.0",
)
```

### 2. Scanner (`scanner.py`)

The `SwiftScanner` class provides:
- `scan_file(path)`: Scan a single Swift file
- `scan_directory(path, exclude_patterns)`: Recursively scan directories
- `scan_paths(paths)`: Scan multiple files/directories

**Finding Object:**
Each detection creates a `Finding` object with:
- `file_path`: Absolute path
- `line_number`: 1-indexed line number
- `column`: Column position
- `line_content`: The matched line
- `rule`: Reference to the matched Rule

### 3. Structured Output

The `Finding.to_dict()` method returns:
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

This structure is **independent of CLI output formatting** and can be used programmatically.

## V1 High-Confidence Rules

### Why These 5 Rules?

1. **Clear deprecation path**: Apple has documented replacements
2. **High impact**: Commonly used APIs
3. **Detectable via pattern matching**: No AST parsing required
4. **Actionable**: Developers can fix immediately

### Rule Details

#### NAV001: NavigationView → NavigationStack
- **Pattern**: `\bNavigationView\s*\{`
- **Why deprecated**: Replaced by more flexible navigation APIs
- **Migration**: Use `NavigationStack` for simple hierarchical navigation or `NavigationSplitView` for multi-column layouts
- **iOS**: 16.0+

#### ENV001: presentationMode → dismiss
- **Pattern**: `@Environment\(\\\.presentationMode\)`
- **Why deprecated**: Simplified dismiss API
- **Migration**: Replace with `@Environment(\.dismiss)` and call `dismiss()` directly
- **iOS**: 15.0+

#### MOD001: navigationBarTitle → navigationTitle
- **Pattern**: `\.navigationBarTitle\(`
- **Why deprecated**: Naming consistency
- **Migration**: Use `.navigationTitle(_:)` and optionally `.navigationBarTitleDisplayMode(_:)`
- **iOS**: 14.0+

#### MOD002: navigationBarItems → toolbar
- **Pattern**: `\.navigationBarItems\(`
- **Why deprecated**: Replaced by more powerful toolbar API
- **Migration**: Use `.toolbar { ToolbarItem(placement: ...) { ... } }`
- **iOS**: 14.0+

#### MOD003: edgesIgnoringSafeArea → ignoresSafeArea
- **Pattern**: `\.edgesIgnoringSafeArea\(`
- **Why deprecated**: API naming improvement
- **Migration**: Use `.ignoresSafeArea(_:edges:)`
- **iOS**: 14.0+

## Usage Patterns

### CLI Usage
```bash
# Scan and get migration suggestions
swiftui-migrate scan ./Sources

# JSON output for tooling
swiftui-migrate scan ./Sources --format json > report.json
```

### Programmatic Usage
```python
from swiftui_migrate.scanner import SwiftScanner
from pathlib import Path

scanner = SwiftScanner()
findings = scanner.scan_file(Path("MyView.swift"))

for finding in findings:
    data = finding.to_dict()
    # Process structured data
    print(f"{data['rule_id']}: {data['migration_suggestion']}")
```

### CI/CD Integration
```python
import sys
from swiftui_migrate.scanner import SwiftScanner
from pathlib import Path

scanner = SwiftScanner()
findings = scanner.scan_directory(Path("./Sources"))

if findings:
    print(f"Found {len(findings)} migration issues")
    for f in findings:
        print(f.to_dict())
    sys.exit(1)
else:
    print("✓ No migration issues")
    sys.exit(0)
```

## Design Decisions

### Text-Based Scanning (V1)
- **Pro**: Fast, no Swift compilation required
- **Pro**: Works on any platform with Python 3.10+
- **Pro**: CI-friendly (no Xcode needed)
- **Con**: Regex patterns may produce false positives
- **Con**: Can't detect context-dependent issues

### Future: AST-Based Scanning (V2+)
- Use Swift's libSyntax or SwiftSyntax for semantic analysis
- Reduce false positives
- Enable more complex rule patterns
- Support safe auto-refactoring

## Extending the Rule Engine

### Adding a New Rule

1. **Define the rule** in `rules.py`:
```python
Rule(
    id="NEW001",
    name="Your rule name",
    pattern=r"your_regex_pattern",
    message="Description of the issue",
    severity="warning",
    ios_version="iOS XX",
    suggestion="How to fix it",
    min_ios_version="iOS XX.0",
)
```

2. **Test the rule**:
```python
def test_new_rule():
    rule = get_rule_by_id("NEW001")
    assert rule is not None
    # Test pattern matching
```

3. **Update documentation** in README.md

### Best Practices for Rules

- **Be specific**: Use word boundaries (`\b`) to avoid partial matches
- **Capture context**: Include surrounding syntax in patterns
- **Provide value**: Only add rules with clear migration paths
- **Test thoroughly**: Ensure patterns match intended code only

## Performance Characteristics

- **Speed**: ~100-500 files/second (regex-based)
- **Memory**: O(n) where n = file size
- **Scalability**: Handles large codebases (10,000+ files)

**Benchmarks** (approximate):
- Small project (50 files): < 1 second
- Medium project (500 files): < 5 seconds
- Large project (5000 files): < 30 seconds

## Error Handling

- **File read errors**: Silently skipped (logged in verbose mode)
- **Unicode errors**: Invalid UTF-8 files skipped
- **Pattern errors**: Validated at module load time

## Future Enhancements

### V0.2
- Custom rule configuration via YAML/TOML
- Rule severity override
- Exclude specific rules

### V0.3
- Multi-line pattern matching
- Context-aware rules
- Confidence scores

### V0.4
- AST-based parsing via libSyntax
- Semantic analysis
- Higher accuracy

### V1.0
- Safe auto-refactoring
- Fix suggestions with code snippets
- Interactive migration mode
