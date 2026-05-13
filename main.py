#!/usr/bin/env python3
"""
Proxmox VE Telegram Monitor - Entry point wrapper
Routes to src.main - uses the modular package structure
"""

import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run main from src
from main import main

if __name__ == "__main__":
    asyncio.run(main())
