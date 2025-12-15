# SwiftUI Migrate

A Python CLI tool that scans Swift/SwiftUI codebases and reports deprecated or fragile SwiftUI API usage to help developers migrate across iOS versions.

## Problem Statement

SwiftUI evolves rapidly with each iOS release. APIs get deprecated, new best practices emerge, and code that worked perfectly in iOS 15 may trigger warnings or crashes in iOS 17. Manually tracking these changes across large codebases is time-consuming and error-prone.

**SwiftUI Migrate** helps you:
- 🔍 Identify deprecated SwiftUI APIs before they break
- ⚠️ Detect fragile patterns that may cause issues
- 📊 Get a clear migration roadmap for your codebase
- 🚀 Integrate seamlessly into CI/CD pipelines

## What It Does

✅ **Does:**
- Recursively scans `.swift` files in your project
- Detects **deprecated SwiftUI APIs** (e.g., `NavigationView`, `navigationBarItems`)
- Identifies **fragile patterns** that break or behave inconsistently (e.g., `NavigationLink` with `isActive`)
- Provides line-by-line reports with actionable suggestions
- Explains *why* patterns are problematic with behavioral notes
- Supports multiple output formats (text, summary, JSON)
- Zero runtime dependencies on Swift compiler or Xcode
- Fast, read-only scanning suitable for CI environments

✅ **Detects two categories:**
- **Deprecated APIs**: Officially deprecated by Apple (fails CI by default)
- **Fragile Patterns**: Known to cause issues but not deprecated (warnings only)

❌ **Does NOT:**
- Perform AST parsing or deep semantic analysis (v1)
- Automatically rewrite or refactor code
- Require Swift compilation or project builds
- Modify your source files in any way

## Installation

**Requirements:**
- Python 3.10 or higher

**Install from source:**
```bash
git clone https://github.com/yourusername/swiftui-migrate.git
cd swiftui-migrate
pip install -e .
```

**Or install dependencies directly:**
```bash
pip install click rich
```

## Usage

### Basic Commands

Scan a single file or directory:
```bash
swiftui-migrate scan /path/to/your/project
```

Scan multiple paths:
```bash
swiftui-migrate scan ./Sources ./Tests
```

### Output Modes

**Human-readable (default)**:
```bash
swiftui-migrate scan ./Sources
```

**JSON for CI/CD**:
```bash
swiftui-migrate scan ./Sources --json
```

Example JSON output:
```json
{
  "version": "0.1.0",
  "files_scanned": 42,
  "summary": {
    "total": 15,
    "deprecated": 10,
    "fragile": 5
  },
  "findings": [...]
}
```

### Filtering

**By iOS version** (focus on specific migrations):
```bash
# Only show iOS 16+ issues
swiftui-migrate scan ./Sources --min-ios 16

# Only show iOS 17+ issues
swiftui-migrate scan ./Sources --min-ios 17
```

**By category** (deprecated vs fragile):
```bash
# Only deprecated APIs (hard blockers)
swiftui-migrate scan ./Sources --category deprecated

# Only fragile patterns (warnings)
swiftui-migrate scan ./Sources --category fragile
```

**By severity**:
```bash
swiftui-migrate scan ./Sources --severity error
swiftui-migrate scan ./Sources --severity warning
```

### Grouping Options

Group results by file (default), rule, or category:
```bash
swiftui-migrate scan ./Sources --group-by file
swiftui-migrate scan ./Sources --group-by rule
swiftui-migrate scan ./Sources --group-by category
swiftui-migrate scan ./Sources --group-by none
```

### Advanced Options

**Fail CI on fragile patterns** (optional strict mode):
```bash
# By default, only deprecated APIs fail CI
swiftui-migrate scan ./Sources --fail-on-fragile
```

**Exclude directories**:
```bash
swiftui-migrate scan ./Sources --exclude Pods --exclude DerivedData
```

### List Available Rules

View all detection rules:
```bash
swiftui-migrate rules
```

## Example Output

