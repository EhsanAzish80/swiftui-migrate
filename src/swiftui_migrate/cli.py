"""CLI interface for swiftui-migrate."""

import sys
from pathlib import Path
from typing import List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from . import __version__
from .scanner import SwiftScanner, group_findings_by_file, group_findings_by_rule
from .rules import get_all_rules

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="swiftui-migrate")
def cli():
    """SwiftUI Migrate - Scan Swift/SwiftUI codebases for deprecated APIs."""
    pass


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    "--format",
    type=click.Choice(["text", "summary", "json"], case_sensitive=False),
    default="text",
    help="Output format",
)
@click.option(
    "--severity",
    type=click.Choice(["warning", "error", "all"], case_sensitive=False),
    default="all",
    help="Filter by severity",
)
@click.option(
    "--group-by",
    type=click.Choice(["file", "rule", "none"], case_sensitive=False),
    default="file",
    help="Group results by file or rule",
)
@click.option(
    "--exclude",
    multiple=True,
    help="Directory patterns to exclude (can be specified multiple times)",
)
def scan(paths: tuple, format: str, severity: str, group_by: str, exclude: tuple):
    """Scan Swift/SwiftUI files for deprecated or fragile API usage.

    PATHS: One or more files or directories to scan
    """
    console.print(
        Panel.fit(
            f"[bold cyan]SwiftUI Migrate v{__version__}[/bold cyan]\n"
            "Scanning for deprecated and fragile SwiftUI APIs...",
            border_style="cyan",
        )
    )

    # Convert paths to Path objects
    scan_paths = [Path(p).resolve() for p in paths]

    # Initialize scanner
    scanner = SwiftScanner()

    # Configure exclusions
    exclude_patterns = set(exclude) if exclude else None
    if exclude_patterns:
        console.print(f"[dim]Excluding patterns: {', '.join(exclude_patterns)}[/dim]\n")

    # Scan paths
    all_findings = []
    for path in scan_paths:
        if path.is_file():
            findings = scanner.scan_file(path)
        else:
            findings = scanner.scan_directory(path, exclude_patterns)
        all_findings.extend(findings)

    # Filter by severity
    if severity != "all":
        all_findings = [f for f in all_findings if f.rule.severity == severity]

    # Display results
    if format == "text":
        display_text_format(all_findings, group_by)
    elif format == "summary":
        display_summary_format(all_findings)
    elif format == "json":
        display_json_format(all_findings)

    # Exit with error code if findings exist
    if all_findings:
        sys.exit(1)
    else:
        console.print("\n[bold green]✓ No issues found![/bold green]")
        sys.exit(0)


@cli.command()
def rules():
    """List all available detection rules."""
    all_rules = get_all_rules()

    table = Table(title="SwiftUI Migration Rules", show_header=True, header_style="bold cyan")
    table.add_column("Rule ID", style="cyan", width=10)
    table.add_column("Name", style="white", width=30)
    table.add_column("Severity", width=10)
    table.add_column("iOS Version", width=12)
    table.add_column("Message", style="dim")

    for rule in all_rules:
        severity_color = "yellow" if rule.severity == "warning" else "red"
        table.add_row(
            rule.id,
            rule.name,
            f"[{severity_color}]{rule.severity.upper()}[/{severity_color}]",
            rule.ios_version,
            rule.message,
        )

    console.print(table)
    console.print(f"\n[dim]Total rules: {len(all_rules)}[/dim]")


def display_text_format(findings: List, group_by: str):
    """Display findings in text format."""
    if not findings:
        return

    if group_by == "file":
        grouped = group_findings_by_file(findings)
        for file_path, file_findings in grouped.items():
            console.print(f"\n[bold white]{file_path}[/bold white]")
            for finding in file_findings:
                severity_color = "yellow" if finding.rule.severity == "warning" else "red"
                console.print(
                    f"  [dim]Line {finding.line_number}:{finding.column}[/dim] "
                    f"[{severity_color}]{finding.rule.id}[/{severity_color}] "
                    f"{finding.rule.message}"
                )
                console.print(f"    [dim]│[/dim] {finding.line_content}")

    elif group_by == "rule":
        grouped = group_findings_by_rule(findings)
        for rule_id, rule_findings in grouped.items():
            rule = rule_findings[0].rule
            severity_color = "yellow" if rule.severity == "warning" else "red"
            console.print(
                f"\n[bold {severity_color}]{rule_id}[/bold {severity_color}] - {rule.name}"
            )
            console.print(f"  [dim]{rule.message}[/dim]")
            console.print(f"  [dim]Found {len(rule_findings)} occurrence(s):[/dim]")
            for finding in rule_findings:
                console.print(
                    f"    • {finding.file_path}:{finding.line_number}:{finding.column}"
                )

    else:  # none
        for finding in findings:
            severity_color = "yellow" if finding.rule.severity == "warning" else "red"
            console.print(
                f"[{severity_color}]{finding.rule.severity.upper()}[/{severity_color}] "
                f"{finding.file_path}:{finding.line_number}:{finding.column} "
                f"[{severity_color}]{finding.rule.id}[/{severity_color}]: {finding.rule.message}"
            )

    console.print(f"\n[bold]Total issues found: {len(findings)}[/bold]")


def display_summary_format(findings: List):
    """Display findings in summary format."""
    if not findings:
        return

    grouped_by_rule = group_findings_by_rule(findings)
    grouped_by_file = group_findings_by_file(findings)

    # Summary table
    table = Table(title="Scan Summary", show_header=True, header_style="bold cyan")
    table.add_column("Rule ID", style="cyan")
    table.add_column("Rule Name", style="white")
    table.add_column("Count", justify="right", style="bold yellow")
    table.add_column("Severity")

    for rule_id, rule_findings in sorted(
        grouped_by_rule.items(), key=lambda x: len(x[1]), reverse=True
    ):
        rule = rule_findings[0].rule
        severity_color = "yellow" if rule.severity == "warning" else "red"
        table.add_row(
            rule_id,
            rule.name,
            str(len(rule_findings)),
            f"[{severity_color}]{rule.severity.upper()}[/{severity_color}]",
        )

    console.print(table)
    console.print(f"\n[bold]Total files scanned: {len(grouped_by_file)}[/bold]")
    console.print(f"[bold]Total issues found: {len(findings)}[/bold]")


def display_json_format(findings: List):
    """Display findings in JSON format."""
    import json

    output = {
        "version": __version__,
        "total_findings": len(findings),
        "findings": [
            {
                "file": str(f.file_path),
                "line": f.line_number,
                "column": f.column,
                "rule_id": f.rule.id,
                "rule_name": f.rule.name,
                "severity": f.rule.severity,
                "message": f.rule.message,
                "ios_version": f.rule.ios_version,
                "line_content": f.line_content,
            }
            for f in findings
        ],
    }
    console.print_json(json.dumps(output, indent=2))


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
