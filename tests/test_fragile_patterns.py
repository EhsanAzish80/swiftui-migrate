"""Tests for fragile pattern detection."""

import pytest
from pathlib import Path
from swiftui_migrate.rules import get_fragile_rules, get_deprecated_rules, get_rule_by_id
from swiftui_migrate.scanner import SwiftScanner


def test_fragile_rules_count():
    """Test that we have the expected number of fragile rules."""
    fragile_rules = get_fragile_rules()
    assert len(fragile_rules) == 5
    
    deprecated_rules = get_deprecated_rules()
    assert len(deprecated_rules) == 5


def test_fragile_rules_have_behavioral_notes():
    """Test that all fragile rules have behavioral notes."""
    fragile_rules = get_fragile_rules()
    
    for rule in fragile_rules:
        assert rule.category == "fragile"
        assert rule.behavioral_note is not None
        assert len(rule.behavioral_note) > 50  # Meaningful explanation
        assert rule.severity == "warning"  # Fragile patterns are warnings


def test_navigationlink_isactive_detection(tmp_path):
    """Test FRAG001: NavigationLink with isActive parameter."""
    swift_file = tmp_path / "test.swift"
    swift_file.write_text("""
struct MyView: View {
    @State private var showDetail = false
    
    var body: some View {
        NavigationLink(destination: DetailView(), isActive: $showDetail) {
            Text("Show")
        }
    }
}
""")
    
    scanner = SwiftScanner()
    findings = scanner.scan_file(swift_file)
    
    frag001_findings = [f for f in findings if f.rule.id == "FRAG001"]
    assert len(frag001_findings) >= 1
    
    finding = frag001_findings[0]
    assert finding.rule.category == "fragile"
    assert "NavigationStack" in finding.rule.suggestion
    assert finding.rule.behavioral_note is not None


def test_bool_driven_navigation_detection(tmp_path):
    """Test FRAG002: Bool-driven navigation."""
    swift_file = tmp_path / "test.swift"
    swift_file.write_text("""
NavigationLink(destination: DetailView(), isActive: $isActive) {
    Text("Navigate")
}
""")
    
    scanner = SwiftScanner()
    findings = scanner.scan_file(swift_file)
    
    frag002_findings = [f for f in findings if f.rule.id == "FRAG002"]
    assert len(frag002_findings) >= 1
    assert "NavigationPath" in frag002_findings[0].rule.suggestion


def test_onappear_detection(tmp_path):
    """Test FRAG003: onAppear in row views."""
    swift_file = tmp_path / "test.swift"
    swift_file.write_text("""
List {
    ForEach(items) { item in
        Text(item)
            .onAppear {
                loadData()
            }
    }
}
""")
    
    scanner = SwiftScanner()
    findings = scanner.scan_file(swift_file)
    
    frag003_findings = [f for f in findings if f.rule.id == "FRAG003"]
    assert len(frag003_findings) >= 1
    
    finding = frag003_findings[0]
    assert ".task()" in finding.rule.suggestion
    assert "scrolling" in finding.rule.behavioral_note.lower()


def test_geometryreader_detection(tmp_path):
    """Test FRAG004: GeometryReader in scroll views."""
    swift_file = tmp_path / "test.swift"
    swift_file.write_text("""
ScrollView {
    GeometryReader { geometry in
        Color.blue.frame(height: geometry.size.width)
    }
}
""")
    
    scanner = SwiftScanner()
    findings = scanner.scan_file(swift_file)
    
    frag004_findings = [f for f in findings if f.rule.id == "FRAG004"]
    assert len(frag004_findings) >= 1
    
    finding = frag004_findings[0]
    assert finding.rule.category == "fragile"
    assert "layout" in finding.rule.behavioral_note.lower()


def test_observedobject_in_app_detection(tmp_path):
    """Test FRAG005: @ObservedObject in App struct."""
    swift_file = tmp_path / "test.swift"
    swift_file.write_text("""
@main
struct MyApp: App {
    @ObservedObject var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
""")
    
    scanner = SwiftScanner()
    findings = scanner.scan_file(swift_file)
    
    frag005_findings = [f for f in findings if f.rule.id == "FRAG005"]
    assert len(frag005_findings) >= 1
    
    finding = frag005_findings[0]
    assert "@StateObject" in finding.rule.suggestion
    assert "deallocation" in finding.rule.behavioral_note.lower()


def test_fragile_pattern_to_dict():
    """Test that fragile patterns include behavioral_note in to_dict()."""
    rule = get_rule_by_id("FRAG001")
    assert rule is not None
    assert rule.category == "fragile"
    
    from swiftui_migrate.scanner import Finding
    finding = Finding(
        file_path=Path("/test/file.swift"),
        line_number=10,
        line_content="NavigationLink(destination: DetailView(), isActive: $show) {",
        rule=rule,
        column=8
    )
    
    data = finding.to_dict()
    
    assert data["category"] == "fragile"
    assert "behavioral_note" in data
    assert len(data["behavioral_note"]) > 50
    assert "state" in data["behavioral_note"].lower()


def test_deprecated_patterns_no_behavioral_note():
    """Test that deprecated patterns don't have behavioral_note in output."""
    rule = get_rule_by_id("NAV001")
    assert rule is not None
    assert rule.category == "deprecated"
    
    from swiftui_migrate.scanner import Finding
    finding = Finding(
        file_path=Path("/test/file.swift"),
        line_number=10,
        line_content="NavigationView {",
        rule=rule,
        column=8
    )
    
    data = finding.to_dict()
    
    assert data["category"] == "deprecated"
    assert "behavioral_note" not in data


def test_fragile_patterns_dont_fail_ci():
    """Test that fragile patterns are warnings, not errors."""
    fragile_rules = get_fragile_rules()
    
    for rule in fragile_rules:
        assert rule.severity == "warning"
        assert rule.category == "fragile"


def test_mixed_deprecated_and_fragile(tmp_path):
    """Test file with both deprecated and fragile patterns."""
    swift_file = tmp_path / "test.swift"
    swift_file.write_text("""
struct MyView: View {
    @State private var showDetail = false
    
    var body: some View {
        NavigationView {  // Deprecated
            NavigationLink(destination: DetailView(), isActive: $showDetail) {  // Fragile
                Text("Show")
            }
        }
    }
}
""")
    
    scanner = SwiftScanner()
    findings = scanner.scan_file(swift_file)
    
    deprecated = [f for f in findings if f.rule.category == "deprecated"]
    fragile = [f for f in findings if f.rule.category == "fragile"]
    
    assert len(deprecated) >= 1  # NavigationView
    assert len(fragile) >= 1  # NavigationLink isActive
    
    # Verify they're categorized correctly
    assert any(f.rule.id == "NAV001" for f in deprecated)
    assert any(f.rule.id in ["FRAG001", "FRAG002"] for f in fragile)
