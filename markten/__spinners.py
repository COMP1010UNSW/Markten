"""
# MarkTen / Spinner

Class for displaying multiple parallel spinners.

This is used to report the progress of tasks that run simultaneously.
"""

import asyncio
from enum import Enum

from rich.console import Group, RenderableType
from rich.live import Live
from rich.panel import Panel

SPIN_FRAMES = "|/-\\"
"""
Spin states to draw
"""
SPIN_FRAME_LENGTH = 0.25
"""
How often to redraw the spinners
"""


def get_frame(i: int) -> str:
    """Returns frame number for spinner animation"""
    return SPIN_FRAMES[i % len(SPIN_FRAMES)]


class TaskStatus(Enum):
    """Status of a task"""

    Setup = 0
    """Task is being set up"""
    Running = 1
    """Task is running"""
    Success = 2
    """Task resolved successfully"""
    Failure = 3
    """Task resolved, but failed"""


class SpinnerTask:
    """
    A single task that is associated with a spinner.
    """

    def __init__(self, spinners: "SpinnerManager", name: str) -> None:
        """
        Create a spinner task.

        This should only be called by the `SpinnerManager`, which gives a
        reference to `self`. Use `spinners.create_task(task_name)` instead.

        Args:
            spinners (SpinnerManager): spinner manager
            name (str): name of the task
        """
        self.__spinners = spinners
        self.__status = TaskStatus.Setup
        self.__name = name
        self.__message: str | None = None
        self.__logs: list[str] = []

    def log(self, line: str) -> None:
        """
        Add message to the task logs.
        """
        self.__logs.append(line.strip())
        self.__spinners.draw_frame()

    def message(self, msg: str | None) -> None:
        """
        Set the overall status message of the task.
        """
        self.__message = msg
        self.__spinners.draw_frame()

    def running(self, msg: str | None = None) -> None:
        """
        Set the task status as `Running`
        """
        self.__status = TaskStatus.Running
        self.message(msg)

    def succeed(self, msg: str | None = None) -> None:
        """
        Set the task status as `Success`
        """
        self.__status = TaskStatus.Success
        self.message(msg)

    def fail(self, msg: str | None = None) -> None:
        """
        Set the task status as `Failure`
        """
        self.__status = TaskStatus.Failure
        self.message(msg)

    def is_resolved(self) -> bool:
        """
        Returns whether the task has resolved, meaning it finished
        successfully, or that it failed.
        """
        return self.__status in [TaskStatus.Success, TaskStatus.Failure]

    def display(self, i: int) -> RenderableType:
        """
        Return the lines used to display the spinner's state.
        """
        title: str
        style: str
        msg = f" -- {self.__message}" if self.__message else ""
        logs = self.__logs[-10:]
        match self.__status:
            case TaskStatus.Setup:
                title = f"⏳  {get_frame(i)} {self.__name}{msg}"
                style = "yellow"
            case TaskStatus.Running:
                title = f"⏱️  {get_frame(i)} {self.__name}{msg}"
                style = "cyan"
            case TaskStatus.Success:
                title = f"✅   {self.__name}{msg}"
                style = "green"
            case TaskStatus.Failure:
                title = f"❌   {self.__name}{msg}"
                style = "red"
                # Show full logs
                logs = self.__logs
        return Panel(
            "\n".join(logs).strip(),
            title=title,
            style=style,
        )


class SpinnerManager:
    """
    A manager for running spinners.

    Only one spinner manager should be running at once.

    Usage:

        spinners = SpinnerManager("Some complex task")
        task1 = spinners.create_task("One parallel action")
        task2 = spinners.create_task("Another action")
        spinner_task = asyncio.create_task(spinners.spin())

        # Do work...

        spinner_task.cancel()
    """

    def __init__(self, name: str, live: Live) -> None:
        """
        Create a spinner manager.

        Args:
            name (str): name of spinner manager (name of step being executed)
        """
        self.__name = name
        """Name of spinner"""
        self.__task_list: list[SpinnerTask] = []
        """List of tasks, as they appear while rendering"""
        self.__live = live
        """Rich live output"""
        self.__frame = 0
        """Frame number, updated while spinning"""

    def create_task(self, name: str) -> SpinnerTask:
        """
        Create a task to be displayed by the spinner.

        Args:
            name (str): name of the task being executed within the step.
        """
        task = SpinnerTask(self, name)
        self.__task_list.append(task)
        return task

    def __count_complete(self) -> int:
        """Returns the number of completed tasks"""
        return len(
            list(filter(lambda task: task.is_resolved(), self.__task_list))
        )

    async def spin(self) -> None:
        """
        Begin the spin task.

        This will run infinitely, until the task is cancelled.
        """
        # Move the cursor to the starting position
        while True:
            self.__frame += 1
            self.draw_frame()
            # Wait for the frame duration
            await asyncio.sleep(SPIN_FRAME_LENGTH)

    def draw_frame(self):
        """
        Draw a frame of the spinners.

        This currently redraws all output, which isn't especially efficient.

        Most of the commented code relies on getting and setting the terminal
        cursor position manually, which appears to break when the number of
        lines in the terminal is too small (causing text to be printed multiple
        times).

        Since it's impossible to jump to a negative cursor position manually,
        we rely on the save/restore cursor functionality, since at least it
        only massively breaks if the terminal size is extremely tiny, and works
        reasonably well otherwise.

        I need to find a library that handles all of the terminal outputting so
        I can get nice outputs that update in multiple places without causing
        major headaches and console spamming, but that is a future Maddy
        problem.
        """
        completed_tasks = self.__count_complete()

        title = f"{self.__name} ({completed_tasks}/{len(self.__task_list)})"

        # Draw the spinners
        tasks: list[RenderableType] = []
        for task in self.__task_list:
            tasks.append(task.display(self.__frame))

        panel = Panel(Group(*tasks), title=title)
        self.__live.update(panel)
