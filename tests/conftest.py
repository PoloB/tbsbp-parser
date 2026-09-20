"""Configuration of tests."""

import os
from pathlib import Path

SAMPLE_DIRECTORY = Path(os.path.realpath(__file__)).parent / "samples"

TESTED_FILES = (
    "empty_project.sboard",
    "test_01.sboard",
    "test_02.sboard",
    "test_03.sboard",
    "test_04.sboard",
    "sequence.sboard",
    "test3d.sboard",
    "track.sboard",
)
