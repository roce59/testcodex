import os
import platform
import tkinter as tk
from tkinter import ttk

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
    apps = set()
    roots = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
    for root in roots:
        for path in REGISTRY_PATHS:
            try:
                with winreg.OpenKey(root, path) as uninstall_key:
                    for i in range(winreg.QueryInfoKey(uninstall_key)[0]):
                        try:
                            sub_key_name = winreg.EnumKey(uninstall_key, i)
                            with winreg.OpenKey(uninstall_key, sub_key_name) as sub_key:
                                name, _ = winreg.QueryValueEx(sub_key, 'DisplayName')
                                if name:
                                    apps.add(name)
                        except OSError:
                            continue
            except OSError:
                continue
    return sorted(apps)


def get_mac_apps():
    search_paths = [
        '/Applications',
        '/Applications/Utilities',
        os.path.expanduser('~/Applications'),
    ]
    apps = set()
    for base in search_paths:
        if os.path.isdir(base):
            for entry in os.scandir(base):
                if entry.name.endswith('.app'):
                    apps.add(entry.name[:-4])
    return sorted(apps)


def get_installed_apps():
    system = platform.system()
    if system == 'Windows':
        return get_windows_apps()
    if system == 'Darwin':
        return get_mac_apps()
    return []


def main():
    apps = get_installed_apps()

    root = tk.Tk()
    root.title('Installed Applications')
    root.geometry('500x600')

    frame = ttk.Frame(root, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
    for app in apps:
        listbox.insert(tk.END, app)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)

    root.mainloop()


if __name__ == '__main__':
    main()
