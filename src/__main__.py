#!/usr/bin/env python3
"""Entry point for running the proxmox-monitor as a module"""

import asyncio
from main import ProxmoxMonitor, main

if __name__ == "__main__":
    asyncio.run(main())
