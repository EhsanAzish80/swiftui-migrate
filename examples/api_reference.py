"""
Complete API reference for swiftui-migrate rule engine.

This file demonstrates all public APIs and their usage patterns.
"""

from pathlib import Path
from swiftui_migrate.scanner import SwiftScanner, Finding, group_findings_by_file, group_findings_by_rule
from swiftui_migrate.rules import get_all_rules, get_rule_by_id, get_rules_by_severity


# =============================================================================
# 1. RULE QUERYING API
# =============================================================================

def demo_rule_api():
    """Demonstrate rule querying APIs."""
    print("="*70)
    print("1. RULE QUERYING API")
    print("="*70 + "\n")
    
    # Get all available rules
    all_rules = get_all_rules()
    print(f"Total rules available: {len(all_rules)}\n")
    
    # Get a specific rule by ID
    rule = get_rule_by_id("NAV001")
    if rule:
        print(f"Rule NAV001:")
        print(f"  Name: {rule.name}")
        print(f"  Pattern: {rule.pattern}")
        print(f"  Suggestion: {rule.suggestion}")
        print(f"  Min iOS: {rule.min_ios_version}\n")
    
    # Filter rules by severity
    warnings = get_rules_by_severity("warning")
    print(f"Warning-level rules: {len(warnings)}\n")


# =============================================================================
# 2. SCANNING API
# =============================================================================

def demo_scanning_api():
    """Demonstrate file and directory scanning."""
    print("="*70)
    print("2. SCANNING API")
    print("="*70 + "\n")
    
    scanner = SwiftScanner()
    examples_dir = Path(__file__).parent
    
    # Scan a single file
    sample_file = examples_dir / "SampleView.swift"
    if sample_file.exists():
        findings = scanner.scan_file(sample_file)
        print(f"Scanned {sample_file.name}: {len(findings)} findings\n")
    
    # Scan a directory
    findings = scanner.scan_directory(examples_dir)
    print(f"Scanned directory {examples_dir.name}: {len(findings)} findings\n")
    
    # Scan with exclusions
    findings = scanner.scan_directory(
        examples_dir, 
        exclude_patterns={"build", "DerivedData"}
    )
    print(f"Scanned with exclusions: {len(findings)} findings\n")
    
    # Scan multiple paths
    paths = [examples_dir / "SampleView.swift"]
    findings = scanner.scan_paths(paths)
    print(f"Scanned {len(paths)} paths: {len(findings)} findings\n")


# =============================================================================
# 3. FINDING OBJECT API
# =============================================================================

def demo_finding_api():
    """Demonstrate Finding object usage."""
    print("="*70)
    print("3. FINDING OBJECT API")
    print("="*70 + "\n")
    
    scanner = SwiftScanner()
    sample_file = Path(__file__).parent / "SampleView.swift"
    
    if not sample_file.exists():
        print("Sample file not found\n")
        return
    
    findings = scanner.scan_file(sample_file)
    
    if not findings:
        print("No findings to demonstrate\n")
        return
    
    finding = findings[0]
    
    # Access Finding attributes
    print("Finding attributes:")
    print(f"  file_path: {finding.file_path}")
    print(f"  line_number: {finding.line_number}")
    print(f"  column: {finding.column}")
    print(f"  line_content: {finding.line_content.strip()}")
    print(f"  rule.id: {finding.rule.id}")
    print(f"  rule.name: {finding.rule.name}")
    print(f"  rule.suggestion: {finding.rule.suggestion}\n")
    
    # String representation
    print(f"String repr: {finding}\n")
    
    # Structured dictionary
    data = finding.to_dict()
    print("Structured output (to_dict()):")
    for key, value in data.items():
        print(f"  {key}: {value}")
    print()


# =============================================================================
# 4. GROUPING API
# =============================================================================

