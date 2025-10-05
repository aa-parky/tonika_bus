#!/usr/bin/env python3
"""
Update README.md with current project statistics

Automatically updates:
- Test counts per file
- Total test count
- Coverage statistics
- File tree structure

Usage:
    python update_readme_stats.py

    or via Make:
    make update-readme
"""

import ast
import re
import subprocess
from pathlib import Path


def count_tests_in_file(filepath: Path) -> int:
    """Count test functions in a Python test file."""
    try:
        with open(filepath, "r") as f:
            tree = ast.parse(f.read())

        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("test_"):
                    count += 1
        return count
    except Exception as e:
        print(f"Warning: Could not parse {filepath}: {e}")
        return 0


def get_test_counts() -> dict:
    """Get test counts for each test file."""
    tests_dir = Path("tests")
    counts = {}

    for test_file in tests_dir.glob("test_*.py"):
        count = count_tests_in_file(test_file)
        counts[test_file.name] = count

    return counts


def get_coverage_stats() -> dict:
    """Run pytest --cov and parse coverage output."""
    try:
        result = subprocess.run(
            ["pytest", "--cov=tonika_bus.core", "--cov-report=term", "--tb=no", "-q"],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Parse coverage output
        # Look for lines like: src/tonika_bus/core/bus.py      200     10    92%
        coverage = {}
        lines = result.stdout.split("\n")

        for line in lines:
            # Look for lines containing our source files
            if "tonika_bus/core/" in line and line.strip():
                parts = line.split()

                # Find the percentage (should end with %)
                percent = None
                for part in reversed(parts):
                    if part.endswith("%"):
                        percent = part.replace("%", "").strip()
                        break

                if percent and percent.replace(".", "").isdigit():
                    # Extract filename from path
                    filename = None
                    for part in parts:
                        if "tonika_bus/core/" in part:
                            filename = part.split("/")[-1]
                            break

                    if filename:
                        coverage[filename] = percent

        return coverage
    except Exception as e:
        print(f"Warning: Could not run coverage: {e}")
        return {}


def generate_file_tree() -> str:
    """Generate the file tree structure."""
    test_counts = get_test_counts()
    total_tests = sum(test_counts.values())

    tree = f"""tonika_bus/                          # ✅ COMPLETE - Core event system
├── src/
│   └── tonika_bus/                  # Main package
│       ├── __init__.py              # Package exports
│       └── core/                    # Core components
│           ├── __init__.py          # Core exports
│           ├── bus.py               # TonikaBus singleton
│           ├── module.py            # TonikaModule base class
│           └── events.py            # Event structures
│
├── tests/                           # ✅ {total_tests} tests
│   ├── __init__.py
│   ├── conftest.py                  # Shared fixtures
│   ├── test_bus.py                  # Bus tests ({test_counts.get('test_bus.py', 0)} tests)
│   ├── test_events.py               # Event tests ({test_counts.get('test_events.py', 0)} tests)
│   └── test_module.py               # Module tests ({test_counts.get('test_module.py', 0)} tests)
│
├── examples/                        # Working examples
│   ├── example_1_simple_counter_module.py
│   ├── example_2_midi_like_system.py
│   ├── example_3_request_response.py
│   └── example_4_module_dependencies.py
│
├── docs/                            # Documentation
│   ├── conf.py                      # Sphinx configuration
│   ├── index.rst                    # Documentation index
│   ├── tonika_bus_readme.md         # Detailed Bus docs
│   ├── goblin-laws.md               # Design principles
│   └── examples.md                  # Example documentation
│
├── htmlcov/                         # Coverage reports
├── pyproject.toml                   # Package configuration
├── LICENSE                          # GPL-3.0
└── README.md                        # This file"""

    return tree


def generate_coverage_table() -> str:
    """Generate the coverage statistics table."""
    coverage = get_coverage_stats()

    if not coverage:
        return """Name                Coverage
----------------------------------
src/tonika_bus/core/bus.py       (run pytest --cov)
src/tonika_bus/core/events.py   (run pytest --cov)
src/tonika_bus/core/module.py    (run pytest --cov)
----------------------------------
TOTAL                            (run pytest --cov)"""

    # Calculate total safely
    percentages = []
    for p in coverage.values():
        try:
            if p and p != "N/A":
                percentages.append(float(p))
        except ValueError:
            continue

    total = int(sum(percentages) / len(percentages)) if percentages else 0

    table = f"""Name                Coverage
----------------------------------
src/tonika_bus/core/bus.py       {coverage.get('bus.py', 'N/A')}%
src/tonika_bus/core/events.py   {coverage.get('events.py', 'N/A')}%
src/tonika_bus/core/module.py    {coverage.get('module.py', 'N/A')}%
----------------------------------
TOTAL                            {total}%"""

    return table


def update_readme():
    """Update README.md with current statistics."""
    readme_path = Path("README.md")

    if not readme_path.exists():
        print("ERROR: README.md not found")
        return False

    with open(readme_path, "r") as f:
        content = f.read()

    # Get statistics
    test_counts = get_test_counts()
    total_tests = sum(test_counts.values())
    coverage = get_coverage_stats()

    # Calculate total coverage safely
    percentages = []
    for p in coverage.values():
        try:
            if p and p != "N/A":
                percentages.append(float(p))
        except ValueError:
            continue

    total_coverage = int(sum(percentages) / len(percentages)) if percentages else 0

    # Generate new sections
    file_tree = generate_file_tree()
    coverage_table = generate_coverage_table()

    # Update file tree section
    tree_pattern = r"(## Current Project Structure\s+```\s*)(.*?)(\s*```)"
    if re.search(tree_pattern, content, re.DOTALL):
        content = re.sub(
            tree_pattern,
            f"\\1\n{file_tree}\n\\3",
            content,
            flags=re.DOTALL
        )
        print("✓ Updated file tree")
    else:
        print("⚠ Could not find file tree section")

    # Update coverage table section
    coverage_pattern = r"(### Test Coverage\s+```\s*)(.*?)(\s*```\s*\*\*)\d+ tests, \d+% coverage"
    if re.search(coverage_pattern, content, re.DOTALL):
        def replace_coverage(match):
            return f"{match.group(1)}\n{coverage_table}\n{match.group(3)}{total_tests} tests, {total_coverage}% coverage"

        content = re.sub(
            coverage_pattern,
            replace_coverage,
            content,
            flags=re.DOTALL
        )
        print("✓ Updated coverage table")
    else:
        print("⚠ Could not find coverage section")

    # Write updated content
    with open(readme_path, "w") as f:
        f.write(content)

    print(f"\n📊 Statistics:")
    print(f"   Total tests: {total_tests}")
    print(f"   Coverage: {total_coverage}%")
    print(f"   test_bus.py: {test_counts.get('test_bus.py', 0)} tests")
    print(f"   test_events.py: {test_counts.get('test_events.py', 0)} tests")
    print(f"   test_module.py: {test_counts.get('test_module.py', 0)} tests")

    return True


if __name__ == "__main__":
    print("🔄 Updating README.md with current statistics...\n")
    success = update_readme()

    if success:
        print("\n✅ README.md updated successfully!")
        print("\nRun 'git diff README.md' to see changes")
    else:
        print("\n❌ Failed to update README.md")
        exit(1)