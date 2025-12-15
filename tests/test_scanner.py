"""Tests for the rule engine and scanner."""

import pytest
from pathlib import Path
from swiftui_migrate.rules import get_all_rules, get_rule_by_id
from swiftui_migrate.scanner import SwiftScanner, Finding


def test_all_rules_have_required_fields():
    """Test that all rules have required fields."""
    rules = get_all_rules()
    assert len(rules) == 5  # v1 has 5 high-confidence rules
    
    for rule in rules:
        assert rule.id
        assert rule.name
        assert rule.pattern
        assert rule.message
        assert rule.severity in ["warning", "error"]
        assert rule.ios_version
        assert rule.suggestion is not None
        assert rule.min_ios_version is not None


def test_navigation_view_rule():
    """Test NavigationView detection."""
    rule = get_rule_by_id("NAV001")
    assert rule is not None
    assert rule.name == "NavigationView deprecated"
    assert "NavigationStack" in rule.suggestion
    assert rule.min_ios_version == "iOS 16.0"


def test_presentation_mode_rule():
    """Test @Environment(\.presentationMode) detection."""
    rule = get_rule_by_id("ENV001")
    assert rule is not None
    assert rule.name == "presentationMode deprecated"
    assert "dismiss" in rule.suggestion
    assert rule.min_ios_version == "iOS 15.0"


def test_scanner_detects_navigation_view(tmp_path):
    """Test scanner detects NavigationView usage."""
    swift_file = tmp_path / "test.swift"
    swift_file.write_text("""
import SwiftUI

struct ContentView: View {
    var body: some View {
        NavigationView {
            Text("Hello")
        }
    }
}
""")
    
    scanner = SwiftScanner()
    findings = scanner.scan_file(swift_file)
    
    assert len(findings) >= 1
    nav_findings = [f for f in findings if f.rule.id == "NAV001"]
    assert len(nav_findings) == 1
    assert nav_findings[0].line_number == 6


def test_scanner_detects_multiple_issues(tmp_path):
    """Test scanner detects multiple deprecated APIs."""
    swift_file = tmp_path / "test.swift"
    swift_file.write_text("""
import SwiftUI

struct ContentView: View {
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            Text("Hello")
                .navigationBarTitle("Title")
                .navigationBarItems(trailing: Button("Done") {})
                .edgesIgnoringSafeArea(.all)
        }
    }
}
""")
    
    scanner = SwiftScanner()
    findings = scanner.scan_file(swift_file)
    
    # Should find: NavigationView, presentationMode, navigationBarTitle, 
    # navigationBarItems, edgesIgnoringSafeArea
    assert len(findings) >= 5
    
    rule_ids = {f.rule.id for f in findings}
    assert "NAV001" in rule_ids  # NavigationView
    assert "ENV001" in rule_ids  # presentationMode
    assert "MOD001" in rule_ids  # navigationBarTitle
    assert "MOD002" in rule_ids  # navigationBarItems
    assert "MOD003" in rule_ids  # edgesIgnoringSafeArea


def test_finding_to_dict():
    """Test Finding.to_dict() returns complete structure."""
    rule = get_rule_by_id("NAV001")
    finding = Finding(
        file_path=Path("/test/file.swift"),
        line_number=10,
        line_content="        NavigationView {",
        rule=rule,
        column=8
    )
    
    data = finding.to_dict()
    
    assert data["rule_id"] == "NAV001"
    assert data["rule_name"] == "NavigationView deprecated"
    assert data["file_path"] == "/test/file.swift"
    assert data["line_number"] == 10
    assert data["column"] == 8
    assert data["matched_snippet"] == "NavigationView {"
    assert data["message"] == "NavigationView is deprecated in iOS 16+."
    assert data["severity"] == "warning"
    assert data["deprecated_in"] == "iOS 16"
    assert "NavigationStack" in data["migration_suggestion"]
    assert data["minimum_ios_version"] == "iOS 16.0"


def test_scanner_excludes_directories(tmp_path):
    """Test scanner respects exclude patterns."""
    # Create test structure
    pods_dir = tmp_path / "Pods"
    pods_dir.mkdir()
    (pods_dir / "test.swift").write_text("NavigationView {}")
    
    src_dir = tmp_path / "Sources"
    src_dir.mkdir()
    (src_dir / "test.swift").write_text("NavigationView {}")
    
    scanner = SwiftScanner()
    findings = scanner.scan_directory(tmp_path, exclude_patterns={"Pods"})
    
    # Should only find the one in Sources
    assert len(findings) == 1
    assert "Sources" in str(findings[0].file_path)
    assert "Pods" not in str(findings[0].file_path)
