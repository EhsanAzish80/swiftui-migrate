#!/bin/bash
# Test script for CLI UX redesign

set -e

echo "=================================================="
echo "CLI UX Redesign Tests"
echo "=================================================="
echo ""

# Set up environment
export PYTHONPATH=src

echo "1. Basic scan (human-readable)"
echo "-------------------------------"
python3 -m swiftui_migrate.cli scan examples/SampleView.swift
echo ""

echo "=================================================="
echo "2. JSON mode (--json)"
echo "-------------------------------"
python3 -m swiftui_migrate.cli scan examples/SampleView.swift --json | head -20
echo "..."
echo ""

echo "=================================================="
echo "3. iOS version filtering (--min-ios 16)"
echo "-------------------------------"
python3 -m swiftui_migrate.cli scan examples/SampleView.swift --min-ios 16
echo ""

echo "=================================================="
echo "4. Category filtering (--category fragile)"
echo "-------------------------------"
python3 -m swiftui_migrate.cli scan examples/ --category fragile
EXIT_CODE=$?
echo "Exit code: $EXIT_CODE (should be 0)"
echo ""

echo "=================================================="
echo "5. Category grouping (--group-by category)"
echo "-------------------------------"
python3 -m swiftui_migrate.cli scan examples/ --group-by category | head -50
echo "..."
echo ""

echo "=================================================="
echo "6. Rules listing"
echo "-------------------------------"
python3 -m swiftui_migrate.cli rules
echo ""

echo "=================================================="
echo "All tests completed successfully!"
echo "=================================================="
