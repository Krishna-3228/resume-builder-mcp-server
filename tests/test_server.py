from pathlib import Path

import pytest

import server


@pytest.fixture
def test_output_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "OUTPUT_DIR", tmp_path)
    return tmp_path


def test_write_resume(test_output_dir):
    latex = r"""
    \documentclass{article}
    \begin{document}
    Test Resume
    \end{document}
    """

    result = server.write_resume(latex)

    resume_file = test_output_dir / "resume.tex"

    assert resume_file.exists()
    assert resume_file.read_text(encoding="utf-8") == latex
    assert "successfully" in result.lower()


def test_read_resume(test_output_dir):
    latex = "test resume content"

    resume_file = test_output_dir / "resume.tex"
    resume_file.write_text(latex, encoding="utf-8")

    result = server.read_resume()

    assert result == latex


def test_read_resume_when_file_does_not_exist(test_output_dir):
    result = server.read_resume()

    assert result == "No resume exists yet."


def test_compile_resume(test_output_dir):
    latex = r"""
    \documentclass{article}

    \begin{document}

    Test Resume

    \end{document}
    """

    resume_file = test_output_dir / "resume.tex"
    resume_file.write_text(latex, encoding="utf-8")

    result = server.compile_resume()

    pdf_file = test_output_dir / "resume.pdf"

    assert pdf_file.exists()
    assert "compiled successfully" in result.lower()