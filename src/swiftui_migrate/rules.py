"""Rule definitions for deprecated SwiftUI APIs."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Rule:
    """A rule for detecting deprecated or fragile SwiftUI API usage."""

    id: str
    name: str
    pattern: str
    message: str
    severity: str  # "warning" or "error"
    ios_version: str  # e.g., "iOS 17", "iOS 16", etc.
    suggestion: Optional[str] = None  # Migration suggestion
    min_ios_version: Optional[str] = None  # Minimum iOS version for suggestion
    category: str = "deprecated"  # "deprecated" or "fragile"
    behavioral_note: Optional[str] = None  # Why pattern is fragile (for fragile patterns)


# Fragile pattern rules (not deprecated, but known to break)
FRAGILE_RULES: List[Rule] = [
    # 1. NavigationLink with isActive parameter
    Rule(
        id="FRAG001",
        name="NavigationLink isActive pattern",
        pattern=r"NavigationLink\(.*isActive:",
        message="NavigationLink with isActive: can cause navigation state issues in iOS 16+.",
        severity="warning",
        ios_version="iOS 16",
        suggestion="Use NavigationStack with navigationDestination(isPresented:) or value-based navigation",
        min_ios_version="iOS 16.0",
        category="fragile",
        behavioral_note="The isActive binding pattern breaks with NavigationStack and can cause state desynchronization, "
                       "especially with programmatic navigation. Navigation state may not update correctly when "
                       "using back button or swipe gestures.",
    ),
    # 2. Bool-driven programmatic navigation
    Rule(
        id="FRAG002",
        name="Bool-driven navigation",
        pattern=r"NavigationLink\(.*isActive:\s*\$",
        message="Bool-driven navigation bindings are fragile in iOS 16+ NavigationStack.",
        severity="warning",
        ios_version="iOS 16",
        suggestion="Use NavigationPath with value-based navigation or navigationDestination(item:)",
        min_ios_version="iOS 16.0",
        category="fragile",
        behavioral_note="Bool bindings for navigation don't compose well with NavigationStack's path-based model. "
                       "Can lead to unexpected navigation behavior, state loss, or inability to deep-link. "
                       "Multiple bool flags for navigation stack becomes unmaintainable.",
    ),
    # 3. onAppear for data loading (simplified pattern)
    Rule(
        id="FRAG003",
        name="onAppear in row views",
        pattern=r"\.onAppear\s*\{",
        message="Using .onAppear inside row views can cause repeated loads during scrolling.",
        severity="warning",
        ios_version="All",
        suggestion="Move data loading to parent view's .task() or use .onAppear on List itself",
        min_ios_version="iOS 15.0",
        category="fragile",
        behavioral_note="onAppear fires every time a row appears during scrolling, causing redundant network "
                       "requests or computation. In iOS 15+, cells are aggressively recycled, triggering onAppear "
                       "multiple times for the same data. Can cause performance issues and API rate limiting. "
                       "Consider using .task() on the parent view or .refreshable for user-initiated refreshes.",
    ),
    # 4. GeometryReader in scrollable containers
    Rule(
        id="FRAG004",
        name="GeometryReader in scroll views",
        pattern=r"\bGeometryReader\s*\{",
        message="GeometryReader can cause layout loops and performance issues in scrollable views.",
        severity="warning",
        ios_version="All",
        suggestion="Use scrollViewReader, visualEffect modifier, or containerRelativeFrame instead",
        min_ios_version="iOS 17.0",
        category="fragile",
        behavioral_note="GeometryReader triggers layout recalculations that conflict with ScrollView's lazy "
                       "rendering. Can cause infinite layout loops, jittery scrolling, or incorrect sizing. "
                       "iOS 17+ offers better alternatives like visualEffect and scrollTransition for "
                       "scroll-based animations.",
    ),
    # 5. @ObservedObject in root views
    Rule(
        id="FRAG005",
        name="ObservedObject in App struct",
        pattern=r"@ObservedObject\s+(?:private\s+)?var\s+\w+\s*=\s*\w+\(",
        message="Using @ObservedObject with object initialization in App/root views can cause premature deallocation.",
        severity="warning",
        ios_version="All",
        suggestion="Use @StateObject for object ownership in root views, or pass via @EnvironmentObject",
        min_ios_version="iOS 14.0",
        category="fragile",
        behavioral_note="@ObservedObject doesn't own the object, relying on parent to keep it alive. In root views "
                       "or App struct, there's no parent, so object may be deallocated unexpectedly causing "
                       "crashes or state loss. @StateObject ensures SwiftUI owns the lifecycle.",
    ),
]


# Combined rules list
RULES: List[Rule] = [
    # High-confidence migration rules (v1)
    Rule(
        id="NAV001",
        name="NavigationView deprecated",
        pattern=r"\bNavigationView\s*\{",
        message="NavigationView is deprecated in iOS 16+.",
        severity="warning",
        ios_version="iOS 16",
        suggestion="Replace with NavigationStack for simple navigation or NavigationSplitView for multi-column layouts",
        min_ios_version="iOS 16.0",
        category="deprecated",
    ),
    # 2. @Environment(\.presentationMode) → @Environment(\.dismiss)
    Rule(
        id="ENV001",
        name="presentationMode deprecated",
        pattern=r"@Environment\(\\\.presentationMode\)",
        message="@Environment(\\.presentationMode) is deprecated in iOS 15+.",
        severity="warning",
        ios_version="iOS 15",
        suggestion="Replace with @Environment(\\.dismiss) and call dismiss() directly",
        min_ios_version="iOS 15.0",
        category="deprecated",
    ),
    # 3. .navigationBarTitle(_:displayMode:) deprecated
    Rule(
        id="MOD001",
        name="navigationBarTitle deprecated",
        pattern=r"\.navigationBarTitle\(",
        message="navigationBarTitle(_:displayMode:) is deprecated in iOS 14+.",
        severity="warning",
        ios_version="iOS 14",
        suggestion="Replace with .navigationTitle(_:) and .navigationBarTitleDisplayMode(_:)",
        min_ios_version="iOS 14.0",
        category="deprecated",
    ),
    # 4. .navigationBarItems(...) deprecated
    Rule(
        id="MOD002",
        name="navigationBarItems deprecated",
        pattern=r"\.navigationBarItems\(",
        message="navigationBarItems(leading:trailing:) is deprecated in iOS 14+.",
        severity="warning",
        ios_version="iOS 14",
        suggestion="Replace with .toolbar { ToolbarItem(placement: .navigationBarLeading/.navigationBarTrailing) { ... } }",
        min_ios_version="iOS 14.0",
        category="deprecated",
    ),
    # 5. .edgesIgnoringSafeArea(...) → .ignoresSafeArea(...)
    Rule(
        id="MOD003",
        name="edgesIgnoringSafeArea deprecated",
        pattern=r"\.edgesIgnoringSafeArea\(",
        message="edgesIgnoringSafeArea(_:) is deprecated in iOS 14+.",
        severity="warning",
        ios_version="iOS 14",
        suggestion="Replace with .ignoresSafeArea(_:edges:)",
        min_ios_version="iOS 14.0",
        category="deprecated",
    ),
] + FRAGILE_RULES  # Combine deprecated and fragile rules


def get_all_rules() -> List[Rule]:
    """Return all configured rules."""
    return RULES


def get_rules_by_severity(severity: str) -> List[Rule]:
    """Return rules filtered by severity."""
    return [rule for rule in RULES if rule.severity == severity]


def get_rule_by_id(rule_id: str) -> Optional[Rule]:
    """Return a specific rule by ID."""
    for rule in RULES:
        if rule.id == rule_id:
            return rule
    return None


def get_deprecated_rules() -> List[Rule]:
    """Return only deprecated API rules."""
    return [rule for rule in RULES if rule.category == "deprecated"]


def get_fragile_rules() -> List[Rule]:
    """Return only fragile pattern rules."""
    return [rule for rule in RULES if rule.category == "fragile"]


def get_rules_by_category(category: str) -> List[Rule]:
    """Return rules filtered by category (deprecated or fragile)."""
    return [rule for rule in RULES if rule.category == category]
