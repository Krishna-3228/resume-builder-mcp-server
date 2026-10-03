# Resume Builder MCP Server

A local [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that allows an LLM such as Claude to build and iteratively modify a LaTeX resume using personal profile data and reusable LaTeX templates.

The project separates **reasoning** from **execution**:

- The LLM is responsible for understanding the job description, selecting relevant profile information, and generating/editing LaTeX.
- The MCP server provides access to profile data and templates.
- The MCP server also handles writing and compiling the generated LaTeX.
- LaTeX/PDF generation is performed locally using `pdflatex`.

The goal is to make resume creation an interactive workflow rather than manually editing a LaTeX resume for every job application.

---

## Features

- Store personal information in flexible YAML resources.
- Expose profile information to an MCP client as MCP resources.
- Store multiple LaTeX resume templates.
- Expose templates to the MCP client as MCP resources.
- Write generated LaTeX to a local file.
- Compile the LaTeX resume into a PDF.
- Read the current resume LaTeX for iterative editing.
- Work completely locally except for the LLM/MCP client being used.

---

# Architecture

The project follows a simple architecture:

```text
                       ┌─────────────────────┐
                       │     Claude / LLM    │
                       │                     │
                       │  - Understand JD    │
                       │  - Select profile   │
                       │  - Generate LaTeX   │
                       │  - Modify resume    │
                       └──────────┬──────────┘
                                  │
                     MCP Resources / Tools
                                  │
              ┌───────────────────┴───────────────────┐
              │                                       │
              ▼                                       ▼
      ┌─────────────────┐                    ┌─────────────────┐
      │ Profile Data    │                    │ LaTeX Templates │
      │                 │                    │                 │
      │ skills.yaml     │                    │ template-1.tex  │
      │ projects.yaml   │                    │ template-2.tex  │
      │ education.yaml  │                    │                 │
      │ etc.            │                    └─────────────────┘
      └─────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   MCP Server     │
                         │                  │
                         │ write_resume()   │
                         │ read_resume()    │
                         │ compile_resume() │
                         └────────┬─────────┘
                                  │
                                  ▼
                            output/resume.tex
                                  │
                                  │ pdflatex
                                  ▼
                            output/resume.pdf
```
---
# Design Philosophy
The project intentionally keeps the MCP server simple.
The LLM acts as the brain, while the MCP server acts as the execution layer.
For example, the MCP server does not need to understand:
- What skills are relevant to a particular job.
- Which projects should be selected.
- How a job description should be interpreted.
- How the resume should be rewritten.
Those are reasoning tasks handled by the LLM.
The MCP server instead provides the LLM with the information and operations it needs to perform those tasks.

---
# Project Structure
```text
resume-mcp/
│
├── resources/
│   ├── personal-info.yaml
│   ├── skills.yaml
│   ├── projects.yaml
│   ├── education.yaml
│   ├── certifications.yaml
│   └── experience.yaml
│
├── templates/
│   ├── template-1.tex
│   └── template-2.tex
│
├── output/
│   ├── resume.tex
│   ├── resume.pdf
│   ├── resume.log
│   └── resume.aux
│
├── src/
│   └── server.py
│
├── pyproject.toml
├── uv.lock
└── README.md
```

### `resources/`

Contains the user's personal profile information.
The files are YAML files, but the project does not enforce a particular schema.
For example:
```
skills:
  - C
  - C++
  - Python
  - Linux
  - Docker
```

or a much more complex structure can be used.
The LLM is responsible for interpreting the contents.
The resources currently exposed by the MCP server are:
```text
profile://persona-info
profile://skills
profile://projects
profile://education
profile://certifications
profile://experience
```
### `templates/`
Contains LaTeX resume templates.
Multiple templates can be stored here.
For example:
```text
templates/
├── template-1.tex
└── template-2.tex
```

They are exposed to the MCP client as:
```text
template://template-1
template://template-2
```
The templates define the visual structure and formatting of the resume.

### `output/`
Contains the currently generated resume and LaTeX compilation files.
```text
output/
├── resume.tex
├── resume.pdf
├── resume.log
└── resume.aux
```
`resume.tex` is the current generated LaTeX source.
`resume.pdf` is the compiled resume.
The `.log` and `.aux` files are generated by LaTeX.

### `src/server.py`
Contains the MCP server implementation.
It currently provides:
#### Resources
```text
profile://persona-info
profile://skills
profile://projects
profile://education
profile://certifications
profile://experience

template://template-1
template://template-2
```

#### Tools
```text
write_resume()
read_resume()
compile_resume()
```
## MCP Tools
### `write_resume()`
Writes LLM-generated LaTeX to: `output/resume.tex`

Conceptually:
```
Claude
  │
  │ LaTeX
  ▼
write_resume()
  │
  ▼
output/resume.tex
```

The tool does not generate or modify the LaTeX itself. It simply writes the content provided by the LLM.

### `read_resume()`
Reads the current: `output/resume.tex` and returns its contents to the LLM.
This allows iterative modifications.
For example:
```
User:
"Make the project descriptions shorter."

        ↓

Claude calls read_resume()

        ↓

Claude receives current LaTeX

        ↓

Claude modifies the LaTeX

        ↓

Claude calls write_resume()

        ↓

Claude calls compile_resume()
```

### `compile_resume()`
Compiles: `output/resume.tex` using:`pdflatex`and produces: `output/resume.pdf`

Compilation errors are returned to the LLM so that it can identify and fix LaTeX problems.

---
# Installation
Requirements
You need:
- Python
- uv
- LaTeX / pdflatex
- An MCP-compatible client such as Claude Desktop

## Step 1 : Install pdfLatex
### Windows
Install `MiKTeX` https://miktex.org/download and make sure its binaries are available in your system `PATH`.

Verify from PowerShell: 
```powershell
pdflatex --version
```

If pdflatex is not recognized, restart PowerShell after installing MiKTeX or add the MiKTeX bin directory to your PATH.

### Linux 
On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install texlive-latex-base texlive-latex-extra
```
Verify the installation: 
```bash
pdflatex --version
```

You should see the installed pdfTeX/TeX Live version.

### MacOS
Install MacTeX:
```zsh
brew install --cask mactex
```
After installation, restart your terminal.
Verify:
```zsh
pdflatex --version
```
If the command is not found, make sure the MacTeX binary directory is available in your `PATH`:
```zsh
export PATH="/Library/TeX/texbin:$PATH"
```

To make this permanent for zsh:
```zsh
echo 'export PATH="/Library/TeX/texbin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```
Verify again:
```zsh
pdflatex --version
```
> You may try to compile a sample .tex file to verify pdflatex works independently 

## Step 2 : Clone the repository
```bash
git clone https://github.com/Krishna-3228/resume-builder-mcp-server.git
cd resume-builder-mcp-server
```
## Step 3 : Create python virtual environment
### For Linux/macOS:
```bash
uv venv
source .venv/bin/activate

uv sync
```

### For Windows PowerShell:
```bash
uv venv
.venv\Scripts\Activate.ps1

uv sync
```

## Step 4 : Configure Claude Desktop

### Linux/macOS
Go:
`Claude Desktop ➞ Settings ➞ Developer ➞ Edit config`
Add the following configuration to the `claude_desktop_config.json`
```json
{
  "mcpServers": {
    "resume-builder": {
      "command": "/absolute/path/to/uv",
      "args": [
        "--directory",
        "/absolute/path/to/resume-mcp",
        "run",
        "python",
        "src/server.py"
      ]
    }
  }
}
```
Run: 
```
which uv
```
within the repo directory to get the path of `uv` and replace with `/absolute/path/to/uv`

Also replace `/absolute/path/to/resume-mcp`

### Windows
Go:
`Claude Desktop ➞ Settings ➞ Developer ➞ Edit config`
Add the following configuration to the `claude_desktop_config.json`
```json
{
  "mcpServers": {
    "resume-builder": {
      "command": "C:\\absolute\\path\\to\\uv",
      "args": [
        "--directory",
        "C:\\absolute\\path\\to\\resume-mcp",
        "run",
        "python",
        "src\\server.py"
      ]
    }
  }
}
```

Run: 
```
where uv
```
within the repo directory to get the path of `uv` and replace with `C:\\absolute\\path\\to\\uv`

Also replace `C:\\absolute\\path\\to\\resume-mcp"`

## Step 5 : Configure Your Profile

After completing the installation, you need to add your personal information
to the YAML files in the `resources/` directory.

These files act as the knowledge base that Claude uses when generating your
resume.

The project intentionally does not enforce a fixed YAML schema. You can
organize the information in a way that makes sense for your profile.
### Resource Files

Create/populate the following files:

```text
resources/
├── personal-info.yaml
├── skills.yaml
├── projects.yaml
├── education.yaml
├── certifications.yaml
└── experience.yaml
```
You can refer to the `.yaml.example` files for examples of how to
structure your profile information.
---
# Usage

Once the MCP server is connected to Claude, Claude can access the profile resources and resume templates.

A typical workflow looks like this:
```text
                    User
                     │
                     │ Job Description
                     ▼
                  Claude
                     │
             reads profile data
                     │
             reads template
                     │
             reasons about JD
                     │
             selects relevant
              information
                     │
             generates LaTeX
                     │
                     ▼
              write_resume()
                     │
                     ▼
                resume.tex
                     │
                     ▼
             compile_resume()
                     │
                     ▼
                resume.pdf
```
## Creating a Resume
Provide Claude with a job description and ask it to create a resume using one of the available templates.

```text
Create a resume for this job description.

Use the profile information available through the
resume-builder MCP server.

Use template-1.

Job Description:

[PASTE JOB DESCRIPTION HERE]
```
#### Claude can then:
1. Read the relevant profile resources.
2. Read the requested template.
3. Analyze the job description.
4. Select relevant experience, projects, and skills.
5. Generate LaTeX.
6. Call `write_resume()`.
7. Call `compile_resume()`.

The resulting files will be:
```text
output/
├── resume.tex
└── resume.pdf
```
### Iterative Editing
The main advantage of the system is that the resume can be modified through natural language.

This creates an iterative workflow:
```text
read
  ↓
modify
  ↓
write
  ↓
compile
  ↓
review
  ↓
repeat
```
---
# Why MCP?
Without MCP, the LLM can generate LaTeX but has no direct way to interact with the local resume files.

MCP provides a controlled interface between the LLM and the local environment.
```text
LLM
 │
 │ MCP
 ▼
Local Resume Environment
 │
 ├── Profile resources
 ├── Templates
 ├── resume.tex
 └── resume.pdf
```
This allows the LLM to reason about the resume while the local MCP server performs the actual file operations and compilation.

---
# License
This project is available under the license specified in the repository.