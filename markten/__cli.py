"""
# MarkTen / Spinner

Class for displaying multiple parallel spinners.

This is used to report the progress of tasks that run simultaneously.
"""

from rich.columns import Columns
from rich.console import Group, RenderableType
from rich.padding import Padding
from rich.spinner import Spinner
from rich.text import Text

from markten.__action_session import ActionInfo, ActionStatus

INDENT_MULTIPLIER = 2

PARTIAL_OUTPUT_LINES = 10


def action_status(action: ActionInfo) -> RenderableType:
    if action.status == ActionStatus.Running:
        return Spinner("dots")
    elif action.status == ActionStatus.Failure:
        return Text("❌")
    else:  # ActionStatus.Success
        return Text("✅")


def action_title(action: ActionInfo) -> RenderableType:
    if action.status == ActionStatus.Running:
        return Text(f"[cyan]{action.name}[/]")
    elif action.status == ActionStatus.Failure:
        return Text(f"[red]{action.name}[/]")
    else:  # ActionStatus.Success
        return Text(f"[green]{action.name}[/]")


def draw_action_brief(action: ActionInfo) -> RenderableType:
    return Columns(
        [
            action_status(action),
            " - ",
            action_title(action),
            *((" - ", action.message) if action.message else ()),
        ]
    )


def draw_action_partial(action: ActionInfo) -> RenderableType:
    header = draw_action_brief(action)
    latest_logs = "\n".join(action.output[-PARTIAL_OUTPUT_LINES:])

    # Brief overview of child actions
    children = [
        Padding.indent(draw_action_brief(child), INDENT_MULTIPLIER)
        for child in action.children
    ]

    return Group(
        header,
        Padding.indent(latest_logs, INDENT_MULTIPLIER),
        *children,
    )



def draw_action_full(action: ActionInfo) -> RenderableType:
    header = draw_action_brief(action)
    latest_logs = "\n".join(action.output)

    # Brief overview of child actions
    children = [
        Padding.indent(draw_action_full(child), INDENT_MULTIPLIER)
        for child in action.children
    ]

    return Group(
        header,
        Padding.indent(latest_logs, INDENT_MULTIPLIER),
        *children,
    )


def draw_action(action: ActionInfo) -> RenderableType:
    if action.status == ActionStatus.Failure:
        return draw_action_full(action)
    else:
        return draw_action_partial(action)
