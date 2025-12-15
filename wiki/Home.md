# swiftui-migrate

A Python CLI tool that scans Swift/SwiftUI code for deprecated APIs and fragile patterns.

## What It Does

Scans your Swift files with regex patterns and reports:

1. **Deprecated APIs** - Officially deprecated by Apple (iOS 14-17)
2. **Fragile Patterns** - Not deprecated, but known to cause issues

For each finding, you get:
- File location (`file.swift:line:column`)
- What's wrong
- How to fix it
- Minimum iOS version for the fix

## What It Doesn't Do

- Parse Swift AST (uses regex)
- Understand your app's logic
- Modify code automatically (read-only by default)
- Catch every possible issue
- Guarantee migration correctness

This is a pattern matcher, not a compiler. Expect occasional false positives and false negatives.

## Quick Start

```bash
# Install
pip install click rich
git clone https://github.com/EhsanAzish80/swiftui-migrate.git
cd swiftui-migrate
pip install -e .

# Scan a directory
swiftui-migrate scan Sources/

# Scan for deprecated APIs only
swiftui-migrate scan Sources/ --category deprecated

# Output as JSON for CI
swiftui-migrate scan Sources/ --json
```

## Documentation

- **[Installation](Installation)** - Setup and requirements
- **[CLI Usage](CLI-Usage)** - Commands, flags, and output modes
- **[Deprecated API Rules](Deprecated-API-Rules)** - Complete list of deprecated API patterns
- **[Fragile Pattern Rules](Fragile-Pattern-Rules)** - Common SwiftUI pitfalls
- **[Annotation Mode](Annotation-Mode)** - Write inline comments into Swift files
- **[CI Integration](CI-Integration)** - GitHub Actions, GitLab CI, exit codes
- **[Roadmap](Roadmap)** - Future plans

## Philosophy

This tool is boring in the best possible way:

- No AI
- No magic
- No hype
- No automatic refactoring (v1)
- Just straightforward pattern matching

It does one thing: find deprecated and fragile SwiftUI code. That's it.

## Exit Codes

- **0** - No issues or only fragile patterns (warnings)
- **1** - Deprecated APIs found (fails CI by default)

Use `--fail-on-fragile` to fail CI on any issue.

## Contributing

Report issues or contribute rules on [GitHub](https://github.com/EhsanAzish80/swiftui-migrate).

## License

See repository for license information.
