# Testcodex

This repository contains small examples. The current example shows how to list installed applications on Windows or macOS using a simple graphical interface.

## Usage

Run the script with Python (it requires `tkinter`, which ships with standard Python distributions). The script detects the operating system and lists applications for Windows or macOS.

```bash
python list_apps.py
```

A window will appear listing all discovered applications. On unsupported
platforms the list may be empty.
