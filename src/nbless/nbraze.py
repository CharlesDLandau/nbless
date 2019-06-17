# !/usr/bin/env python
from typing import Dict
from pathlib import Path

import nbformat


def nbraze(in_file: str, extension: str = "py") -> Dict[str, str]:
    """Create markdown and code files from a Jupyter notebook.

    :param in_file: The name of the input Jupyter notebook file.
    :param extension: The extension for code files.
    """
    nb = nbformat.read(in_file, as_version=4)
    if not extension and nb.metadata.language_info.name:
        lang_ext_dict = {
            "R": ".R",
            "python": ".py",
            "javascript": ".js",
            "ruby": ".rb",
            "julia": ".jl",
            "octave": ".m",
            "go": ".go",
        }
        if nb.metadata.language_info.name in lang_ext_dict:
            extension = lang_ext_dict[nb.metadata.language_info.name]
    filenames = (
        f"{Path(in_file).stem}_cell{n}.md"
        if cell.cell_type == "markdown"
        else f"{Path(in_file).stem}_cell{n}.{extension}"
        for n, cell in enumerate(nb.cells)
    )
    sources = (cell.source for cell in nb.cells)
    return dict(zip(filenames, sources))
