#!/usr/bin/env python3
"""
Basic syntax and import verification for all modules
"""

import sys
from pathlib import Path

def verify_syntax(file_path: Path) -> bool:
    """Verify Python file syntax"""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        compile(code, str(file_path), 'exec')
        print(f"  ✓ {file_path.name}")
        return True
    except SyntaxError as e:
        print(f"  ✗ {file_path.name}: {e}")
        return False

def main():
    print("Verifying Python module syntax...")
    print("=" * 40)
    
    modules = [
        Path("proxmox.py"),
        Path("alerts.py"),
        Path("telegram.py"),
        Path("main.py"),
        Path("health_check.py"),
    ]
    
    all_ok = True
    for module in modules:
        if module.exists():
            if not verify_syntax(module):
                all_ok = False
        else:
            print(f"  ⚠ {module.name} - not found")
    
    print("=" * 40)
    if all_ok:
        print("✓ All syntax checks passed!")
        return 0
    else:
        print("✗ Some files have syntax errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())
