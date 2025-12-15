# swiftui-migrate

A straightforward Python CLI tool that scans Swift/SwiftUI code for deprecated APIs and common pitfalls.

## Why This Exists

SwiftUI changes fast. Apple deprecates APIs, introduces new patterns, and existing code that worked fine in iOS 15 might cause issues in iOS 17. Manually tracking these changes across a codebase is tedious.

This tool does the boring work: it scans your Swift files with regex patterns and tells you what's deprecated or likely to break.

That's it. No magic, no AI, no code rewriting (yet).

## What It Does

**Scans for two categories of issues:**

1. **Deprecated APIs** - Officially deprecated by Apple
   - `NavigationView` (iOS 16+)
   - `@Environment(\.presentationMode)` (iOS 15+)
   - `navigationBarTitle` (iOS 14+)
   - `navigationBarItems` (iOS 14+)
   - `edgesIgnoringSafeArea` (iOS 14+)

2. **Fragile Patterns** - Not deprecated, but known to break
   - `NavigationLink(isActive:)` - breaks with NavigationStack
   - Bool-driven navigation bindings - causes state issues
   - `.onAppear` in list rows - triggers on every scroll
   - `GeometryReader` in scroll views - layout loops
   - `@ObservedObject` in root views - premature deallocation

**For each issue:**
- Shows file location (`file.swift:line:column`)
- Explains what's wrong
- Suggests how to fix it
- Notes minimum iOS version for the fix

## What It Does NOT Do

- ❌ Parse Swift AST (uses regex patterns)
- ❌ Understand your app's logic or architecture
- ❌ Modify your code (read-only scanning)
- ❌ Catch every possible SwiftUI issue
- ❌ Replace code review or testing
- ❌ Guarantee migration correctness

This is a pattern matcher, not a compiler. It will miss some issues and occasionally flag false positives.

## Installation

**Requirements:**
- Python 3.10+
- No Swift compiler needed
- No Xcode required

```bash
# From source
git clone <repository-url>
cd swiftui-migrate
pip install -e .
```

**Or install dependencies:**
```bash
pip install click rich
```

## Usage

### Basic Scan

```bash
# Scan a file
swiftui-migrate scan MyView.swift

# Scan a directory
swiftui-migrate scan Sources/

# Scan with exclusions
swiftui-migrate scan . --exclude Pods --exclude Build
```

### Output Modes

**Human-readable (default):**
```bash
swiftui-migrate scan Sources/
```

**JSON for CI:**
```bash
swiftui-migrate scan Sources/ --json
```

### Filtering

```bash
# Only iOS 16+ issues
swiftui-migrate scan Sources/ --min-ios 16

# Only deprecated APIs
swiftui-migrate scan Sources/ --category deprecated

# Only fragile patterns
swiftui-migrate scan Sources/ --category fragile
```

### Grouping

```bash
# Group by file (default)
swiftui-migrate scan Sources/

# Group by rule type
swiftui-migrate scan Sources/ --group-by rule

# Group by category (deprecated vs fragile)
swiftui-migrate scan Sources/ --group-by category
```

## Example Output

```
swiftui-migrate v0.1.0

Sources/HomeView.swift
  15:8 NAV001: NavigationView is deprecated in iOS 16+.
  NavigationView {
  Suggestion: Replace with NavigationStack for simple navigation
  (Requires iOS 16.0+)

  42:12 FRAG001: NavigationLink with isActive: can cause issues
  NavigationLink(destination: DetailView(), isActive: $show) {
  Suggestion: Use NavigationStack with navigationDestination
  (Requires iOS 16.0+)

────────────────────────────────────────────────────────────
Summary
────────────────────────────────────────────────────────────
Files scanned:    12
Total issues:     8
  Deprecated:     5
  Fragile:        3
────────────────────────────────────────────────────────────
```

## CI Integration

### Exit Codes

**By default:**
- Deprecated APIs → exit 1 (fails CI)
- Fragile patterns → exit 0 (warnings only)

