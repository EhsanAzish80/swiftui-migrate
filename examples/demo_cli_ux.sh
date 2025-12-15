#!/bin/bash
# Comprehensive CLI UX Demo

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  SwiftUI Migrate - CLI UX Redesign Demo                 ║"
echo "╔══════════════════════════════════════════════════════════╗"
echo ""

export PYTHONPATH=src

# 1. Default output - clean and professional
echo "┌─ Demo 1: Default Output (Professional, No Emojis) ─────┐"
echo ""
python3 -m swiftui_migrate.cli scan examples/SampleView.swift | head -30
echo "..."
echo ""
sleep 2

# 2. JSON output for CI
echo "┌─ Demo 2: JSON Output (CI Integration) ─────────────────┐"
echo ""
python3 -m swiftui_migrate.cli scan examples/SampleView.swift --json | jq '.summary'
echo ""
sleep 2

# 3. iOS version filtering
echo "┌─ Demo 3: iOS Version Filtering (--min-ios 16) ─────────┐"
echo ""
python3 -m swiftui_migrate.cli scan examples/SampleView.swift --min-ios 16
echo ""
sleep 2

# 4. Category filtering (fragile only)
echo "┌─ Demo 4: Fragile Patterns Only (Exit 0) ───────────────┐"
echo ""
python3 -m swiftui_migrate.cli scan examples/ --category fragile | head -30
FRAGILE_EXIT=$?
echo "..."
echo ""
echo "Exit code: $FRAGILE_EXIT (should be 0 - warnings only)"
echo ""
sleep 2

# 5. Category grouping
echo "┌─ Demo 5: Category Grouping ─────────────────────────────┐"
echo ""
python3 -m swiftui_migrate.cli scan examples/ --group-by category | head -40
echo "..."
echo ""
sleep 2

# 6. Rules command
echo "┌─ Demo 6: List All Rules ────────────────────────────────┐"
echo ""
python3 -m swiftui_migrate.cli rules
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  All demos completed successfully!                       ║"
echo "║                                                           ║"
echo "║  Key Features:                                            ║"
echo "║  ✓ No emojis, professional output                        ║"
echo "║  ✓ Standard file:line:column format                      ║"
echo "║  ✓ Comprehensive summary with files scanned              ║"
echo "║  ✓ --json flag for CI integration                        ║"
echo "║  ✓ --min-ios for targeted migrations                     ║"
echo "║  ✓ Category filtering (deprecated vs fragile)            ║"
echo "║  ✓ Fragile patterns don't fail CI by default             ║"
echo "╚══════════════════════════════════════════════════════════╝"
