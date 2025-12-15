"""
Demonstration: Fragile Pattern Detection

This script demonstrates the new fragile pattern detection feature.
"""

from pathlib import Path
from swiftui_migrate.scanner import SwiftScanner, group_findings_by_rule
from swiftui_migrate.rules import get_deprecated_rules, get_fragile_rules


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def demo_rule_categories():
    """Show the two categories of rules."""
    print_section("RULE CATEGORIES")
    
    deprecated = get_deprecated_rules()
    fragile = get_fragile_rules()
    
    print(f"📊 Total Rules: {len(deprecated) + len(fragile)}")
    print(f"  ⚠️  Deprecated APIs: {len(deprecated)} (fail CI by default)")
    print(f"  🔧 Fragile Patterns: {len(fragile)} (warnings only)\n")
    
    print("Fragile Pattern Rules:")
    for rule in fragile:
        print(f"  {rule.id}: {rule.name}")
        print(f"    → {rule.suggestion[:60]}...")
        print()


def demo_deprecated_vs_fragile():
    """Compare deprecated API vs fragile pattern detection."""
    print_section("DEPRECATED vs FRAGILE: Example File")
    
    scanner = SwiftScanner()
    
    # Scan file with deprecated APIs
    deprecated_file = Path("examples/SampleView.swift")
    if deprecated_file.exists():
        findings = scanner.scan_file(deprecated_file)
        deprecated = [f for f in findings if f.rule.category == "deprecated"]
        fragile = [f for f in findings if f.rule.category == "fragile"]
        
        print(f"📄 {deprecated_file.name}:")
        print(f"  Deprecated APIs: {len(deprecated)}")
        print(f"  Fragile patterns: {len(fragile)}")
        print()
    
    # Scan file with fragile patterns
    fragile_file = Path("examples/FragilePatterns.swift")
    if fragile_file.exists():
        findings = scanner.scan_file(fragile_file)
        deprecated = [f for f in findings if f.rule.category == "deprecated"]
        fragile = [f for f in findings if f.rule.category == "fragile"]
        
        print(f"📄 {fragile_file.name}:")
        print(f"  Deprecated APIs: {len(deprecated)}")
        print(f"  Fragile patterns: {len(fragile)}")
        print()


def demo_behavioral_notes():
    """Show behavioral notes for fragile patterns."""
    print_section("BEHAVIORAL NOTES (Why Patterns Are Fragile)")
    
    scanner = SwiftScanner()
    fragile_file = Path("examples/FragilePatterns.swift")
    
    if not fragile_file.exists():
        print("FragilePatterns.swift not found\n")
        return
    
    findings = scanner.scan_file(fragile_file)
    fragile = [f for f in findings if f.rule.category == "fragile"]
    
    # Show unique rules
    seen_rules = set()
    for f in fragile:
        if f.rule.id not in seen_rules:
            seen_rules.add(f.rule.id)
            print(f"🔧 {f.rule.id}: {f.rule.name}")
            print(f"  Why fragile:")
            # Wrap behavioral note
            note = f.rule.behavioral_note
            words = note.split()
            line = "    "
            for word in words:
                if len(line) + len(word) + 1 > 70:
                    print(line)
                    line = "    " + word
                else:
                    line += " " + word if line != "    " else word
            if line != "    ":
                print(line)
            print()


def demo_structured_output():
    """Show structured output differences."""
    print_section("STRUCTURED OUTPUT: Deprecated vs Fragile")
    
    scanner = SwiftScanner()
    fragile_file = Path("examples/FragilePatterns.swift")
    
    if not fragile_file.exists():
        print("FragilePatterns.swift not found\n")
        return
    
    findings = scanner.scan_file(fragile_file)
    
    # Show one deprecated (if any)
    deprecated = [f for f in findings if f.rule.category == "deprecated"]
    if deprecated:
        print("⚠️  Deprecated API (NAV001):")
        data = deprecated[0].to_dict()
        print(f"  category: {data['category']}")
        print(f"  message: {data['message']}")
        print(f"  migration_suggestion: {data['migration_suggestion'][:50]}...")
        print(f"  behavioral_note: (not present for deprecated)\n")
    
    # Show one fragile
    fragile = [f for f in findings if f.rule.category == "fragile"]
    if fragile:
        print("🔧 Fragile Pattern (FRAG001):")
        data = fragile[0].to_dict()
        print(f"  category: {data['category']}")
        print(f"  message: {data['message']}")
        print(f"  migration_suggestion: {data['migration_suggestion'][:50]}...")
        print(f"  behavioral_note: {data['behavioral_note'][:80]}...\n")


def demo_ci_behavior():
    """Explain CI/CD behavior."""
    print_section("CI/CD BEHAVIOR")
    
    print("Exit Code Logic:")
    print()
    print("Scenario 1: Only deprecated APIs found")
    print("  Command: swiftui-migrate scan ./Sources")
    print("  Result:  Exit 1 ❌ (fails CI)")
    print()
    print("Scenario 2: Only fragile patterns found")
    print("  Command: swiftui-migrate scan ./Sources")
    print("  Result:  Exit 0 ✅ (passes CI)")
    print()
    print("Scenario 3: Both deprecated + fragile found")
    print("  Command: swiftui-migrate scan ./Sources")
    print("  Result:  Exit 1 ❌ (fails due to deprecated)")
    print()
    print("Scenario 4: Strict mode (fail on fragile)")
    print("  Command: swiftui-migrate scan ./Sources --fail-on-fragile")
    print("  Result:  Exit 1 ❌ (fails if ANY issues)")
    print()
    print("💡 Default behavior: Fragile patterns are informational")
    print("   Use --fail-on-fragile to enforce strict checking")
    print()


def demo_filtering():
    """Show filtering capabilities."""
    print_section("FILTERING OPTIONS")
    
    scanner = SwiftScanner()
    examples_dir = Path("examples")
    
    if not examples_dir.exists():
        return
    
    all_findings = scanner.scan_directory(examples_dir)
    deprecated = [f for f in all_findings if f.rule.category == "deprecated"]
    fragile = [f for f in all_findings if f.rule.category == "fragile"]
    
    print(f"Total findings in examples/: {len(all_findings)}")
    print()
    print("Filter by category:")
    print(f"  --category deprecated → {len(deprecated)} findings")
    print(f"  --category fragile    → {len(fragile)} findings")
    print(f"  --category all        → {len(all_findings)} findings (default)")
    print()
    print("Group by category:")
    print("  --group-by category → Shows deprecated first, then fragile")
    print()


def main():
    """Run all demonstrations."""
    print("\n" + "="*70)
    print("  FRAGILE PATTERN DETECTION - DEMONSTRATION")
    print("="*70)
    
    demo_rule_categories()
    demo_deprecated_vs_fragile()
    demo_behavioral_notes()
    demo_structured_output()
    demo_ci_behavior()
    demo_filtering()
    
    print("="*70)
    print("  For full documentation, see docs/FRAGILE_PATTERNS.md")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
