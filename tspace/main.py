"""
Simple TUI app to show how much space a folder takes.
"""
from .scan import getFolderSpace
from textual.app import App, ComposeResult
from textual.widgets import Label
from textual.containers import VerticalScroll, Horizontal, Vertical
from textual.widgets import Header, Static, Button, Input, Footer
import os
from humanize import naturalsize
import asyncio
from threading import Event
from concurrent.futures import CancelledError
import contextlib
from pathlib import Path

class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("tSpace")
        yield Button("space")
        yield Button("clean")


class AppContent(VerticalScroll):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._scan_task: asyncio.Task | None = None
        self._cancel_event: Event | None = None

    async def _start_scan(self) -> None:
        if self._scan_task and not self._scan_task.done():
            return

        dir_input = self.query_one("#dir-input", Input)
        label = self.query_one("#directory-size", Label)
        scan_btn = self.query_one("#scan-dir", Button)
        cancel_btn = self.query_one("#cancel-scan", Button)

        to_search_dir = (dir_input.value or "").strip()
        if not to_search_dir or not os.path.isdir(os.path.expanduser(to_search_dir)):
            label.update("Directory doesn't exist")
            return

        scan_btn.disabled = True
        cancel_btn.disabled = False
        label.update("Scanning...")
        
        self._cancel_event = Event()

        async def animate(task: asyncio.Task):
            progress = ""
            while not task.done():
                progress += "#"
                if len(progress) >= 10:
                    progress = ""
                label.update(progress or "#")
                await asyncio.sleep(0.1)

        async def run_scan():
            try:
                work_task = asyncio.create_task(
                    asyncio.to_thread(
                        getFolderSpace,
                        to_search_dir,
                        cancel_event=self._cancel_event
                    )
                )
                anim_task = asyncio.create_task(animate(work_task))
                size = await work_task
                anim_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await anim_task
                label.update(naturalsize(size) if size >= 0 else "Error")
            except Exception as e:
                label.update(f"Error: {e}")
            finally:
                scan_btn.disabled = False
                cancel_btn.disabled = True
                self._scan_task = None
                self._cancel_event = None

        self._scan_task = asyncio.create_task(run_scan())

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        await self._start_scan()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "scan-dir":
            await self._start_scan()
        elif event.button.id == "cancel-scan":
            if not self._scan_task or self._scan_task.done():
                return
            if self._cancel_event:
                self._cancel_event.set()
            label = self.query_one("#directory-size", Label)
            label.update("Stopping...")
            await asyncio.sleep(1)
            label.update("Stopped")
            await asyncio.sleep(1)
            label.update("")
        elif event.button.id == "exit":
            self.app.exit()

    def compose(self) -> ComposeResult:
        yield Vertical(
            Input(placeholder="Directory", id="dir-input", classes="dir-input"),
            Vertical(
                Label("", id="directory-size", classes="directory-size"),
                Horizontal(
                    Button("Scan", id="scan-dir", classes="scan-dir", disabled=False),
                    Button("Cancel", id="cancel-scan", classes="cancel-scan", disabled=True),
                    Button("Exit", id="exit", classes="exit"),
                    classes="scan-dir-div",
                    id="scan-dir-div"
                ),
                id="scan-dir-vert",
                classes="scan-dir-vert"
            ),
            id="app-content",
            classes="app-content",
        )

class tSpace(App):
    CSS_PATH = Path(__file__).with_name("styles") / "app.tcss"
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="tS", id="header", time_format="%H:%M:%S")
        yield Horizontal(
            # Sidebar(id="sidebar", classes="sidebar"),
            AppContent(id="app-content"),
        )
        yield Footer(id="footer", show_command_palette=False, classes="footer")

def main() -> None:
    """Console-script entrypoint to run the app."""
    app = tSpace()
    app.run()


if __name__ == "__main__":
    main()