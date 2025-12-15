"""
File annotation module for swiftui-migrate.

This module handles writing inline comments directly into Swift source files
at the location of detected issues. All modifications are opt-in via --annotate flag.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List
from rich.console import Console

from .scanner import Finding


def _generate_comment_block(finding: Finding, indentation: str) -> str:
    """
    Generate a structured comment block for a finding.
    
    Args:
        finding: The Finding object
        indentation: The indentation to use for the comment block
    
    Returns:
        Multiline comment string with proper formatting
    """
    lines = [
        f"{indentation}// swiftui-migrate: {finding.rule.id}",
        f"{indentation}// {finding.rule.message}",
    ]
    
    # Add suggestion if available
    if finding.rule.suggestion:
        lines.append(f"{indentation}// Suggestion: {finding.rule.suggestion}")
    
    # Add iOS version requirement
    ios_version = finding.rule.ios_version if finding.rule.ios_version else "N/A"
    lines.append(f"{indentation}// Minimum iOS: {ios_version}")
    
    return "\n".join(lines)


def _comment_already_exists(lines: List[str], line_idx: int, rule_id: str) -> bool:
    """
    Check if a swiftui-migrate comment for this rule already exists above the line.
    
    Args:
        lines: All lines of the file
        line_idx: Index of the line with the finding (0-based)
        rule_id: The rule ID to check for
    
    Returns:
        True if comment already exists, False otherwise
    """
    # Look up to 10 lines above for an existing comment
    start_idx = max(0, line_idx - 10)
    
    for i in range(line_idx - 1, start_idx - 1, -1):
        line = lines[i].strip()
        
        # Check if this is our comment marker with the same rule ID
        if f"// swiftui-migrate: {rule_id}" in line:
            return True
        
        # Stop searching if we hit a non-comment line
        if not line.startswith("//") and line != "":
            break
    
    return False


def _get_indentation(line: str) -> str:
    """
    Extract the indentation (leading whitespace) from a line.
    
    Args:
        line: The line to analyze
    
    Returns:
        The leading whitespace string
    """
    return line[:len(line) - len(line.lstrip())]


def annotate_file(
    file_path: Path,
    findings: List[Finding],
    backup: bool = False,
    console: Console = None
) -> bool:
    """
    Annotate a single Swift file with inline comments for detected issues.
    
    Args:
        file_path: Path to the Swift file
        findings: List of findings for this file
        backup: Whether to create a .bak backup before modification
        console: Rich console for output (optional)
    
    Returns:
        True if file was modified, False otherwise
    """
    if console is None:
        console = Console()
    
    # Check if file is writable
    if not os.access(file_path, os.W_OK):
        console.print(
            f"[yellow]Warning: File is read-only, skipping: {file_path}[/yellow]"
        )
        return False
    
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines(keepends=True)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")
        return False
    
    # Sort findings by line number in descending order
    # This ensures we insert comments from bottom to top, avoiding line number shifts
    sorted_findings = sorted(findings, key=lambda f: f.line_number, reverse=True)
    
    modified = False
    
    for finding in sorted_findings:
        line_idx = finding.line_number - 1  # Convert to 0-based index
        
        # Validate line index
        if line_idx < 0 or line_idx >= len(lines):
            console.print(
                f"[yellow]Warning: Line {finding.line_number} out of range in {file_path}[/yellow]"
            )
            continue
        
        # Check if comment already exists
        if _comment_already_exists(lines, line_idx, finding.rule.id):
            continue
        
        # Get indentation from the target line
        target_line = lines[line_idx]
        indentation = _get_indentation(target_line)
        
        # Generate comment block
        comment_block = _generate_comment_block(finding, indentation)
        
        # Insert comment block above the target line
        lines.insert(line_idx, comment_block + "\n")
        modified = True
    
    # If no modifications were made, return early
    if not modified:
        return False
    
    # Create backup if requested
    if backup:
        backup_path = str(file_path) + ".bak"
        try:
            shutil.copy2(file_path, backup_path)
        except Exception as e:
            console.print(
                f"[yellow]Warning: Could not create backup for {file_path}: {e}[/yellow]"
            )
            return False
    
    # Write the modified content
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    except Exception as e:
        console.print(
            f"[red]Error: Could not write to {file_path}: {e}[/red]"
        )
        # If backup exists, try to restore
        if backup:
            try:
                shutil.copy2(backup_path, file_path)
                console.print(f"[yellow]Restored from backup: {file_path}[/yellow]")
            except Exception:
                pass
        return False
    
    return True


def annotate_findings(
    findings_by_file: Dict[str, List[Finding]],
    backup: bool = False,
    console: Console = None
) -> Dict[str, int]:
    """
    Annotate multiple Swift files with inline comments.
    
    Args:
        findings_by_file: Dictionary mapping file paths to their findings
        backup: Whether to create .bak backups before modification
        console: Rich console for output (optional)
    
    Returns:
        Dictionary with statistics: files_modified, files_skipped, files_failed
    """
    if console is None:
        console = Console()
    
    stats = {
        "files_modified": 0,
        "files_skipped": 0,
        "files_failed": 0,
    }
    
    for file_path_str, findings in findings_by_file.items():
        file_path = Path(file_path_str)
        
        # Skip if no findings
        if not findings:
            continue
        
        try:
            was_modified = annotate_file(file_path, findings, backup, console)
            
            if was_modified:
                stats["files_modified"] += 1
                console.print(f"[dim]Annotated: {file_path}[/dim]")
            else:
                stats["files_skipped"] += 1
        except Exception as e:
            stats["files_failed"] += 1
            console.print(f"[red]Error annotating {file_path}: {e}[/red]")
    
    return stats
