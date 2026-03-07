"""Hardware and OS information."""
import platform
import os


def _safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def collect() -> dict:
    info = {
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "hostname": _safe(platform.node),
        },
        "cpu": {
            "brand": _safe(platform.processor),
            "cores_logical": _safe(lambda: _cpu_count()),
        },
        "ram": _safe(_ram_info),
        "disks": _safe(_disk_info, default=[]),
    }
    return info


def _cpu_count():
    try:
        import psutil
        return psutil.cpu_count(logical=True)
    except ImportError:
        return os.cpu_count()


def _ram_info():
    try:
        import psutil
        vm = psutil.virtual_memory()
        return {
            "total_gb": round(vm.total / 1024 ** 3, 2),
            "available_gb": round(vm.available / 1024 ** 3, 2),
            "used_percent": vm.percent,
        }
    except ImportError:
        return None


def _disk_info():
    try:
        import psutil
        disks = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / 1024 ** 3, 2),
                    "used_gb": round(usage.used / 1024 ** 3, 2),
                    "free_gb": round(usage.free / 1024 ** 3, 2),
                    "used_percent": usage.percent,
                })
            except (PermissionError, OSError):
                continue
        return disks
    except ImportError:
        return []
