"""Running processes information."""


def collect(limit: int = 50) -> dict:
    try:
        import psutil
    except ImportError:
        return {"error": "psutil not available", "processes": []}

    procs = []
    for p in psutil.process_iter(["pid", "name", "status", "cpu_percent", "memory_info", "username"]):
        try:
            info = p.info
            mem_mb = round(info["memory_info"].rss / 1024 ** 2, 2) if info.get("memory_info") else None
            procs.append({
                "pid": info["pid"],
                "name": info["name"],
                "status": info["status"],
                "cpu_percent": info["cpu_percent"],
                "memory_mb": mem_mb,
                "username": info.get("username"),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    procs.sort(key=lambda x: x.get("memory_mb") or 0, reverse=True)

    return {
        "total": len(procs),
        "shown": min(limit, len(procs)),
        "processes": procs[:limit],
    }
