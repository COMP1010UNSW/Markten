"""
# Markten / Actions / editor.py

Actions for launching text editors
"""

from .__interface import TextEditorAction
from .__pulsar import pulsar
from .__vs_code import vs_code, vs_codium
from .__zed import zed

__all__ = [
    "TextEditorAction",
    "pulsar",
    "vs_code",
    "vs_codium",
    "zed",
]
