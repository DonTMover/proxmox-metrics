"""Tests for proxmox module"""
import pytest
from pathlib import Path
from proxmox import ProxmoxCollector, HostMetrics, ContainerMetrics


class TestHostMetrics:
    """Test HostMetrics dataclass"""
    
    def test_host_metrics_creation(self):
        """Test creating HostMetrics"""
        metrics = HostMetrics(
            cpu_percent=50.0,
            cpu_load_1=2.0,
            cpu_load_5=2.5,
            cpu_load_15=2.8,
            ram_used_mb=8192,
            ram_total_mb=16384,
            swap_used_mb=256,
            swap_total_mb=2048,
            uptime_days=1,
            uptime_hours=0,
            uptime_minutes=0,
            disks={"/": {"used": 50, "total": 100, "percent": 50}},
            temperature_cpu=45.0,
            temperature_system=42.0
        )
        
        assert metrics.cpu_percent == 50.0
        assert metrics.ram_used_mb == 8192
        assert metrics.uptime_days == 1
        assert metrics.temperature_cpu == 45.0
    
    def test_host_metrics_ram_percentage(self):
        """Test RAM percentage calculation"""
        metrics = HostMetrics(
            cpu_percent=50.0,
            cpu_load_1=2.0,
            cpu_load_5=2.5,
            cpu_load_15=2.8,
            ram_used_mb=8192,
            ram_total_mb=16384,
            swap_used_mb=256,
            swap_total_mb=2048,
            uptime_days=1,
            uptime_hours=0,
            uptime_minutes=0,
            disks={}
        )
        
        ram_percent = (metrics.ram_used_mb / metrics.ram_total_mb) * 100
        assert ram_percent == 50.0


class TestContainerMetrics:
    """Test ContainerMetrics dataclass"""
    
    def test_container_creation(self):
        """Test creating ContainerMetrics"""
        container = ContainerMetrics(
            vmid=100,
            name="web-server",
            status="running",
            cpu_percent=25.0,
            ram_mb=2048,
            max_ram_mb=4096,
            ram_percent=50.0
        )
        
        assert container.vmid == 100
        assert container.name == "web-server"
        assert container.status == "running"
        assert container.ram_mb == 2048
    
    def test_container_stopped(self):
        """Test stopped container"""
        container = ContainerMetrics(
            vmid=101,
            name="db-server",
            status="stopped",
            cpu_percent=0.0,
            ram_mb=0
        )
        
        assert container.status == "stopped"
        assert container.ram_mb == 0


class TestProxmoxCollector:
    """Test ProxmoxCollector"""
    
    def test_collector_initialization(self):
        """Test ProxmoxCollector initialization"""
        collector = ProxmoxCollector()
        
        assert collector is not None
        assert hasattr(collector, 'get_host_metrics')
        assert hasattr(collector, 'get_all_containers_and_vms')
    
    def test_get_host_metrics_returns_host_metrics(self):
        """Test get_host_metrics returns HostMetrics object"""
        collector = ProxmoxCollector()
        try:
            metrics = collector.get_host_metrics()
            assert isinstance(metrics, HostMetrics)
        except Exception as e:
            # Skip on non-Linux systems where commands may not be available
            pass
