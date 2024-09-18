"""
# MarkTen / Spinner

Class for displaying multiple parallel spinners.
"""
from enum import Enum
import asyncio
import term  # type: ignore


SPIN_FRAMES = "|/-\\"
"""
Spin states to draw
"""
SPIN_FRAME_LENGTH = 0.25
"""
How often to redraw the spinners
"""


def get_frame(i: int) -> str:
    return SPIN_FRAMES[i % len(SPIN_FRAMES)]


class TaskStatus(Enum):
    Setup = 0
    Running = 1
    Success = 2
    Failure = 3


class SpinnerTask:
    def __init__(self, spinners: 'SpinnerManager', name: str) -> None:
        self.__spinners = spinners
        self.__status = TaskStatus.Setup
        self.__name = name
        self.__message: str | None = None

    def message(self, msg: str | None) -> None:
        self.__message = msg
        self.__spinners.draw_frame()

    def running(self, msg: str | None = None) -> None:
        self.__status = TaskStatus.Running
        self.message(msg)

    def succeed(self, msg: str | None = None) -> None:
        self.__status = TaskStatus.Success
        self.message(msg)

    def fail(self, msg: str | None = None) -> None:
        self.__status = TaskStatus.Failure
        self.message(msg)

    def is_resolved(self) -> bool:
        return self.__status in [TaskStatus.Success, TaskStatus.Failure]

    def display(self, i: int):
        msg = f" -- {self.__message}" if self.__message else ""
        match self.__status:
            case TaskStatus.Setup:
                print(f"⏳  {get_frame(i)} {self.__name} {msg}")
            case TaskStatus.Running:
                print(f"⏱️  {get_frame(i)} {self.__name} {msg}")
            case TaskStatus.Success:
                print(f"✅   {self.__name} {msg}")
            case TaskStatus.Failure:
                print(f"❌   {self.__name} {msg}")


class SpinnerManager:
    def __init__(self, name: str) -> None:
        self.__name = name
        """Name of spinner"""
        self.__task_list: list[SpinnerTask] = []
        """List of tasks, as they appear while rendering"""
        self.__task_mapping: dict[int, SpinnerTask] = {}
        """Mapping of tasks, so that we can update them given an object"""
        # Save the cursor position
        term.saveCursor()

    def create_task(self, owner: object, name: str) -> SpinnerTask:
        """
        Create a task to be displayed by the spinner
        """
        task = SpinnerTask(self, name)
        self.__task_list.append(task)
        self.__task_mapping[id(owner)] = task
        self.__frame = 0
        return task

    def __count_complete(self) -> int:
        """Returns the number of completed tasks"""
        return len(list(filter(
            lambda task: task.is_resolved(),
            self.__task_list
        )))

    async def spin(self) -> None:
        """
        Begin the spin task
        """
        # Move the cursor to the starting position
        while True:
            self.__frame += 1
            self.draw_frame()
            # Wait for the frame duration
            await asyncio.sleep(SPIN_FRAME_LENGTH)

    def draw_frame(self):
        term.restoreCursor()
        completed_tasks = self.__count_complete()
        print(f"{self.__name} ({completed_tasks}/{len(self.__task_list)})")
        # Draw the spinners
        for task in self.__task_list:
            term.clearLine()
            task.display(self.__frame)
