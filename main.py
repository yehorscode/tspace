"""
Apparently its a good practice to say what the app does in this line. And i will abuse it and write absolutely nothing important and straight up jiberish.
"""
from scan import getSize, getSpace, getFolderSpace
from textual.app import App, ComposeResult
from textual.widgets import Label
from textual.containers import VerticalScroll, Horizontal, Vertical
from textual.widgets import Header, Static, Button, Input, Footer, Label
from textual.reactive import reactive
from textual.message import Message
import os
import sys
from humanize import naturalsize


class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("tSpace")
        yield Button("space")
        yield Button("clean")


class AppContent(VerticalScroll):
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "scan-dir":
            to_search_dir = self.query_one("#dir-input", Input).value
            space = naturalsize(getFolderSpace(to_search_dir))
            self.query_one("#directory-size", Label).update(f"{space}")
        
    def compose(self) -> ComposeResult:
        yield Vertical(
            Input(placeholder="Directory", id="dir-input", classes="dir-input", type="text"),
            Button("Scan", id="scan-dir"),
            Label("", id="directory-size", classes="directory-size"),
            id="app-content",
            classes="app-content",
            
        )

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