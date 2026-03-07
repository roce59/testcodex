"""Network interfaces and connectivity."""
import socket


def collect() -> dict:
    return {
        "hostname": _safe(socket.gethostname),
        "fqdn": _safe(socket.getfqdn),
        "interfaces": _safe(_interfaces, default=[]),
        "dns": _safe(_dns_servers, default=[]),
    }


def _safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def _interfaces():
    try:
        import psutil
        ifaces = []
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for name, addr_list in addrs.items():
            stat = stats.get(name)
            ipv4 = [a.address for a in addr_list if a.family == socket.AF_INET]
            ipv6 = [a.address for a in addr_list if a.family == socket.AF_INET6]
            ifaces.append({
                "name": name,
                "ipv4": ipv4,
                "ipv6": ipv6,
                "is_up": stat.isup if stat else None,
                "speed_mbps": stat.speed if stat else None,
            })
        return ifaces
    except ImportError:
        return []


def _dns_servers():
    import platform
    if platform.system() == "Windows":
        import subprocess
        result = subprocess.run(
            ["netsh", "interface", "ip", "show", "dns"],
            capture_output=True, text=True, timeout=5
        )
        servers = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("DNS") or ":" not in line:
                continue
            parts = line.split(":")
            if len(parts) == 2:
                servers.append(parts[1].strip())
        return servers
    return []
