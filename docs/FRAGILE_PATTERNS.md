# Fragile Pattern Detection

## Overview

In addition to detecting **deprecated APIs**, swiftui-migrate now identifies **fragile patterns** - SwiftUI code that is not officially deprecated but is known to break or behave inconsistently, especially in newer iOS versions.

## What Are Fragile Patterns?

Fragile patterns are coding practices that:
- ❌ **Are NOT officially deprecated** by Apple
- ⚠️ **Cause runtime issues** or unexpected behavior  
- 🔄 **Break when iOS versions change** behavior
- 📉 **Lead to poor performance** or state management issues
- 🐛 **Are hard to debug** when they fail

**Key Difference:**
- **Deprecated APIs**: Apple says "don't use this anymore"
- **Fragile Patterns**: Community wisdom says "this will cause problems"

## The 5 Fragile Patterns (V1)

### FRAG001: NavigationLink with isActive

**Pattern:**
```swift
NavigationLink(destination: DetailView(), isActive: $showDetail) {
    Text("Show Detail")
}
```

**Why Fragile:**
The `isActive` binding pattern breaks with `NavigationStack` (iOS 16+) and can cause state desynchronization, especially with programmatic navigation. Navigation state may not update correctly when using back button or swipe gestures.

**Modern Replacement:**
```swift
NavigationStack {
    // Value-based navigation
    NavigationLink(value: detailItem) {
        Text("Show Detail")
    }
}
.navigationDestination(for: Item.self) { item in
    DetailView(item: item)
}
```

**Requires:** iOS 16.0+

---

### FRAG002: Bool-Driven Navigation

**Pattern:**
```swift
@State private var showSettings = false
@State private var showProfile = false

NavigationLink(destination: SettingsView(), isActive: $showSettings) { EmptyView() }
NavigationLink(destination: ProfileView(), isActive: $showProfile) { EmptyView() }
```

**Why Fragile:**
Bool bindings for navigation don't compose well with NavigationStack's path-based model. Can lead to unexpected navigation behavior, state loss, or inability to deep-link. Multiple bool flags for navigation stack becomes unmaintainable.

**Modern Replacement:**
```swift
@State private var path = NavigationPath()

NavigationStack(path: $path) {
    // ...
}

// Navigate programmatically
path.append(NavigationDestination.settings)
```

**Requires:** iOS 16.0+

---

### FRAG003: onAppear for Data Loading in Lists

**Pattern:**
```swift
List {
    ForEach(items) { item in
        RowView(item: item)
            .onAppear {
                loadMoreData()  // ❌ Fires on every scroll!
            }
    }
}
```

**Why Fragile:**
`onAppear` fires every time a row appears during scrolling, causing redundant network requests or computation. In iOS 15+, cells are aggressively recycled, triggering `onAppear` multiple times for the same data. Can cause performance issues and API rate limiting.

**Modern Replacement:**
```swift
List {
    ForEach(items) { item in
        RowView(item: item)
    }
}
.task {
    await loadInitialData()  // ✅ Only once
}
.refreshable {
    await refreshData()      // ✅ User-initiated
}
```

**Requires:** iOS 15.0+

---

### FRAG004: GeometryReader in Scrollable Containers

**Pattern:**
```swift
ScrollView {
    GeometryReader { geometry in
        Color.blue
            .frame(height: geometry.size.width * 0.5)
    }
}
```

**Why Fragile:**
GeometryReader triggers layout recalculations that conflict with ScrollView's lazy rendering. Can cause infinite layout loops, jittery scrolling, or incorrect sizing. iOS 17+ offers better alternatives for scroll-based animations.

**Modern Replacement:**
```swift
ScrollView {
    Color.blue
        .containerRelativeFrame(.horizontal) { width, _ in
            return width * 0.5
        }
}

// Or for scroll effects
ScrollView {
    ForEach(items) { item in
        ItemView(item: item)
            .visualEffect { content, proxy in
                content.offset(y: proxy.frame(in: .scrollView).minY * 0.5)
            }
    }
}
```

**Requires:** iOS 17.0+

---

### FRAG005: @ObservedObject in Root/App Views

**Pattern:**
```swift
@main
struct MyApp: App {
    @ObservedObject var appState = AppState()  // ❌ Can be deallocated!
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}
```

**Why Fragile:**
`@ObservedObject` doesn't own the object, relying on parent to keep it alive. In root views or App struct, there's no parent, so object may be deallocated unexpectedly causing crashes or state loss. `@StateObject` ensures SwiftUI owns the lifecycle.

**Modern Replacement:**
```swift
@main
struct MyApp: App {
    @StateObject private var appState = AppState()  // ✅ Owned by SwiftUI
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}
```

**Requires:** iOS 14.0+

---

## Detection & Output

### CLI Usage

**Scan for all issues (deprecated + fragile):**
```bash
swiftui-migrate scan ./Sources
```

**Scan for fragile patterns only:**
```bash
swiftui-migrate scan ./Sources --category fragile
```

**Group by category:**
```bash
swiftui-migrate scan ./Sources --group-by category
```

Output shows fragile patterns with 🔧 badge:
```
🔧 FRAG001 at line 12: NavigationLink with isActive
  → Use NavigationStack with navigationDestination(isPresented:)
  Why fragile: The isActive binding pattern breaks with NavigationStack...
```

