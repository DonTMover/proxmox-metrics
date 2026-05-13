#!/usr/bin/env python3
"""
Quick health check and test of Proxmox Monitor installation
"""

import sys
import subprocess
from pathlib import Path

def check_command(cmd: str) -> bool:
    """Check if a command exists"""
    result = subprocess.run(["which", cmd], capture_output=True)
    return result.returncode == 0

def check_file(path: Path, readable: bool = True, writable: bool = False) -> bool:
    """Check if a file exists and has required permissions"""
    if not path.exists():
        return False
    if readable and not path.is_file():
        return False
    return True

def check_python_modules() -> bool:
    """Check if required Python modules are installed"""
    modules = ["telegram", "yaml", "psutil"]
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} - NOT INSTALLED")
            all_ok = False
    return all_ok

def main():
    print("Proxmox Monitor - Health Check")
    print("=" * 40)
    
    # Check configuration
    print("\n1. Configuration Files:")
    config_ok = check_file(Path("config.yaml"))
    print(f"  {'✓' if config_ok else '✗'} config.yaml")
    
    if config_ok:
        try:
            import yaml
            with open("config.yaml") as f:
                config = yaml.safe_load(f)
                token = config.get("telegram", {}).get("token", "")
                if token == "YOUR_BOT_TOKEN_HERE":
                    print("    ⚠ Telegram token not configured")
                elif not token:
                    print("    ⚠ Telegram token missing")
                else:
                    print("    ✓ Telegram token configured")
        except Exception as e:
            print(f"    ✗ Error reading config: {e}")
    
    # Check system commands
    print("\n2. System Commands:")
    commands = ["pvesh", "qm", "pct", "df", "free", "uptime"]
    cmd_ok = all(check_command(cmd) for cmd in commands)
    for cmd in commands:
        print(f"  {'✓' if check_command(cmd) else '✗'} {cmd}")
    
    # Check Python modules
    print("\n3. Python Modules:")
    modules_ok = check_python_modules()
    
    # Check Proxmox commands
    print("\n4. Proxmox Access:")
    try:
        result = subprocess.run(["pvesh", "get", "/nodes"], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("  ✓ Can access Proxmox API")
        else:
            print("  ✗ Cannot access Proxmox API")
    except Exception as e:
        print(f"  ✗ Error checking Proxmox: {e}")
    
    # Summary
    print("\n" + "=" * 40)
    if config_ok and cmd_ok and modules_ok:
        print("✓ All checks passed!")
        return 0
    else:
        print("✗ Some checks failed, see above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
