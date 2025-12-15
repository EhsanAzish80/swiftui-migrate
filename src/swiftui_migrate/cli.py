"""CLI interface for swiftui-migrate."""

import sys
from pathlib import Path
from typing import List

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .scanner import SwiftScanner, group_findings_by_file, group_findings_by_rule
from .rules import get_all_rules

console = Console()


def _extract_ios_version(ios_version_str: str) -> int:
    """Extract major iOS version number from string like 'iOS 16'."""
    import re
    match = re.search(r'\d+', ios_version_str)
    return int(match.group()) if match else 0


@click.group()
@click.version_option(version=__version__, prog_name="swiftui-migrate")
def cli():
    """SwiftUI Migrate - Scan Swift/SwiftUI codebases for deprecated APIs."""
    pass


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    "--json",
    is_flag=True,
    help="Output as JSON for CI/CD integration",
)
@click.option(
    "--min-ios",
    type=str,
    help="Only show issues for iOS versions >= this (e.g., '16', '17')",
)
@click.option(
    "--severity",
    type=click.Choice(["warning", "error", "all"], case_sensitive=False),
    default="all",
    help="Filter by severity",
)
@click.option(
    "--category",
    type=click.Choice(["deprecated", "fragile", "all"], case_sensitive=False),
    default="all",
    help="Filter by category (deprecated APIs or fragile patterns)",
)
@click.option(
    "--group-by",
    type=click.Choice(["file", "rule", "category", "none"], case_sensitive=False),
    default="file",
    help="Group results by file, rule, category, or none",
)
@click.option(
    "--exclude",
    multiple=True,
    help="Directory patterns to exclude (can be specified multiple times)",
)
@click.option(
    "--fail-on-fragile/--no-fail-on-fragile",
    default=False,
    help="Exit with error code if fragile patterns found (default: no)",
)
def scan(paths: tuple, json: bool, min_ios: str, severity: str, category: str, group_by: str, exclude: tuple, fail_on_fragile: bool):
    """Scan Swift/SwiftUI files for deprecated or fragile API usage.

    PATHS: One or more files or directories to scan
    """
    if not json:
        console.print(f"[dim]swiftui-migrate v{__version__}[/dim]")
        console.print()

    # Convert paths to Path objects
    scan_paths = [Path(p).resolve() for p in paths]

    # Initialize scanner
    scanner = SwiftScanner()

    # Configure exclusions
    exclude_patterns = set(exclude) if exclude else None
    if exclude_patterns and not json:
        console.print(f"[dim]Excluding: {', '.join(exclude_patterns)}[/dim]\n")

    # Scan paths
    all_findings = []
    files_scanned = set()
    for path in scan_paths:
        if path.is_file():
            findings = scanner.scan_file(path)
            files_scanned.add(path)
        else:
            findings = scanner.scan_directory(path, exclude_patterns)
            # Track all scanned files
            for f in findings:
                files_scanned.add(f.file_path)
        all_findings.extend(findings)

    # Filter by min iOS version
    if min_ios:
        min_version = int(min_ios)
        all_findings = [f for f in all_findings if _extract_ios_version(f.rule.ios_version) >= min_version]
    
    # Filter by severity
    if severity != "all":
        all_findings = [f for f in all_findings if f.rule.severity == severity]
    
    # Filter by category
    if category != "all":
        all_findings = [f for f in all_findings if f.rule.category == category]

    # Display results
    if json:
        display_json_format(all_findings, len(files_scanned))
    else:
        display_text_format(all_findings, group_by, len(files_scanned))

    # Exit code logic
    if all_findings:
        # Count deprecated vs fragile
        deprecated_count = sum(1 for f in all_findings if f.rule.category == "deprecated")
        fragile_count = sum(1 for f in all_findings if f.rule.category == "fragile")
        
        # Only fail CI for deprecated by default, unless --fail-on-fragile is set
        should_fail = deprecated_count > 0 or (fail_on_fragile and fragile_count > 0)
        
        if should_fail:
            sys.exit(1)
        else:
            sys.exit(0)
    else:
        if not json:
            console.print("\nNo issues found.")
        sys.exit(0)


@cli.command()
def rules():
    """List all available detection rules."""
    all_rules = get_all_rules()

    table = Table(title="SwiftUI Migration Rules", show_header=True, header_style="bold")
    table.add_column("Rule ID", width=10)
    table.add_column("Name", width=30)
    table.add_column("Category", width=12)
    table.add_column("iOS Version", width=12)
    table.add_column("Message")

    for rule in all_rules:
        table.add_row(
            rule.id,
            rule.name,
            rule.category.title(),
            rule.ios_version,
            rule.message,
        )

    console.print(table)
    console.print(f"\n[dim]Total rules: {len(all_rules)}[/dim]")