### Programmatic Usage

```python
from swiftui_migrate.scanner import SwiftScanner
from swiftui_migrate.rules import get_fragile_rules
from pathlib import Path

scanner = SwiftScanner()
findings = scanner.scan_file(Path("MyView.swift"))

# Filter fragile patterns
fragile = [f for f in findings if f.rule.category == "fragile"]

for finding in fragile:
    data = finding.to_dict()
    print(f"{data['rule_id']}: {data['rule_name']}")
    print(f"  Suggestion: {data['migration_suggestion']}")
    print(f"  Why fragile: {data['behavioral_note']}")
```

### JSON Output

```json
{
  "rule_id": "FRAG001",
  "rule_name": "NavigationLink isActive pattern",
  "category": "fragile",
  "message": "NavigationLink with isActive: can cause navigation state issues in iOS 16+.",
  "migration_suggestion": "Use NavigationStack with navigationDestination(isPresented:)...",
  "behavioral_note": "The isActive binding pattern breaks with NavigationStack and can cause state desynchronization..."
}
```

## CI/CD Behavior

**Important:** Fragile patterns **DO NOT fail CI by default**.

```bash
# Exit code 0 if only fragile patterns found
swiftui-migrate scan ./Sources

# Exit code 1 if fragile patterns found
swiftui-migrate scan ./Sources --fail-on-fragile
```

### Why This Design?

- Deprecated APIs: **Breaking changes** → Should fail CI
- Fragile patterns: **Code smells** → Informational warnings

Teams can opt-in to strict checking with `--fail-on-fragile`.

## Detection Rules

| Rule ID | Pattern | Severity | Fails CI |
|---------|---------|----------|----------|
| FRAG001 | NavigationLink isActive | warning | No* |
| FRAG002 | Bool-driven navigation | warning | No* |
| FRAG003 | onAppear in rows | warning | No* |
| FRAG004 | GeometryReader in ScrollView | warning | No* |
| FRAG005 | @ObservedObject in App | warning | No* |

\* Unless `--fail-on-fragile` flag is used

## When to Act on Fragile Patterns

### High Priority
- **FRAG001/FRAG002**: If targeting iOS 16+ and using NavigationStack
- **FRAG005**: If experiencing crashes or state loss
- **FRAG004**: If experiencing scroll jank or layout issues

### Medium Priority
- **FRAG003**: If API rate limits hit or performance issues in lists

### Consider Context
Fragile patterns may be acceptable if:
- ✅ You're targeting older iOS versions
- ✅ Pattern works in your specific use case
- ✅ Migration cost > benefit for your app

## Best Practices

### 1. Review, Don't Auto-Fix
Unlike deprecated APIs, fragile patterns require judgment:
```bash
# Get the report
swiftui-migrate scan ./Sources --category fragile --format summary

# Review each case
# Fix high-impact patterns first
```

### 2. Test After Fixing
Fragile patterns often involve state management - test thoroughly:
```swift
// Before
@ObservedObject var model = ViewModel()

// After - TEST that object lifecycle is correct
@StateObject private var model = ViewModel()
```

### 3. Use as Learning Tool
Fragile patterns teach modern SwiftUI best practices:
- Read the `behavioral_note` to understand *why* it's fragile
- Share findings with team for education
- Update coding guidelines

## Implementation Notes

### Pattern Detection
- **Text-based regex** (like deprecated APIs)
- **Line-by-line scanning** (no AST in v1)
- **May have false positives** - review manually

### Behavioral Notes
Each fragile pattern includes:
- Root cause explanation
- When it breaks
- Impact on user experience
- iOS version context

## Future Enhancements

### V0.2
- Context-aware detection (reduce false positives)
- Confidence scores for each finding
- "Safe to ignore" annotations

### V0.3
- Multi-line pattern matching
- Call graph analysis for @ObservedObject
- Integration with SwiftUI view hierarchy

### V1.0
- Safe refactoring suggestions
- Automated migration for simple cases
- Custom fragile pattern definitions

## FAQ

**Q: Will fragile patterns ever become deprecated?**  
A: Unlikely. They're patterns, not APIs. Apple may improve alternatives but won't deprecate the syntax.

**Q: Should I fix all fragile patterns?**  
A: No. Use as informational. Fix based on:
- iOS version target
- Actual bugs you're experiencing
- Migration effort vs benefit

**Q: Can I add my own fragile patterns?**  
A: Not yet in V1. Coming in V0.2 with custom rule configuration.

**Q: Why is GeometryReader considered fragile?**  
A: It's not always fragile, but in `ScrollView`/`List` it often causes layout issues. The rule helps catch common misuse.

**Q: What if I disagree with a fragile pattern classification?**  
A: That's valid! These are community wisdom, not absolute rules. Use `--category deprecated` to ignore fragile patterns.

## Examples

See [examples/FragilePatterns.swift](../examples/FragilePatterns.swift) for demonstration file with all 5 patterns.

## Contributing

Know of other fragile patterns? Submit an issue or PR with:
1. Pattern description
2. Why it's fragile (behavioral note)
3. iOS versions affected  
4. Modern replacement
5. Example code demonstrating the issue

---

**Remember:** Fragile patterns are warnings, not errors. Use them to improve code quality, not as strict gates.