def demo_grouping_api():
    """Demonstrate finding grouping utilities."""
    print("="*70)
    print("4. GROUPING API")
    print("="*70 + "\n")
    
    scanner = SwiftScanner()
    sample_file = Path(__file__).parent / "SampleView.swift"
    
    if not sample_file.exists():
        print("Sample file not found\n")
        return
    
    findings = scanner.scan_file(sample_file)
    
    # Group by file
    by_file = group_findings_by_file(findings)
    print(f"Grouped by file: {len(by_file)} files")
    for file_path, file_findings in by_file.items():
        print(f"  {file_path.name}: {len(file_findings)} findings")
    print()
    
    # Group by rule
    by_rule = group_findings_by_rule(findings)
    print(f"Grouped by rule: {len(by_rule)} rules")
    for rule_id, rule_findings in by_rule.items():
        print(f"  {rule_id}: {len(rule_findings)} occurrences")
    print()


# =============================================================================
# 5. COMPLETE WORKFLOW EXAMPLE
# =============================================================================

def demo_complete_workflow():
    """Complete workflow: scan → analyze → report."""
    print("="*70)
    print("5. COMPLETE WORKFLOW")
    print("="*70 + "\n")
    
    # Step 1: Initialize
    scanner = SwiftScanner()
    project_path = Path(__file__).parent
    
    # Step 2: Scan
    findings = scanner.scan_directory(project_path)
    print(f"Scanned project: {len(findings)} total findings\n")
    
    if not findings:
        print("✓ No migration issues found!\n")
        return
    
    # Step 3: Analyze by priority
    by_rule = group_findings_by_rule(findings)
    
    # Step 4: Generate report
    print("Migration Priority Report:")
    print("-" * 70)
    
    for rule_id, rule_findings in sorted(by_rule.items()):
        rule = rule_findings[0].rule
        print(f"\n{rule_id}: {rule.name}")
        print(f"  Occurrences: {len(rule_findings)}")
        print(f"  Deprecated in: {rule.ios_version}")
        print(f"  Migration: {rule.suggestion}")
        print(f"  Requires: {rule.min_ios_version}+")
        print(f"  Files affected:")
        
        affected_files = set(f.file_path for f in rule_findings)
        for file_path in affected_files:
            print(f"    • {file_path.name}")
    
    print("\n" + "="*70)
    print(f"Total: {len(findings)} issues across {len(by_rule)} rules")
    print("="*70 + "\n")


# =============================================================================
# 6. CI/CD INTEGRATION EXAMPLE
# =============================================================================

def demo_ci_integration():
    """Example CI/CD integration pattern."""
    print("="*70)
    print("6. CI/CD INTEGRATION")
    print("="*70 + "\n")
    
    import json
    import sys
    
    scanner = SwiftScanner()
    project_path = Path(__file__).parent
    
    # Scan project
    findings = scanner.scan_directory(project_path)
    
    # Generate JSON report
    report = {
        "project": str(project_path),
        "total_findings": len(findings),
        "findings": [f.to_dict() for f in findings],
        "summary_by_rule": {
            rule_id: {
                "count": len(rule_findings),
                "severity": rule_findings[0].rule.severity,
                "migration": rule_findings[0].rule.suggestion,
            }
            for rule_id, rule_findings in group_findings_by_rule(findings).items()
        }
    }
    
    print("JSON Report (suitable for CI artifacts):")
    print(json.dumps(report, indent=2)[:500] + "...\n")
    
    # Exit code logic
    if findings:
        print(f"❌ CI Check Failed: {len(findings)} migration issues found")
        print(f"   Would exit with code: 1\n")
    else:
        print("✅ CI Check Passed: No migration issues")
        print(f"   Would exit with code: 0\n")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SwiftUI Migrate - Complete API Reference")
    print("="*70 + "\n")
    
    demo_rule_api()
    demo_scanning_api()
    demo_finding_api()
    demo_grouping_api()
    demo_complete_workflow()
    demo_ci_integration()
    
    print("="*70)
    print("API Reference Complete")
    print("="*70 + "\n")
