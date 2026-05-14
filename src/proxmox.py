#!/usr/bin/env python3
"""
Proxmox VE metrics collector - gathers CPU, RAM, disk, uptime and CT/VM status
"""

import subprocess
import json
import logging
import re
from typing import Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class HostMetrics:
    """Host system metrics"""
    cpu_percent: float
    cpu_load_1: float
    cpu_load_5: float
    cpu_load_15: float
    ram_used_mb: float
    ram_total_mb: float
    swap_used_mb: float
    swap_total_mb: float
    uptime_days: int
    uptime_hours: int
    uptime_minutes: int
    disks: Dict[str, Dict[str, float]]  # {"/": {"used": X, "total": Y, "percent": Z}}
    temperature_cpu: float | None = None
    temperature_system: float | None = None


@dataclass
class ContainerMetrics:
    """CT/VM metrics"""
    vmid: int
    name: str
    status: str  # "running" or "stopped"
    vm_type: str = "unknown"  # "container" or "vm"
    cpu_percent: float = 0.0
    ram_mb: float = 0.0
    max_ram_mb: float = 0.0
    ram_percent: float = 0.0
    network_rx: int = 0
    network_tx: int = 0


class ProxmoxCollector:
    """Collects metrics from Proxmox VE host"""

    def __init__(self, node: str = "pve"):
        self.node = node

    def _run_command(self, cmd: List[str]) -> str:
        """Execute shell command and return output"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                logger.warning(f"Command {cmd[0]} failed: {result.stderr}")
                return ""
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            logger.warning(f"Command {cmd[0]} timed out")
            return ""
        except Exception as e:
            logger.warning(f"Error running command {cmd[0]}: {e}")
            return ""

    def get_cpu_load(self) -> tuple[float, float, float, float]:
        """Get CPU usage % and load averages"""
        try:
            output = self._run_command(["uptime"])
            if not output:
                return 0.0, 0.0, 0.0, 0.0

            # Parse "load average: 0.15, 0.12, 0.09"
            match = re.search(r'load average[s]?:\s+([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)', output)
            if match:
                load1, load5, load15 = float(match.group(1)), float(match.group(2)), float(match.group(3))
                # Rough CPU percentage from load
                cpu_percent = min(100, load1 * 25)
                return cpu_percent, load1, load5, load15
        except Exception as e:
            logger.warning(f"Error parsing CPU load: {e}")
        return 0.0, 0.0, 0.0, 0.0

    def get_memory_info(self) -> tuple[float, float, float, float]:
        """Get RAM and Swap usage in MB"""
        try:
            output = self._run_command(["free", "-m"])
            if not output:
                return 0, 0, 0, 0

            lines = output.split('\n')
            # Parse "Mem:  total  used  free"
            mem_line = lines[1] if len(lines) > 1 else ""
            swap_line = lines[2] if len(lines) > 2 else ""

            mem_parts = mem_line.split()
            swap_parts = swap_line.split()

            if len(mem_parts) >= 3:
                mem_total = float(mem_parts[1])
                mem_used = float(mem_parts[2])
            else:
                mem_total, mem_used = 0, 0

            if len(swap_parts) >= 3:
                swap_total = float(swap_parts[1])
                swap_used = float(swap_parts[2])
            else:
                swap_total, swap_used = 0, 0

            return mem_used, mem_total, swap_used, swap_total
        except Exception as e:
            logger.warning(f"Error parsing memory info: {e}")
            return 0, 0, 0, 0

    def get_uptime(self) -> tuple[int, int, int]:
        """Get uptime in days, hours, minutes"""
        try:
            output = self._run_command(["uptime", "-p"])
            if not output:
                return 0, 0, 0

            # Parse "up X days, Y hours, Z minutes"
            days = hours = minutes = 0

            days_match = re.search(r'(\d+)\s+day', output)
            if days_match:
                days = int(days_match.group(1))

            hours_match = re.search(r'(\d+)\s+hour', output)
            if hours_match:
                hours = int(hours_match.group(1))

            mins_match = re.search(r'(\d+)\s+min', output)
            if mins_match:
                minutes = int(mins_match.group(1))

            return days, hours, minutes
        except Exception as e:
            logger.warning(f"Error parsing uptime: {e}")
            return 0, 0, 0

    def get_disk_usage(self, paths: List[str] = None) -> Dict[str, Dict[str, float]]:
        """Get disk usage for specified paths"""
        if paths is None:
            paths = ["/", "/var/lib/vz", "/boot"]

        result = {}
        for path in paths:
            try:
                output = self._run_command(["df", "-B1", path])
                if not output:
                    continue

                lines = output.split('\n')
                if len(lines) < 2:
                    continue

                parts = lines[1].split()
                if len(parts) >= 3:
                    total = float(parts[1])
                    used = float(parts[2])
                    percent = (used / total * 100) if total > 0 else 0
                    result[path] = {
                        "used": used / 1024 / 1024 / 1024,  # Convert to GB
                        "total": total / 1024 / 1024 / 1024,
                        "percent": percent
                    }
            except Exception as e:
                logger.warning(f"Error parsing disk usage for {path}: {e}")

        return result

    def get_temperature(self) -> tuple[float | None, float | None]:
        """Get CPU and system temperature from sensors"""
        cpu_temp = None
        sys_temp = None
        try:
            output = self._run_command(["sensors"])
            if not output:
                return None, None

            # Look for temperature patterns
            cpu_match = re.search(r'Core\s+\d+:\s+\+?([\d.]+)°C', output)
            if cpu_match:
                cpu_temp = float(cpu_match.group(1))

            sys_match = re.search(r'(System|SYSTIN):\s+\+?([\d.]+)°C', output)
            if sys_match:
                sys_temp = float(sys_match.group(2))
        except Exception as e:
            logger.debug(f"Could not read temperature: {e}")

        return cpu_temp, sys_temp

    def get_host_metrics(self) -> HostMetrics:
        """Collect all host metrics"""
        cpu_percent, load1, load5, load15 = self.get_cpu_load()
        ram_used, ram_total, swap_used, swap_total = self.get_memory_info()
        uptime_days, uptime_hours, uptime_mins = self.get_uptime()
        disks = self.get_disk_usage()
        temp_cpu, temp_sys = self.get_temperature()

        return HostMetrics(
            cpu_percent=cpu_percent,
            cpu_load_1=load1,
            cpu_load_5=load5,
            cpu_load_15=load15,
            ram_used_mb=ram_used,
            ram_total_mb=ram_total,
            swap_used_mb=swap_used,
            swap_total_mb=swap_total,
            uptime_days=uptime_days,
            uptime_hours=uptime_hours,
            uptime_minutes=uptime_mins,
            disks=disks,
            temperature_cpu=temp_cpu,
            temperature_system=temp_sys
        )

    def get_containers(self) -> List[ContainerMetrics]:
        """Get list of all CTs"""
        containers = []
        try:
            output = self._run_command(["pct", "list"])
            if not output:
                return containers

            lines = output.split('\n')[1:]  # Skip header
            for line in lines:
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) >= 3:
                    vmid = int(parts[0])
                    status = parts[1].lower()
                    name = parts[2]

                    containers.append(ContainerMetrics(
                        vmid=vmid,
                        name=name,
                        status=status,
                        vm_type="container"
                    ))
        except Exception as e:
            logger.warning(f"Error getting containers: {e}")

        return containers

    def get_vms(self) -> List[ContainerMetrics]:
        """Get list of all VMs"""
        vms = []
        try:
            output = self._run_command(["qm", "list"])
            if not output:
                return vms

            lines = output.split('\n')[1:]  # Skip header
            for line in lines:
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) >= 3:
                    vmid = int(parts[0])
                    status = parts[1].lower()
                    name = parts[2]

                    vms.append(ContainerMetrics(
                        vmid=vmid,
                        name=name,
                        status=status,
                        vm_type="vm"
                    ))
        except Exception as e:
            logger.warning(f"Error getting VMs: {e}")

        return vms

    def get_all_containers_and_vms(self) -> List[ContainerMetrics]:
        """Get all CTs and VMs combined"""
        return self.get_containers() + self.get_vms()
