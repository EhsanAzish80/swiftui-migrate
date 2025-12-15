# Annotation Mode

The `--annotate` flag writes structured comments directly into Swift source files at detected issue locations.

**⚠️ This modifies your code files.** Always commit changes before using this feature.

## What It Does

Inserts comment blocks above each detected issue:

```swift
// swiftui-migrate: NAV001
// NavigationView is deprecated in iOS 16+.
// Suggestion: Replace with NavigationStack
// Minimum iOS: iOS 16
NavigationView {
    // your code
}
```

## Usage

### Basic annotation

```bash
swiftui-migrate scan Sources/ --annotate
```

### With backup

```bash
swiftui-migrate scan Sources/ --annotate --backup
```

Creates `.bak` files before modifying:
- `MyView.swift.bak` (original)
- `MyView.swift` (annotated)

**Restore from backup:**
```bash
cp MyView.swift.bak MyView.swift
```

### With filtering

```bash
# Only deprecated APIs
swiftui-migrate scan Sources/ --annotate --category deprecated

# Only iOS 16+ issues
swiftui-migrate scan Sources/ --annotate --min-ios 16
```

## Comment Format

Every comment follows this structure:

```
// swiftui-migrate: <RULE_ID>
// <Message>
// Suggestion: <Fix>
// Minimum iOS: <Version>
```

**Examples:**

```swift
// swiftui-migrate: ENV001
// @Environment(\.presentationMode) is deprecated in iOS 15+.
// Suggestion: Replace with @Environment(\.dismiss)
// Minimum iOS: iOS 15
@Environment(\.presentationMode) var presentationMode

// swiftui-migrate: FRAG001
// NavigationLink with isActive: can cause issues in iOS 16+.
// Suggestion: Use NavigationStack with navigationDestination
// Minimum iOS: iOS 16
NavigationLink(destination: DetailView(), isActive: $show) {
    Text("Go")
}
```

## Safety Features

### Duplicate prevention

Running annotation twice on the same file is safe:

```bash
# First run
swiftui-migrate scan Sources/ --annotate
# Files modified: 5

# Second run
swiftui-migrate scan Sources/ --annotate
# Files modified: 0 (comments already exist)
```

The tool scans 10 lines above each issue. If it finds a comment for the same rule, it skips insertion.

### Read-only protection

Read-only files are skipped:

```
Warning: File is read-only, skipping: ReadOnlyFile.swift
```

### Indentation preservation

Comments match the target line's indentation:

```swift
struct MyView: View {
    var body: some View {
        VStack {
            // swiftui-migrate: NAV001  <- indented properly
            // NavigationView is deprecated
            // Suggestion: Use NavigationStack
            // Minimum iOS: iOS 16
            NavigationView {
                Text("Hello")
            }
        }
    }
}
```

### Valid Swift code

Annotations are standard comments:
- Don't break compilation
- Don't affect runtime
- Don't trigger Xcode warnings
- Work with all Swift versions

## Recommended Workflow

### Step 1: Commit first

```bash
git add .
git commit -m "Pre-annotation checkpoint"
```

### Step 2: Annotate with backup

```bash
swiftui-migrate scan Sources/ --annotate --backup
```

### Step 3: Review changes

```bash
git diff Sources/
```

### Step 4: Verify code compiles

```bash
xcodebuild build
```

### Step 5: Commit or revert

```bash
# If satisfied
git add .
git commit -m "Add migration annotations"

# If not satisfied
git checkout .
```

## Team Workflow

Share annotations with your team:

```bash
# Annotate codebase
swiftui-migrate scan Sources/ --annotate --backup

# Create branch
git checkout -b feature/swiftui-migration

# Commit
git add .
git commit -m "Add SwiftUI migration annotations

Total issues: 47
- Deprecated: 23
- Fragile: 24
"

# Push
git push -u origin feature/swiftui-migration
```

Team members will see annotations directly in Xcode.

## Removing Annotations

### Git revert

If annotations are in one commit:

```bash
git revert <commit-hash>
```

### Restore from backup

```bash
for f in Sources/**/*.swift.bak; do 
    cp "$f" "${f%.bak}"
done
rm Sources/**/*.swift.bak
```

### Manual removal with sed

```bash
# macOS
find Sources -name "*.swift" -exec sed -i '' '/^[[:space:]]*\/\/ swiftui-migrate:/,/^[[:space:]]*\/\/ Minimum iOS:/d' {} \;

# Linux
find Sources -name "*.swift" -exec sed -i '/^[[:space:]]*\/\/ swiftui-migrate:/,/^[[:space:]]*\/\/ Minimum iOS:/d' {} \;
```

## Limitations

### What annotations DON'T do

- ❌ Auto-fix code
- ❌ Update when code changes
- ❌ Work in CI (modifies files)
- ❌ Handle all edge cases
- ❌ Guarantee correctness

### Line number drift

After annotating, line numbers shift:

```bash
# Before annotation
MyView.swift:15:8 NAV001: NavigationView is deprecated

# After annotation (4 comment lines added)
MyView.swift:19:8 NAV001: NavigationView is deprecated
```

The code location is still correct, just at a different line number.

### Multiple issues per line

If one line triggers multiple rules, each gets its own comment block:

```swift
// swiftui-migrate: FRAG002
// Bool-driven navigation bindings are fragile
// Suggestion: Use NavigationPath
// Minimum iOS: iOS 16
// swiftui-migrate: FRAG001
// NavigationLink with isActive: can cause issues
// Suggestion: Use navigationDestination
// Minimum iOS: iOS 16
NavigationLink(destination: Detail(), isActive: $show) {
    Text("Go")
}
```

This is intentional.

## CI Usage

**Don't use `--annotate` in CI:**

```yaml
# ❌ WRONG - modifies files
- run: swiftui-migrate scan Sources/ --annotate

# ✅ CORRECT - read-only
- run: swiftui-migrate scan Sources/ --json
```

Annotations should be:
- Created locally by developers
- Reviewed with `git diff`
- Committed intentionally
- Not automated in CI

## FAQ

**Q: Will annotations break my code?**  
A: No. They're standard Swift comments.

**Q: Can I customize the format?**  
A: Not currently. The format is standardized.

**Q: Should I commit annotations?**  
A: Personal choice. They're helpful for teams but add noise to diffs.

**Q: What if I run --annotate twice?**  
A: Safe. Existing annotations are detected and skipped.

**Q: Can I use --annotate in CI?**  
A: No. It modifies files. Use read-only scanning in CI.

**Q: How do I remove all annotations?**  
A: Git revert, restore from `.bak`, or use sed (see "Removing Annotations").

**Q: Do annotations update when I fix code?**  
A: No. They're static. Re-scan to verify fixes.

**Q: What about merge conflicts?**  
A: Annotations can cause conflicts. Coordinate with your team or use feature branches.

## Philosophy

Annotations are designed to feel like **helpful notes from a teammate**, not compiler errors.

They're useful for:
- Migration planning
- Team visibility
- Tracking progress
- Learning SwiftUI patterns

They're NOT:
- Required for the tool to work
- Automatically maintained
- Suitable for CI/CD
- A replacement for understanding the code