### Human-Readable (Default)
```
swiftui-migrate v0.1.0

/Users/dev/MyApp/Sources/ContentView.swift
  4:4 ENV001: @Environment(\.presentationMode) is deprecated in iOS 15+.
  @Environment(\.presentationMode) var presentationMode
  Suggestion: Replace with @Environment(\.dismiss) and call dismiss() directly
  (Requires iOS 15.0+)

  7:8 NAV001: NavigationView is deprecated in iOS 16+.
  NavigationView {
  Suggestion: Replace with NavigationStack for simple navigation
  (Requires iOS 16.0+)

────────────────────────────────────────────────────────────
Summary
────────────────────────────────────────────────────────────
Files scanned:    1
Total issues:     6
  Deprecated:     6
  Fragile:        0
────────────────────────────────────────────────────────────
```

### JSON Mode
```json
{
  "version": "0.1.0",
  "files_scanned": 1,
  "summary": {
    "total": 6,
    "deprecated": 6,
    "fragile": 0
  },
  "findings": [
    {
      "rule_id": "NAV001",
      "rule_name": "NavigationView deprecated",
      "file_path": "/Users/dev/MyApp/Sources/ContentView.swift",
      "line_number": 7,
      "column": 8,
      "matched_snippet": "NavigationView {",
      "message": "NavigationView is deprecated in iOS 16+.",
      "severity": "warning",
      "deprecated_in": "iOS 16",
      "migration_suggestion": "Replace with NavigationStack...",
      "minimum_ios_version": "iOS 16.0",
      "category": "deprecated"
    }
  ]
}
```

## Detection Rules

### Deprecated APIs (Fail CI by Default)

**V1 High-Confidence Migration Rules:**

The rule engine focuses on detecting deprecated APIs with clear migration paths:

| Rule ID | Deprecated API | Replacement | Min iOS |
|---------|---------------|-------------|---------|
| `NAV001` | `NavigationView` | `NavigationStack` or `NavigationSplitView` | iOS 16.0 |
| `ENV001` | `@Environment(\.presentationMode)` | `@Environment(\.dismiss)` | iOS 15.0 |
| `MOD001` | `.navigationBarTitle(_:displayMode:)` | `.navigationTitle(_:)` + `.navigationBarTitleDisplayMode(_:)` | iOS 14.0 |
| `MOD002` | `.navigationBarItems(leading:trailing:)` | `.toolbar { ToolbarItem(...) }` | iOS 14.0 |
| `MOD003` | `.edgesIgnoringSafeArea(_:)` | `.ignoresSafeArea(_:edges:)` | iOS 14.0 |

### Fragile Patterns (Warnings Only)

**Patterns that aren't deprecated but cause issues:**

| Rule ID | Fragile Pattern | Why Problematic | Modern Alternative |
|---------|----------------|-----------------|-------------------|
| `FRAG001` | `NavigationLink(isActive:)` | Breaks with NavigationStack, state desync | Value-based navigation |
| `FRAG002` | Bool-driven navigation | Doesn't compose with NavigationPath | NavigationPath |
| `FRAG003` | `.onAppear` in list rows | Fires on every scroll, redundant loads | `.task()` on parent view |
| `FRAG004` | `GeometryReader` in ScrollView | Layout loops, jittery scrolling | `.visualEffect` or `.containerRelativeFrame` |
| `FRAG005` | `@ObservedObject` in App struct | Premature deallocation | `@StateObject` |

**Important:** Fragile patterns don't fail CI by default. Use `--fail-on-fragile` to enforce.

See [docs/FRAGILE_PATTERNS.md](docs/FRAGILE_PATTERNS.md) for detailed explanations.

### Finding Structure

Each finding includes:
- **Rule ID**: Unique identifier
- **File path & line number**: Exact location
- **Matched snippet**: The problematic code
- **Migration suggestion**: How to fix it
- **Minimum iOS version**: Required for the replacement API
- **Category**: "deprecated" or "fragile"
- **Behavioral note**: (Fragile patterns only) Why it causes issues

Run `swiftui-migrate rules` for detailed descriptions.

## Programmatic Usage

