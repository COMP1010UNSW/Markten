"""
# MarkTen / Actions / web browser

Actions associated with web browsers
"""

import subprocess
import sys

from markten.__spinners import SpinnerTask
from markten.actions.__action_old import MarkTenAction


class open(MarkTenAction):
    """
    Open a URL in the user's web browser.
    """

    def __init__(
        self,
        url: str,
        /,
        new_tab: bool = False,
        new_window: bool = False,
    ) -> None:
        """Open the given URL in the user's default web browser.

        Parameters
        ----------
        url : str
            URL to open
        new_tab : bool
            Open a new tab
        new_window : bool
            Open in a new window
        """
        if new_tab and new_window:
            raise ValueError(
                "`new_tab` and `new_window` options are mutually exclusive"
            )
        self.url = url
        self.new_tab = new_tab
        self.new_window = new_window

    def get_name(self) -> str:
        return f"open '{self.url}'"

    async def run(self, task: SpinnerTask):
        options = []
        if self.new_tab:
            options.append("-t")
        if self.new_window:
            options.append("-n")
        task.running("Launching browser")
        # Run `python -m webbrowser` in a subprocess so we can hide the stdout
        # and stderr
        subprocess.Popen(
            (sys.executable, "-m", "webbrowser", *options, self.url),
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        task.succeed()
