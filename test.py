import tkinter as tk
from tkinter import messagebox

import requests
import semantic_version

plugin_version: str = '0.8.0'

def version_check() -> str:
    try:
        req = requests.get(url='https://api.github.com/repos/alby666/EDMC-PowerPlayProgress/releases/latest')
        data = req.json()
        if req.status_code != requests.codes.ok:
            raise requests.RequestException
    except (requests.RequestException, requests.JSONDecodeError) as ex:
        #logger.error('Failed to parse GitHub release info', exc_info=ex)
        return ''

    plugin_ver = semantic_version.Version(plugin_version)
    version = semantic_version.Version(data['tag_name'][1:])
    if version > plugin_ver:
        return str(version)
    return ''

def check_version():
    result = version_check()
    if result:
        messagebox.showinfo("Update Available", f"A new version is available: {result}")
    else:
        messagebox.showinfo("No Update", "You are using the latest version.")

# Create the main application window
root = tk.Tk()
root.title("Version Checker")

# Add a button to trigger the version check
check_button = tk.Button(root, text="Check for Updates", command=check_version)
check_button.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()