Use swiftui-migrate as a library in your own Python tools:

```python
from pathlib import Path
from swiftui_migrate.scanner import SwiftScanner

# Initialize scanner
scanner = SwiftScanner()

# Scan files
findings = scanner.scan_file(Path("MyView.swift"))

# Get structured results
for finding in findings:
    result = finding.to_dict()
    print(f"{result['rule_id']}: {result['migration_suggestion']}")
    print(f"  Min iOS: {result['minimum_ios_version']}")
```

Each `Finding` object includes:
- `rule_id`: Unique rule identifier
- `rule_name`: Human-readable name
- `file_path`: Absolute path to file
- `line_number`: Line where issue occurs
- `column`: Column position
- `matched_snippet`: The problematic code
- `message`: Issue description
- `severity`: "warning" or "error"
- `deprecated_in`: iOS version where deprecated
- `migration_suggestion`: How to fix it
- `minimum_ios_version`: Required iOS for replacement

See [examples/usage_example.py](examples/usage_example.py) for complete examples.

## CI/CD Integration

### Exit Codes

| Scenario | Exit Code | Behavior |
|----------|-----------|----------|
| No issues found | 0 | ✅ Pass |
| Only fragile patterns | 0 | ✅ Pass (warnings only) |
| Deprecated APIs found | 1 | ❌ Fail |
| Both found | 1 | ❌ Fail (due to deprecated) |
| With `--fail-on-fragile` | 1 | ❌ Fail on any issue |

**Default behavior:** Deprecated APIs fail CI, fragile patterns don't.

### GitHub Actions

**Basic integration**:
```yaml
- name: Check SwiftUI API usage
  run: |
    pip install swiftui-migrate
    swiftui-migrate scan ./Sources
    # Only fails if deprecated APIs found
```

**With JSON output**:
```yaml
- name: Scan SwiftUI code
  run: |
    swiftui-migrate scan ./Sources --json > results.json
    
- name: Check for deprecated APIs
  run: |
    DEPRECATED=$(jq '.summary.deprecated' results.json)
    if [ "$DEPRECATED" -gt 0 ]; then
      echo "Found $DEPRECATED deprecated APIs"
      exit 1
    fi
```

**Strict mode** (fail on fragile patterns too):
```yaml
- name: SwiftUI strict check
  run: swiftui-migrate scan ./Sources --fail-on-fragile
```

### GitLab CI

```yaml
swiftui-check:
  script:
    - pip install swiftui-migrate
    - swiftui-migrate scan ./Sources --json > report.json
  artifacts:
    reports:
      codequality: report.json
```

## Project Structure

```
swiftui-migrate/
├── src/
│   └── swiftui_migrate/
│       ├── __init__.py       # Package initialization
│       ├── __main__.py       # Entry point for python -m
│       ├── cli.py            # CLI interface (Click + Rich)
│       ├── scanner.py        # Core scanning logic
│       └── rules.py          # Rule definitions
├── tests/
│   └── __init__.py
├── pyproject.toml            # Project configuration
├── README.md                 # This file
└── .gitignore
```

## Development

**Install in development mode:**
```bash
pip install -e ".[dev]"
```

**Run tests:**
```bash
pytest
```

**Format code:**
```bash
black src/ tests/
ruff check src/ tests/
```

## Limitations (v1)

- **Text-based scanning only**: Uses regex patterns, not full Swift AST parsing
- **No semantic analysis**: May miss context-dependent issues or produce false positives
- **No auto-refactoring**: Reports issues only; manual fixes required
- **Pattern matching**: Can't detect complex logic flows or multi-line patterns

Future versions may add AST parsing using Swift's libSyntax or similar tools.

## Roadmap

- [ ] v0.2: Custom rule configuration via YAML/TOML
- [ ] v0.3: HTML report generation
- [ ] v0.4: AST-based parsing for higher accuracy
- [ ] v1.0: Auto-fix suggestions (safe refactorings)

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new rules or features
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Credits

Built with:
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting

---

**Built for developers, by developers.** Help make SwiftUI migrations painless.
