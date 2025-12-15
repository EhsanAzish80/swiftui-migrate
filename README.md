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
- Detects deprecated SwiftUI APIs (e.g., `NavigationView`, `navigationBarItems`)
- Flags fragile patterns (e.g., heavy work in `.onAppear`, `GeometryReader` abuse)
- Provides line-by-line reports with actionable suggestions
- Supports multiple output formats (text, summary, JSON)
- Zero runtime dependencies on Swift compiler or Xcode
- Fast, read-only scanning suitable for CI environments

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

### Basic Scan

Scan a single file or directory:
```bash
swiftui-migrate scan /path/to/your/project
```

Scan multiple paths:
```bash
swiftui-migrate scan ./Sources ./Tests
```

### Output Formats

**Default text format** (grouped by file):
```bash
swiftui-migrate scan ./Sources
```

**Summary format** (counts by rule):
```bash
swiftui-migrate scan ./Sources --format summary
```

**JSON format** (for CI/tooling):
```bash
swiftui-migrate scan ./Sources --format json
```

### Filtering

Filter by severity:
```bash
swiftui-migrate scan ./Sources --severity error
swiftui-migrate scan ./Sources --severity warning
```

Group results differently:
```bash
swiftui-migrate scan ./Sources --group-by rule
swiftui-migrate scan ./Sources --group-by none
```

Exclude directories:
```bash
swiftui-migrate scan ./Sources --exclude Pods --exclude DerivedData
```

### List Available Rules

View all detection rules:
```bash
swiftui-migrate rules
```

## Example Output

### Text Format
```
/Users/dev/MyApp/Sources/ContentView.swift
  Line 12:8 NAV001 NavigationView is deprecated in iOS 16+. Use NavigationStack or NavigationSplitView instead.
    │ NavigationView {

  Line 25:12 MOD002 navigationBarItems is deprecated. Use .toolbar() instead.
    │ .navigationBarItems(trailing: Button("Save") {})

Total issues found: 2
```

### Summary Format
```
╭─────────── Scan Summary ───────────╮
│ Rule ID │ Rule Name                │ Count │ Severity │
├─────────┼──────────────────────────┼───────┼──────────┤
│ NAV001  │ NavigationView deprecated│     5 │ WARNING  │
│ MOD002  │ navigationBarItems...    │     3 │ WARNING  │
│ PERF001 │ Heavy work in onAppear   │     2 │ WARNING  │
╰─────────────────────────────────────────────────────╯

Total files scanned: 12
Total issues found: 10
```

### JSON Format
```json
{
  "version": "0.1.0",
  "total_findings": 2,
  "findings": [
    {
      "file": "/Users/dev/MyApp/Sources/ContentView.swift",
      "line": 12,
      "column": 8,
      "rule_id": "NAV001",
      "rule_name": "NavigationView deprecated",
      "severity": "warning",
      "message": "NavigationView is deprecated in iOS 16+. Use NavigationStack or NavigationSplitView instead.",
      "ios_version": "iOS 16",
      "line_content": "NavigationView {"
    }
  ]
}
```

## Detection Rules

Current rules (v0.1.0):

| Rule ID | What It Detects | iOS Version |
|---------|----------------|-------------|
| `NAV001` | `NavigationView` usage | iOS 16+ |
| `MOD001` | `navigationBarTitle` usage | iOS 14+ |
| `MOD002` | `navigationBarItems` usage | iOS 14+ |
| `PERF001` | Heavy work in `.onAppear` | iOS 15+ |
| `GEO001` | Potentially unnecessary `GeometryReader` | All |
| `STATE001` | `@State` outside View structs | All |
| `ENV001` | `@EnvironmentObject` without previews | All |
| `LIST001` | `ForEach` without explicit IDs | All |
| `COLOR001` | Hardcoded color literals | All |
| `BIND001` | `.constant()` binding usage | All |

Run `swiftui-migrate rules` for the complete list with descriptions.

## CI Integration

Exit codes:
- `0`: No issues found
- `1`: Issues found

**GitHub Actions example:**
```yaml
- name: Check SwiftUI API usage
  run: |
    pip install swiftui-migrate
    swiftui-migrate scan ./Sources --format summary
```

**GitLab CI example:**
```yaml
swiftui-check:
  script:
    - pip install swiftui-migrate
    - swiftui-migrate scan ./Sources --format json > report.json
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
