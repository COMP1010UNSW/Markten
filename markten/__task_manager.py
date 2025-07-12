"""
# Markten / Task Manager

The context for a task, allowing it to update its state, log progress, and
create subtasks.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """Status of a task"""

    Running = 1
    """Task is running"""
    Success = 2
    """Task resolved successfully"""
    Failure = 3
    """Task resolved, but failed"""


@dataclass
class TaskInfo:
    name: str
    status: TaskStatus
    progress: float | None
    children: list['TaskInfo']
    output: list[str]


class TaskManager:

    def __init__(
        self,
        name: str | object,
        redraw: Callable[[], None],
    ) -> None:
        """Create a TaskManager object.

        You shouldn't call this directly unless you intend to display the data
        yourself. Instead, you should create a child of an existing task
        using `task.make_child` so that that task's output is drawn nicely.

        Parameters
        ----------
        name : str | object
            Name of this task. If an object is given, its name will be used (if
            it is a function or class).
        redraw : Callable[[], None]
            Redraw callback function. This gets called whenever the output
            should be redrawn.
        """
        self.__redraw = redraw

        self.__name = name if isinstance(name, str) else str(name)
        # TODO: Get pretty name of object

        self.__status = TaskStatus.Running
        """Status as enum"""
        self.__message: str | None = None
        """Status message"""
        self.__output: list[str] = []
        """Overall logs"""
        self.__progress: float | None = None
        """Progress percentage (float from 0 to 1)"""

        self.__children: list[TaskManager] = []
        """Child tasks"""

    def make_child(self, name: str | object) -> 'TaskManager':
        """Create a child task of this task

        Used to indicate when a sub-task is required for the completion of this
        task.

        Parameters
        ----------
        name : str | object
            Name of the child task. If an object is given, its name will be
            used (if it is a function or class).

        Returns
        -------
        TaskManager
            Child task
        """
        child = TaskManager(name, self.__redraw)
        self.__children.append(child)
        return child

    def log(self, line: str) -> None:
        """
        Add message to the task's output log.

        This is used for detailed output, such as the stdout of a child
        process or debugging info.
        """
        self.__output.append(line.strip())
        self.__redraw()

    def progress(self, progress: float | None) -> None:
        """
        Set the progress percentage of the task.

        If set to `None`, indicates progress is not being measured (a spinner
        will be shown rather than a progress bar).
        """

    def message(self, msg: str | None) -> None:
        """
        Set the overall status message of the task.

        If set, this is always displayed alongside the task's name.

        If `None`, no message is shown, and the previous message is discarded.
        """
        self.__message = msg
        self.__redraw()

    def running(self, msg: str | None = None) -> None:
        """
        Set the task status as `Running`.

        Optionally, a status message can be provided.
        """
        self.__status = TaskStatus.Running
        self.message(msg)

    def succeed(self, msg: str | None = None) -> None:
        """
        Set the task status as `Success`.

        Optionally, a status message can be provided.
        """
        self.__status = TaskStatus.Success
        self.message(msg)

    def fail(self, msg: str | None = None) -> None:
        """
        Set the task status as `Failure`.

        Optionally, a status message can be provided.
        """
        self.__status = TaskStatus.Failure
        self.message(msg)

    def is_resolved(self) -> bool:
        """
        Returns whether the task has resolved, meaning it finished
        successfully, or that it failed.
        """
        return self.__status in [TaskStatus.Success, TaskStatus.Failure]

    def display(self) -> TaskInfo:
        """
        Return info about this item in a format which can be displayed easily.
        """
        return TaskInfo(
            self.__name,
            self.__status,
            self.__progress,
            [child.display() for child in self.__children],
            self.__output,
        )
