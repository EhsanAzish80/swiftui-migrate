"""Rule definitions for deprecated SwiftUI APIs."""

from dataclasses import dataclass
from typing import List


@dataclass
class Rule:
    """A rule for detecting deprecated or fragile SwiftUI API usage."""

    id: str
    name: str
    pattern: str
    message: str
    severity: str  # "warning" or "error"
    ios_version: str  # e.g., "iOS 17", "iOS 16", etc.


# Core deprecated API rules
RULES: List[Rule] = [
    # NavigationView deprecated in iOS 16+
    Rule(
        id="NAV001",
        name="NavigationView deprecated",
        pattern="NavigationView",
        message="NavigationView is deprecated in iOS 16+. Use NavigationStack or NavigationSplitView instead.",
        severity="warning",
        ios_version="iOS 16",
    ),
    # GeometryReader abuse patterns
    Rule(
        id="GEO001",
        name="GeometryReader for frame only",
        pattern=r"GeometryReader\s*\{",
        message="GeometryReader may cause performance issues. Consider using .frame() or layout priorities.",
        severity="warning",
        ios_version="All",
    ),
    # @State in non-View types
    Rule(
        id="STATE001",
        name="@State outside View",
        pattern=r"@State\s+(?:private\s+)?var",
        message="@State should only be used in View structs. Use @StateObject or @ObservedObject for reference types.",
        severity="warning",
        ios_version="All",
    ),
    # .onAppear performance issues
    Rule(
        id="PERF001",
        name="Heavy work in onAppear",
        pattern=r"\.onAppear\s*\{",
        message="Avoid heavy synchronous work in .onAppear. Consider using .task() for async operations (iOS 15+).",
        severity="warning",
        ios_version="iOS 15",
    ),
    # Color literal deprecation
    Rule(
        id="COLOR001",
        name="Color literal deprecated",
        pattern=r"Color\(red:",
        message="Consider using Color asset catalog or semantic colors for better dark mode support.",
        severity="warning",
        ios_version="All",
    ),
    # List/ForEach without id
    Rule(
        id="LIST001",
        name="ForEach without explicit id",
        pattern=r"ForEach\([^,]+\)",
        message="ForEach should use explicit identifiers. Consider using id: \\\.self or Identifiable.",
        severity="warning",
        ios_version="All",
    ),
    # @EnvironmentObject without preview data
    Rule(
        id="ENV001",
        name="@EnvironmentObject usage",
        pattern=r"@EnvironmentObject\s+(?:private\s+)?var",
        message="@EnvironmentObject requires parent to inject object. Ensure preview providers supply test data.",
        severity="warning",
        ios_version="All",
    ),
    # Deprecated modifiers
    Rule(
        id="MOD001",
        name="navigationBarTitle deprecated",
        pattern=r"\.navigationBarTitle\(",
        message="navigationBarTitle is deprecated. Use .navigationTitle() instead.",
        severity="warning",
        ios_version="iOS 14",
    ),
    Rule(
        id="MOD002",
        name="navigationBarItems deprecated",
        pattern=r"\.navigationBarItems\(",
        message="navigationBarItems is deprecated. Use .toolbar() instead.",
        severity="warning",
        ios_version="iOS 14",
    ),
    # Binding misuse
    Rule(
        id="BIND001",
        name="Constant binding",
        pattern=r"\.constant\(",
        message="Using .constant() binding. Ensure this is intentional (creates non-mutable binding).",
        severity="warning",
        ios_version="All",
    ),
]


def get_all_rules() -> List[Rule]:
    """Return all configured rules."""
    return RULES


def get_rules_by_severity(severity: str) -> List[Rule]:
    """Return rules filtered by severity."""
    return [rule for rule in RULES if rule.severity == severity]


def get_rule_by_id(rule_id: str) -> Rule | None:
    """Return a specific rule by ID."""
    for rule in RULES:
        if rule.id == rule_id:
            return rule
    return None
