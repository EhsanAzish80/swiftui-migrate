"""Core scanner for Swift/SwiftUI files."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

from .rules import Rule, get_all_rules


@dataclass
class Finding:
    """A single detected issue in a Swift file."""

    file_path: Path
    line_number: int
    line_content: str
    rule: Rule
    column: int = 0

    def __str__(self) -> str:
        """Format finding for display."""
        return (
            f"{self.file_path}:{self.line_number}:{self.column} "
            f"[{self.rule.severity.upper()}] {self.rule.id}: {self.rule.message}"
        )


class SwiftScanner:
    """Scanner for Swift/SwiftUI files."""

    def __init__(self, rules: List[Rule] | None = None):
        """Initialize scanner with rules."""
        self.rules = rules or get_all_rules()

    def scan_file(self, file_path: Path) -> List[Finding]:
        """Scan a single Swift file for issues."""
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, start=1):
                for rule in self.rules:
                    if match := re.search(rule.pattern, line):
                        findings.append(
                            Finding(
                                file_path=file_path,
                                line_number=line_num,
                                line_content=line.strip(),
                                rule=rule,
                                column=match.start(),
                            )
                        )

        except (IOError, UnicodeDecodeError) as e:
            # Skip files that can't be read
            pass

        return findings

    def scan_directory(
        self, directory: Path, exclude_patterns: Set[str] | None = None
    ) -> List[Finding]:
        """Recursively scan directory for Swift files."""
        exclude_patterns = exclude_patterns or {
            ".build",
            "DerivedData",
            "Pods",
            ".git",
            "node_modules",
            "vendor",
        }

        all_findings = []

        for swift_file in directory.rglob("*.swift"):
            # Skip excluded directories
            if any(excluded in swift_file.parts for excluded in exclude_patterns):
                continue

            findings = self.scan_file(swift_file)
            all_findings.extend(findings)

        return all_findings

    def scan_paths(self, paths: List[Path]) -> List[Finding]:
        """Scan multiple paths (files or directories)."""
        all_findings = []

        for path in paths:
            if path.is_file() and path.suffix == ".swift":
                all_findings.extend(self.scan_file(path))
            elif path.is_dir():
                all_findings.extend(self.scan_directory(path))

        return all_findings


def group_findings_by_file(findings: List[Finding]) -> dict[Path, List[Finding]]:
    """Group findings by file path."""
    grouped = {}
    for finding in findings:
        if finding.file_path not in grouped:
            grouped[finding.file_path] = []
        grouped[finding.file_path].append(finding)
    return grouped


def group_findings_by_rule(findings: List[Finding]) -> dict[str, List[Finding]]:
    """Group findings by rule ID."""
    grouped = {}
    for finding in findings:
        rule_id = finding.rule.id
        if rule_id not in grouped:
            grouped[rule_id] = []
        grouped[rule_id].append(finding)
    return grouped
