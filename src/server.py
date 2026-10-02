from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("Resume Builder")

RESOURCE_DIR = Path("resources")
TEMPLATE_DIR = Path("templates")

def read_resource(filename: str) -> str:
    return (RESOURCE_DIR / filename).read_text()

def read_template(filename: str) -> str:
    return (TEMPLATE_DIR / filename).read_text()

# Resources
## 1. Profile
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


if __name__ == "__main__":
    mcp.run()