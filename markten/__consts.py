"""
# Markten / consts
"""

from importlib.metadata import version

VERSION = version("markten")
"""
MarkTen version, determined using importlib metadata (so that I don't need to
constantly remember to update it).
"""


TIME_PER_CLI_FRAME = 0.03
"""10 FPS"""
