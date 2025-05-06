"""
Custom `ttk.ProgressBar` to fix various display issues.
Hacks to fix various display issues with notebooks and their child widgets on Windows.
- style doesn't match the orange theme when in dark theme
Entire file may be imported by plugins.
"""

from tkinter import ttk

class ProgressBar(ttk.Progressbar):
    """
    Custom `ttk.ProgressBar` to fix various display issues.
    Hacks to fix various display issues with notebooks and their child widgets on Windows.
    - style doesn't match the orange theme when in dark theme
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style = ttk.Style()
        self._theme_option = 0
        self._style.theme_create("ppp_elite_orange", parent="alt", settings={
            "TProgressbar": {
                "configure": {
                    "background": "orange",
                    "troughcolor": "white"
                }
            }
        })
        self._style.theme_create("ppp_elite_defautl", parent="alt", settings={
            "TProgressbar": {
                "configure": {
                    "background": "green",
                    "troughcolor": "white"
                }
            }
        })
        self._style.theme_use("ppp_elite_defautl") if self._theme_option == 0 else self._style.theme_use("ppp_elite_orange")

    @property
    def theme_option(self):
        """Getter for theme_option."""
        return self._theme_option

    @theme_option.setter
    def theme_option(self, value):
        """Setter for theme_option, ensures it's an integer."""
        if isinstance(value, int):
            self._theme_option = value
        else:
            raise ValueError("theme_option must be an integer")


    def update_theme(self):
        self._style.theme_use("elite_defautl") if self._theme_option == 0 else self._style.theme_use("elite_orange")