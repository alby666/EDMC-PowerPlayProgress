"""
Custom `ttk.ProgressBar` to fix various display issues.

Hacks to fix various display issues with notebooks and their child widgets on Windows.

- style doesn't match the orange theme when in dark theme

Entire file may be imported by plugins.
"""

from tkinter import ttk
from config import config # type: ignore # noqa: N813

class ProgressBar(ttk.Progressbar):
    """
    Custom `ttk.ProgressBar` to fix various display issues.

    Hacks to fix various display issues with notebooks and their child widgets on Windows.

    - style doesn't match the orange theme when in dark theme
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style = ttk.Style()
        self._style.theme_create("elite_orange", parent="alt", settings={
            "TProgressbar": {
                "configure": {
                    "background": "orange",
                    "troughcolor": "white"
                }
            }
        })
        self._style.theme_create("elite_defautl", parent="alt", settings={
            "TProgressbar": {
                "configure": {
                    "background": "green",
                    "troughcolor": "white"
                }
            }
        })
        self._style.theme_use("elite_defautl") if config.get_int("theme") == 0 else self._style.theme_use("elite_orange")

    def update_theme(self):
        self._style.theme_use("elite_defautl") if config.get_int("theme") == 0 else self._style.theme_use("elite_orange")