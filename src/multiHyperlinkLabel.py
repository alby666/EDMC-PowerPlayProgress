from functools import partial
import re
import tkinter as tk
import plug  # type: ignore[import]
from l10n import translations as tr  # type: ignore[import]
from ttkHyperlinkLabel import HyperlinkLabel  # type: ignore # noqa: N813

class MultiHyperlinkLabel(HyperlinkLabel):  # type: ignore
    """A subclass of HyperlinkLabel that supports multiple context menu options."""

    def _contextmenu(self, event: tk.Event) -> None:
        """
        Display a context menu with additional options when right-clicked.

        :param event: The event object.
        """
        menu = tk.Menu(tearoff=tk.FALSE)

        # Add a 'Copy' option
        menu.add_command(label=tr.tl('Copy'), command=self.copy)

        # Add a separator
        menu.add_separator()

        # Add multiple URLs to the context menu
        if str(self.name).startswith('system'):
            for url in plug.provides('system_url'):
                menu.add_command(
                    label=tr.tl("Open in {URL}").format(URL=url),
                    command=lambda u=url: self.open_system(u)  # Use lambda to bind the correct URL
                )

        if str(self.name).startswith('station'):
            for url in plug.provides('station_url'):
                menu.add_command(
                    label=tr.tl("Open in {URL}").format(URL=url),
                    command=lambda u=url: self.open_station(u)  # Use lambda to bind the correct URL
                )

        if str(self.name).startswith('ship'):
            for url in plug.provides('shipyard_url'):
                menu.add_command(
                    label=tr.tl("Open in {URL}").format(URL=url),
                    command=lambda u=url: self.open_shipyard(u)  # Use lambda to bind the correct URL
                )

        # Display the menu at the cursor's position
        menu.post(event.x_root, event.y_root)

    def copy(self) -> None:
        """Copy the current text to the clipboard."""
        self.clipboard_clear()
        self.clipboard_append(re.sub(r'^[^a-zA-Z]+', '', self['text']))