def display_text_format(findings: List, group_by: str, files_scanned: int):
    """Display findings in text format."""
    if not findings:
        return

    if group_by == "category":
        # Group by category first, then by file within each category
        deprecated = [f for f in findings if f.rule.category == "deprecated"]
        fragile = [f for f in findings if f.rule.category == "fragile"]
        
        if deprecated:
            console.print("\n[bold red]Deprecated APIs[/bold red]")
            console.print("[dim]" + "─" * 60 + "[/dim]")
            _display_findings_by_file(deprecated)
        
        if fragile:
            console.print("\n[bold yellow]Fragile Patterns[/bold yellow]")
            console.print("[dim]" + "─" * 60 + "[/dim]")
            _display_findings_by_file(fragile)
    
    elif group_by == "file":
        _display_findings_by_file(findings)

    elif group_by == "rule":
        grouped = group_findings_by_rule(findings)
        for rule_id, rule_findings in grouped.items():
            rule = rule_findings[0].rule
            
            # Color based on category
            color = "red" if rule.category == "deprecated" else "yellow"
            console.print(f"\n[bold {color}]{rule_id}[/bold {color}] {rule.name}")
            console.print(f"  {rule.message}")
            if rule.suggestion:
                console.print(f"  [cyan]Suggestion:[/cyan] {rule.suggestion}")
                if rule.min_ios_version:
                    console.print(f"  [dim](Requires {rule.min_ios_version}+)[/dim]")
            
            console.print(f"  Found in {len(rule_findings)} location(s):")
            for finding in rule_findings:
                console.print(
                    f"    {finding.file_path}:{finding.line_number}:{finding.column}"
                )

    else:  # none
        for finding in findings:
            color = "red" if finding.rule.category == "deprecated" else "yellow"
            console.print(
                f"[{color}]{finding.file_path}:{finding.line_number}:{finding.column}[/{color}] "
                f"{finding.rule.id}: {finding.rule.message}"
            )
            if finding.rule.suggestion:
                console.print(f"  [cyan]Suggestion:[/cyan] {finding.rule.suggestion}")

    # Summary section
    _display_summary(findings, files_scanned)


def _display_findings_by_file(findings: List):
    """Helper to display findings grouped by file."""
    grouped = group_findings_by_file(findings)
    for file_path, file_findings in grouped.items():
        console.print(f"\n[bold]{file_path}[/bold]")
        for finding in file_findings:
            # Color based on category
            color = "red" if finding.rule.category == "deprecated" else "yellow"
            console.print(
                f"  [{color}]{finding.line_number}:{finding.column} "
                f"{finding.rule.id}:[/{color}] {finding.rule.message}"
            )
            console.print(f"  [dim]{finding.line_content.strip()}[/dim]")
            if finding.rule.suggestion:
                console.print(f"  [cyan]Suggestion:[/cyan] {finding.rule.suggestion}")
                if finding.rule.min_ios_version:
                    console.print(f"  [dim](Requires {finding.rule.min_ios_version}+)[/dim]")


def _display_summary(findings: List, files_scanned: int):
    """Display scan summary."""
    deprecated_count = sum(1 for f in findings if f.rule.category == "deprecated")
    fragile_count = sum(1 for f in findings if f.rule.category == "fragile")
    
    console.print("\n" + "─" * 60)
    console.print("[bold]Summary[/bold]")
    console.print("─" * 60)
    console.print(f"Files scanned:    {files_scanned}")
    console.print(f"Total issues:     {len(findings)}")
    if deprecated_count > 0:
        console.print(f"  [red]Deprecated:[/red]     {deprecated_count}")
    else:
        console.print(f"  Deprecated:     {deprecated_count}")
    if fragile_count > 0:
        console.print(f"  [yellow]Fragile:[/yellow]        {fragile_count}")
    else:
        console.print(f"  Fragile:        {fragile_count}")
    console.print("─" * 60)


def display_json_format(findings: List, files_scanned: int):
    """Display findings in JSON format."""
    import json

    deprecated_count = sum(1 for f in findings if f.rule.category == "deprecated")
    fragile_count = sum(1 for f in findings if f.rule.category == "fragile")

    output = {
        "version": __version__,
        "files_scanned": files_scanned,
        "summary": {
            "total": len(findings),
            "deprecated": deprecated_count,
            "fragile": fragile_count,
        },
        "findings": [f.to_dict() for f in findings],
    }
    console.print_json(json.dumps(output, indent=2))


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
