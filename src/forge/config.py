"""Paths. Override with FORGE_COURSES / FORGE_WORK / FORGE_DATA."""

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COURSES_DIR = Path(os.environ.get("FORGE_COURSES", REPO / "courses"))
WORK_DIR = Path(os.environ.get("FORGE_WORK", Path.home() / "forge-work"))
DATA_DIR = Path(os.environ.get("FORGE_DATA", Path.home() / ".local/share/forge"))
