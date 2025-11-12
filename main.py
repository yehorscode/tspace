"""
Apparently its a good practice to say what the app does in this line. And i will abuse it and write absolutely nothing important and straight up jiberish.
"""

from textual.app import App, ComposeResult
from textual.widgets import Label
from textual.containers import VerticalScroll, Horizontal, Vertical
from textual.widgets import Header, Static, Button, Input, Footer
from textual.reactive import reactive
from textual.message import Message
import os
import sys


class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("tSpace")
        yield Button("space")
        yield Button("clean")


class AppContent(VerticalScroll):
    def getSpace(self, path = "/home/yehors/"):
        return os.path.getsize(path)
    def compose(self) -> ComposeResult:
        yield Vertical(id="content-container")

class tSpace(App):
    CSS_PATH = "styles/app.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="tS", id="header", time_format="%H:%M:%S")
        yield Horizontal(
            Sidebar(id="sidebar", classes="sidebar"),
            AppContent(id="app-content"),
        )
        yield Footer(id="footer", show_command_palette=False, classes="footer")


if __name__ == "__main__":
    app = tSpace()
    app.run()