"""
Example: Using the SwiftUI Migration Rule Engine programmatically.

This demonstrates how to use swiftui-migrate as a library to integrate
migration detection into your own tools.
"""

from pathlib import Path
from swiftui_migrate.scanner import SwiftScanner, group_findings_by_rule
from swiftui_migrate.rules import get_all_rules


def analyze_codebase(project_path: Path):
    """Analyze a SwiftUI codebase for migration issues."""
    
    # Initialize scanner
    scanner = SwiftScanner()
    
    # Scan the project
    print(f"Scanning {project_path}...\n")
    findings = scanner.scan_directory(project_path)
    
    if not findings:
        print("✓ No migration issues found!")
        return
    
    # Group by rule to show migration priorities
    grouped = group_findings_by_rule(findings)
    
    print(f"Found {len(findings)} migration issues across {len(grouped)} rules:\n")
    
    for rule_id, rule_findings in sorted(grouped.items()):
        rule = rule_findings[0].rule
        print(f"{'='*70}")
        print(f"Rule: {rule_id} - {rule.name}")
        print(f"Deprecated in: {rule.ios_version}")
        print(f"Occurrences: {len(rule_findings)}")
        print(f"\nIssue:")
        print(f"  {rule.message}")
        print(f"\nMigration:")
        print(f"  → {rule.suggestion}")
        print(f"  Requires: {rule.min_ios_version}+")
        print(f"\nLocations:")
        for finding in rule_findings[:3]:  # Show first 3
            print(f"  • {finding.file_path}:{finding.line_number}")
        if len(rule_findings) > 3:
            print(f"  ... and {len(rule_findings) - 3} more")
        print()


def get_migration_report(project_path: Path) -> dict:
    """Get structured migration report for CI/CD integration."""
    
    scanner = SwiftScanner()
    findings = scanner.scan_directory(project_path)
    
    # Convert to structured format
    return {
        "project": str(project_path),
        "total_findings": len(findings),
        "rules_triggered": len(set(f.rule.id for f in findings)),
        "findings": [f.to_dict() for f in findings],
        "summary_by_rule": {
            rule_id: {
                "count": len(rule_findings),
                "rule_name": rule_findings[0].rule.name,
                "migration_suggestion": rule_findings[0].rule.suggestion,
                "min_ios_version": rule_findings[0].rule.min_ios_version,
            }
            for rule_id, rule_findings in group_findings_by_rule(findings).items()
        }
    }


if __name__ == "__main__":
    # Example: Analyze the examples directory
    examples_dir = Path(__file__).parent.parent / "examples"
    
    if examples_dir.exists():
        analyze_codebase(examples_dir)
        
        print("\n" + "="*70)
        print("Getting structured report...")
        print("="*70 + "\n")
        
        report = get_migration_report(examples_dir)
        print(f"Project: {report['project']}")
        print(f"Total findings: {report['total_findings']}")
        print(f"Rules triggered: {report['rules_triggered']}")
        print(f"\nMigration priorities:")
        for rule_id, summary in report['summary_by_rule'].items():
            print(f"  {rule_id}: {summary['count']} occurrences - {summary['rule_name']}")
    else:
        print("No examples directory found. Please run from project root.")
