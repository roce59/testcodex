"""Installed applications detection (Windows only for now)."""
import os
import platform

try:
    import winreg
except ImportError:
    winreg = None

REGISTRY_PATHS = [
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
]


def get_windows_apps():
    if winreg is None:
        return []
    apps = []
    roots = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
    seen = set()
    for root in roots:
        for path in REGISTRY_PATHS:
            try:
                with winreg.OpenKey(root, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            sub_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, sub_name) as sub:
                                name, _ = winreg.QueryValueEx(sub, "DisplayName")
                                if not name or name in seen:
                                    continue
                                seen.add(name)
                                entry = {"name": name}
                                for field, key_name in [
                                    ("version", "DisplayVersion"),
                                    ("publisher", "Publisher"),
                                    ("install_date", "InstallDate"),
                                ]:
                                    try:
                                        entry[field], _ = winreg.QueryValueEx(sub, key_name)
                                    except OSError:
                                        entry[field] = None
                                apps.append(entry)
                        except OSError:
                            continue
            except OSError:
                continue
    return sorted(apps, key=lambda x: x["name"].lower())


def collect(search: str = "") -> dict:
    system = platform.system()
    if system == "Windows":
        apps = get_windows_apps()
    else:
        apps = []

    if search:
        term = search.lower()
        apps = [a for a in apps if term in a["name"].lower()]

    return {
        "platform": system,
        "count": len(apps),
        "apps": apps,
    }
