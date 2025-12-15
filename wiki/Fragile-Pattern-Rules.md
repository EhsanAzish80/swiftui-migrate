# Fragile Pattern Rules

These rules detect patterns that aren't officially deprecated but are known to cause issues in modern SwiftUI.

**Exit code:** Fragile patterns produce **exit code 0** by default (warnings only). Use `--fail-on-fragile` to fail CI on these issues.

## Navigation Patterns (iOS 16+)

### FRAG001: NavigationLink with isActive

**Pattern:** `NavigationLink(destination:isActive:)`

**Problem:** Bool-based navigation bindings don't work reliably with `NavigationStack`. Can cause navigation state corruption.

**When it breaks:** iOS 16+ when using NavigationStack

**Example:**

```swift
// ⚠️ Fragile
@State private var showDetail = false

NavigationLink(destination: DetailView(), isActive: $showDetail) {
    Text("Show")
}

// ✅ Modern (iOS 16+)
@State private var path = NavigationPath()

NavigationStack(path: $path) {
    Button("Show") {
        path.append(DetailRoute.detail)
    }
    .navigationDestination(for: DetailRoute.self) { route in
        DetailView()
    }
}
```

**Migration guide:** Use value-based navigation with `NavigationPath` or `.navigationDestination(isPresented:)`.

### FRAG002: Bool-driven navigation bindings

**Pattern:** `NavigationLink(destination:isActive:)` with `@State` Bool

**Problem:** Same as FRAG001. Multiple Bool states can conflict, causing unexpected navigation behavior.

**When it breaks:** iOS 16+ NavigationStack

**Example:**

```swift
// ⚠️ Fragile - multiple Bool bindings
@State private var showA = false
@State private var showB = false

NavigationLink(destination: ViewA(), isActive: $showA) { }
NavigationLink(destination: ViewB(), isActive: $showB) { }

// ✅ Modern - single path
@State private var path = NavigationPath()

NavigationStack(path: $path) {
    // Push destinations onto path
    .navigationDestination(for: Route.self) { route in
        switch route {
        case .a: ViewA()
        case .b: ViewB()
        }
    }
}
```

## Performance Patterns

### FRAG003: .onAppear in List rows

**Pattern:** `.onAppear` inside `ForEach` or list row views

**Problem:** Triggers repeatedly during scrolling, causing excessive network requests or state updates.

**When it breaks:** Large lists, fast scrolling

**Example:**

```swift
// ⚠️ Fragile - loads on every scroll
List(items) { item in
    RowView(item: item)
        .onAppear {
            loadMoreData()  // Called many times!
        }
}

// ✅ Better - load at parent level
List(items) { item in
    RowView(item: item)
}
.task {
    await loadInitialData()
}
```

**Migration guide:** Move data loading to parent view's `.task()` or use `.onAppear` on List itself, not on rows.

### FRAG004: GeometryReader in scrollable views

**Pattern:** `GeometryReader` inside `ScrollView`, `List`, or other scrollable containers

**Problem:** Can cause layout loops, poor performance, and incorrect measurements.

**When it breaks:** Complex scroll views, dynamic content

**Example:**

```swift
// ⚠️ Fragile - layout loops
ScrollView {
    ForEach(items) { item in
        GeometryReader { geometry in
            RowView(width: geometry.size.width)
        }
    }
}

// ✅ iOS 17+ - containerRelativeFrame
ScrollView {
    ForEach(items) { item in
        RowView()
            .containerRelativeFrame(.horizontal)
    }
}
```

**Migration guide:** Use `containerRelativeFrame` (iOS 17+), `scrollViewReader`, or `visualEffect` modifier instead.

## State Management

### FRAG005: @ObservedObject with inline initialization

**Pattern:** `@ObservedObject var model = MyModel()`

**Problem:** SwiftUI may deallocate the object prematurely. View doesn't own the object lifecycle.

**When it breaks:** Root views, App scenes, complex view hierarchies

**Example:**

```swift
// ⚠️ Fragile - object may be deallocated
struct ContentView: View {
    @ObservedObject var appState = AppState()
    
    var body: some View {
        // appState might become nil!
    }
}

// ✅ Correct - @StateObject owns lifecycle
struct ContentView: View {
    @StateObject var appState = AppState()
    
    var body: some View {
        // appState persists across view updates
    }
}
```

**Migration guide:** Use `@StateObject` for object ownership in root views. Use `@ObservedObject` only when passing objects from parent views.

## Detection Accuracy

Fragile pattern rules are **heuristic-based**:

- May flag valid code that works fine in your app
- May miss patterns in unusual contexts
- Based on community-reported issues, not official deprecation

**Use judgment:** If a pattern works in your app, you can ignore the warning. But be aware of potential issues when updating iOS versions.

## Filtering

```bash
# Only fragile patterns
swiftui-migrate scan Sources/ --category fragile

# Ignore fragile patterns in CI
swiftui-migrate scan Sources/ --category deprecated
```

## Adding New Rules

Know a fragile pattern? Submit it via GitHub issues with:

- Pattern description
- Example code (before/after)
- iOS version where it breaks
- Real-world reproduction case

## Exit Code Behavior

```bash
# Default: warnings only (exit 0)
swiftui-migrate scan Sources/ --category fragile

# Strict: fail CI (exit 1)
swiftui-migrate scan Sources/ --category fragile --fail-on-fragile
```
