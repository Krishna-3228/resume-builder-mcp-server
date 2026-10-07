from pathlib import Path
from fastmcp import FastMCP
import subprocess
from mcp.types import ToolAnnotations

mcp = FastMCP("Resume Builder")

RESOURCE_DIR = Path("resources")
TEMPLATE_DIR = Path("templates")
OUTPUT_DIR = Path("output")

def read_resource(filename: str) -> str:
    return (RESOURCE_DIR / filename).read_text()

def read_template(filename: str) -> str:
    return (TEMPLATE_DIR / filename).read_text()

# Resources
## 1. Profile
@mcp.resource("profile://personal-info")
def get_personal_info():
    return read_resource("personal-info.yaml")

@mcp.resource("profile://skills")
def get_skills():
    return read_resource("skills.yaml")


@mcp.resource("profile://projects")
def get_projects():
    return read_resource("projects.yaml")


@mcp.resource("profile://education")
def get_education():
    return read_resource("education.yaml")


@mcp.resource("profile://certifications")
def get_certifications():
    return read_resource("certifications.yaml")


@mcp.resource("profile://experience")
def get_experience():
    return read_resource("experience.yaml")

## 3. Templates
@mcp.resource("template://template-1")
def get_template_1():
    return read_template("template-1.tex")


@mcp.resource("template://template-2")
def get_template_2():
    return read_template("template-2.tex")

# -------------------------
# Resume Tools
# -------------------------

@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=True,
        open_world_hint=False,
    )
)
def write_resume(latex_content: str) -> str:
    """
    Write the generated LaTeX resume to output/resume.tex.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / "resume.tex"

    output_file.write_text(
        latex_content,
        encoding="utf-8"
    )

    return f"Resume written successfully to {output_file}"

@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    )
)
def compile_resume() -> str:
    """
    Compile output/resume.tex into output/resume.pdf using pdflatex.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tex_file = OUTPUT_DIR / "resume.tex"

    if not tex_file.exists():
        return "Compilation failed: output/resume.tex does not exist."

    try:
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                tex_file.name,
            ],
            cwd=OUTPUT_DIR,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            pdf_file = OUTPUT_DIR / "resume.pdf"

            return (
                f"Resume compiled successfully.\n"
                f"PDF: {pdf_file}"
            )

        return (
            "LaTeX compilation failed.\n\n"
            f"{result.stdout}\n\n"
            f"{result.stderr}"
        )

    except FileNotFoundError:
        return (
            "Compilation failed: pdflatex was not found. "
            "Make sure LaTeX is installed and pdflatex is available in PATH."
        )

@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    )
)
def read_resume() -> str:
    """
    Read the last generated resume LaTeX.
    """

    tex_file = OUTPUT_DIR / "resume.tex"

    if not tex_file.exists():
        return "No resume exists yet."

    return tex_file.read_text(encoding="utf-8")

if __name__ == "__main__":
    mcp.run()