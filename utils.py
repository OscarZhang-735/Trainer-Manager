"""Compatibility imports for the original utility API."""

PROGRAM_NAME = "Rinne Toolkit"

from trainer_manager.services.data import Data
from trainer_manager.services.downloads import Download
from trainer_manager.services.files import File
from trainer_manager.services.help import Help
from trainer_manager.services.fonts import Font

__all__ = ["PROGRAM_NAME", "Data", "Download", "File", "Help", "Font"]
