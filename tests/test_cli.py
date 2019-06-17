from pathlib import Path

import nbformat
from click.testing import CliRunner

from cli import (
    nbless_cli,
    nbuild_cli,
    nbexec_cli,
    nbconv_cli,
    nbraze_cli,
    nbdeck_cli
)
from tests.make_temp import make_tempfiles, make_temp_notebook


def test_nbless_cli(tmp_path: Path) -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        files = make_tempfiles(tmp_path)
        result = runner.invoke(nbless_cli.nbless_cli, files)
        cells = nbformat.reads(result.output, as_version=4).cells
        assert result.exit_code == 0
        assert [c.cell_type for c in cells] == ["markdown", "code", "markdown"]
        for cell, tempfile in zip(cells, files):
            assert cell.source == Path(tempfile).read_text()


def test_nbuild_cli(tmp_path: Path) -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        files = make_tempfiles(tmp_path)
        result = runner.invoke(nbuild_cli.nbuild_cli, files)
        cells = nbformat.reads(result.output, as_version=4).cells
        assert result.exit_code == 0
        assert [c.cell_type for c in cells] == ["markdown", "code", "markdown"]
        for cell, tempfile in zip(cells, files):
            assert cell.source == Path(tempfile).read_text()


def test_nbexec_cli(tmp_path: Path) -> None:
    """Run nbexec() to execute a temporary notebook file."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        nb = make_temp_notebook(tmp_path)
        result = runner.invoke(nbexec_cli.nbexec_cli, nb)
        cells = nbformat.reads(result.output, as_version=4).cells
        for cell in cells:
            if cell.cell_type == "code":
                assert cell.execution_count
                for output in cell.outputs:
                    assert output


def test_nbconv_cli(tmp_path: Path) -> None:
    """Convert ``tempfiles`` with each exporter in ``exporters``."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        nb = make_temp_notebook(tmp_path)
        runner.invoke(nbconv_cli.nbconv_cli, [nb, '-e', 'html'])
        assert Path('notebook.html').read_text().startswith('<!DOCTYPE html>\n')
        runner.invoke(nbconv_cli.nbconv_cli, [nb, '-o', 'report.html'])
        assert Path('report.html').read_text().startswith('<!DOCTYPE html>\n')
        runner.invoke(nbconv_cli.nbconv_cli, [nb, '-o', 'report.adoc'])
        assert Path('report.adoc').read_text().startswith('\n[[background]]')


def test_nbraze_cli(tmp_path: Path):
    """Extract code and markdown files from the cells of an input notebook."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(nbraze_cli.nbraze_cli, make_temp_notebook(tmp_path))
        assert Path("notebook_cell0.md").read_text().startswith("# Background")
        assert Path("notebook_cell1.py").read_text().startswith("import numpy")
        assert Path("notebook_cell2.md").read_text().startswith("# Discussion")


def test_nbdeck_cli(tmp_path: Path):
    """ Set up a Jupyter notebook to be viewed as or converted into slides."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        nb = make_temp_notebook(tmp_path)
        result = runner.invoke(nbdeck_cli.nbdeck_cli, nb)
        cells = nbformat.reads(result.output, as_version=4).cells
        c = 0
        for cell in cells:
            if cell.cell_type == "markdown" and cell.source.startswith("#"):
                c += 1
                assert cell.metadata.slideshow == {"slide_type": "slide"}
        assert c == 2
        assert len(cells) == 3
