#!/usr/bin/env python3
"""Basic syntax and import verification for Python modules.

By default this now scans the `src/` directory recursively for `*.py` files
and verifies their syntax. If `src/` does not exist, the script falls back
to the original fixed file list in the repository root.
"""

import sys
from pathlib import Path
from typing import List


def verify_syntax(file_path: Path) -> bool:
    """Verify Python file syntax.

    Prints a single-line result for the file and returns True on success.
    """
    try:
        code = file_path.read_text()
        compile(code, str(file_path), 'exec')
        print(f"  ✓ {file_path}")
        return True
    except SyntaxError as e:
        print(f"  ✗ {file_path}: {e}")
        return False


def gather_files() -> List[Path]:
    src_dir = Path("src")
    if src_dir.is_dir():
        return sorted(src_dir.rglob("*.py"))

    # Fallback to original list (repository root)
    return [
        Path("proxmox.py"),
        Path("alerts.py"),
        Path("telegram.py"),
        Path("main.py"),
        Path("health_check.py"),
    ]


def main() -> int:
    print("Verifying Python module syntax...")
    print("=" * 40)

    files = gather_files()
    if not files:
        print("  ⚠ No Python files found to check")
        print("=" * 40)
        return 0

    all_ok = True
    for f in files:
        if f.exists():
            if not verify_syntax(f):
                all_ok = False
        else:
            # When using the fallback list, show not-found warnings
            print(f"  ⚠ {f.name} - not found")

    print("=" * 40)
    if all_ok:
        print("✓ All syntax checks passed!")
        return 0
    else:
        print("✗ Some files have syntax errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
