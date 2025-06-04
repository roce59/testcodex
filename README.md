# Testcodex

This repository contains small examples. The current example shows how to list installed applications on Windows or macOS using a simple graphical interface.

## Usage

Run the script with Python (it requires `tkinter`, which ships with standard Python distributions). The script detects the operating system and lists applications for Windows or macOS.

```bash
python list_apps.py
```

A window will appear listing all discovered applications. On unsupported
platforms the list may be empty.

If you see `ModuleNotFoundError: No module named '_tkinter'`, your Python
installation lacks Tk support. Install a Python distribution that includes
Tkinter (for example from [python.org](https://www.python.org)) or install the
`tcl-tk` package via your system's package manager.
