# Deprecated API Rules

These rules detect officially deprecated SwiftUI APIs.

## Navigation (iOS 16+)

### NAV001: NavigationView

**Pattern:** `NavigationView`

**Deprecated in:** iOS 16

**Replacement:** `NavigationStack` or `NavigationSplitView`

**Example:**

```swift
// ❌ Deprecated
NavigationView {
    ContentView()
}

// ✅ iOS 16+
NavigationStack {
    ContentView()
}

// ✅ iOS 16+ (multi-column)
NavigationSplitView {
    SidebarView()
} detail: {
    DetailView()
}
```

**Migration guide:** Use `NavigationStack` for simple navigation hierarchies. Use `NavigationSplitView` for multi-column layouts (iPad, macOS).

## Environment (iOS 15+)

### ENV001: presentationMode

**Pattern:** `@Environment(\.presentationMode)`

**Deprecated in:** iOS 15

**Replacement:** `@Environment(\.dismiss)`

**Example:**

```swift
// ❌ Deprecated
@Environment(\.presentationMode) var presentationMode

Button("Close") {
    presentationMode.wrappedValue.dismiss()
}

// ✅ iOS 15+
@Environment(\.dismiss) var dismiss

Button("Close") {
    dismiss()
}
```

**Migration guide:** Replace `.presentationMode.wrappedValue.dismiss()` with `dismiss()`. Much cleaner.

## Modifiers (iOS 14+)

### MOD001: navigationBarTitle

**Pattern:** `navigationBarTitle(_:displayMode:)`

**Deprecated in:** iOS 14

**Replacement:** `.navigationTitle(_:)` + `.navigationBarTitleDisplayMode(_:)`

**Example:**

```swift
// ❌ Deprecated
.navigationBarTitle("Settings", displayMode: .inline)

// ✅ iOS 14+
.navigationTitle("Settings")
.navigationBarTitleDisplayMode(.inline)
```

### MOD002: navigationBarItems

**Pattern:** `navigationBarItems(leading:trailing:)`

**Deprecated in:** iOS 14

**Replacement:** `.toolbar` with `ToolbarItem`

**Example:**

```swift
// ❌ Deprecated
.navigationBarItems(
    leading: Button("Cancel") { },
    trailing: Button("Done") { }
)

// ✅ iOS 14+
.toolbar {
    ToolbarItem(placement: .navigationBarLeading) {
        Button("Cancel") { }
    }
    ToolbarItem(placement: .navigationBarTrailing) {
        Button("Done") { }
    }
}
```

### MOD003: edgesIgnoringSafeArea

**Pattern:** `edgesIgnoringSafeArea(_:)`

**Deprecated in:** iOS 14

**Replacement:** `.ignoresSafeArea(_:edges:)`

**Example:**

```swift
// ❌ Deprecated
.edgesIgnoringSafeArea(.all)

// ✅ iOS 14+
.ignoresSafeArea(.all)
```

## Detection Method

All rules use regex pattern matching, not AST parsing.

**Limitations:**
- May miss dynamic usage
- May flag commented-out code
- Cannot understand context

**False positives:** If you get a false positive, the code might still compile but the pattern is genuinely deprecated. Consider migrating anyway.

## Exit Codes

Finding any deprecated API causes **exit code 1** by default (fails CI).

Override with `--fail-on-fragile` to treat all issues equally.

## Filtering

```bash
# Only deprecated APIs
swiftui-migrate scan Sources/ --category deprecated

# Only iOS 16+ deprecations
swiftui-migrate scan Sources/ --category deprecated --min-ios 16
```

## Roadmap

Future rules planned:
- `GeometryReader` coordinate spaces (iOS 17+)
- `List` selection APIs (iOS 17+)
- Additional environment values

Submit suggestions via GitHub issues.