**Strict mode:**
```bash
swiftui-migrate scan Sources/ --fail-on-fragile
```
Everything fails CI.

### GitHub Actions

**.github/workflows/swiftui-check.yml:**
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
        run: |
          pip install click rich
          # Or: pip install swiftui-migrate
      
      - name: Scan for deprecated APIs
        run: |
          python -m swiftui_migrate.cli scan Sources/ --json > results.json
          
          # Check results
          DEPRECATED=$(jq '.summary.deprecated' results.json)
          FRAGILE=$(jq '.summary.fragile' results.json)
          
          echo "Found $DEPRECATED deprecated APIs"
          echo "Found $FRAGILE fragile patterns"
          
          # Fail on deprecated only (default behavior)
          swiftui-migrate scan Sources/
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: scan-results
          path: results.json
```

**Simpler version:**
```yaml
- name: Check SwiftUI code
  run: |
    pip install click rich
    swiftui-migrate scan Sources/
```

### GitLab CI

**.gitlab-ci.yml:**
```yaml
swiftui-check:
  image: python:3.10
  script:
    - pip install click rich
    - swiftui-migrate scan Sources/ --json > report.json
  artifacts:
    paths:
      - report.json
```

## Performance

**Expected:**
- ~1000 files/second on typical hardware
- Scales linearly with file count
- No compilation required

**Limitations:**
- Large codebases (10k+ files) may take a minute
- Network filesystems will be slower

## Detection Rules

| Rule | Name | iOS | Category |
|------|------|-----|----------|
| NAV001 | NavigationView deprecated | 16 | Deprecated |
| ENV001 | presentationMode deprecated | 15 | Deprecated |
| MOD001 | navigationBarTitle deprecated | 14 | Deprecated |
| MOD002 | navigationBarItems deprecated | 14 | Deprecated |
| MOD003 | edgesIgnoringSafeArea deprecated | 14 | Deprecated |
| FRAG001 | NavigationLink isActive | 16 | Fragile |
| FRAG002 | Bool-driven navigation | 16 | Fragile |
| FRAG003 | onAppear in row views | 15 | Fragile |
| FRAG004 | GeometryReader in scrolls | 17 | Fragile |
| FRAG005 | ObservedObject in root | 14 | Fragile |

Run `swiftui-migrate rules` to see all rules.

## Limitations

**This tool:**
- Uses regex, not a Swift parser
- Can't understand context or app architecture
- May flag valid code as problematic
- May miss complex patterns
- Won't catch all SwiftUI issues
- Doesn't understand conditional compilation
- Can't detect runtime-only issues

**It's a starting point, not a complete solution.**

## Roadmap

**v1.0 (current):**
- ✅ Pattern-based scanning
- ✅ Deprecated API detection
- ✅ Fragile pattern detection
- ✅ CI integration

**Future (maybe):**
- [ ] Auto-refactoring (opt-in, with preview)
- [ ] Swift AST parsing for accuracy
- [ ] Custom rule definitions
- [ ] Plugin system
- [ ] IDE integrations

Auto-refactoring will be:
1. Opt-in only
2. Requires explicit confirmation
3. Creates backups first
4. Shows diffs before applying

**No automated rewrites without user consent.**

## Philosophy

**This tool should be:**
- Boring (predictable, reliable)
- Honest (doesn't claim to be more than it is)
- Helpful (finds real issues)
- Fast (CI-friendly)
- Safe (read-only)

**It should not be:**
- Clever (no surprises)
- Magical (no hidden behavior)
- Intrusive (no code modification)
- Overly confident (flags issues, you decide)

## Contributing

Found a deprecated API this doesn't catch? Open an issue with:
- The API pattern
- iOS version where deprecated
- Suggested replacement

False positives? Also open an issue with:
- The code that was flagged
- Why it's actually fine

## License

MIT

## Credits

Built because migrating SwiftUI code is tedious and error-prone. This tool does the grep work so you don't have to.

No AI was harmed (or used) in the making of this tool.
