from pathlib import Path
from typing import Union

File = Union[Path, str]


def create_folder(folder: Path):
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)

