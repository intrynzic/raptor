# Raptor

*"**The workflow orchestrator for modern C++ repositories.**"*

---


[![PyPI version](https://img.shields.io/pypi/v/intrynzic-raptor.svg?logo=python&logoColor=white&label=PyPI)](https://pypi.org/project/intrynzic-raptor/)

## Overview

Modern C++ projects shouldn't require pages of setup docs, fragile scripts, or tribal knowledge just to get building.

**Raptor makes the repository the source of truth.** It defines how a C++ (or other) repository is prepared, validated, generated, built, and maintained—ensuring every developer machine and CI runner follows the exact same workflow.

Instead of forcing developers to manually configure their machines, Raptor forces the machine to conform to the repository.

### What Raptor Handles

- **Environment Prep:** Machine setup, tool verification, and SDK validation.
- **Build Lifecycle:** Workspace generation, building, and output cleaning.
- **Developer Tools:** Git Hooks, meta-build systems and custom workflows.
- **Troubleshooting:** Raptor can automate troubleshooting and diagnostics using `raptor doctor`.

---

## Philosophy

Most C++ developer tooling is **machine-centric**: *"Install these SDKs, set these environment variables, run these custom scripts, and pray it works."*

Raptor is **repository-centric**.

A repository should completely describe its own development environment. The orchestrator reads that specification and enforces consistency across all environments.

* **One Contract:** The repository defines the requirements.
* **One Workflow:** Developers and CI runners execute the exact same steps.
* **Zero Friction:** Clone, run Raptor, start coding.

---

## Quick Start

### Installation

Install Raptor via PyPI:

``` bash
pip install intrynzic-raptor
```

### Usage

``` text
 Usage: raptor [OPTIONS] COMMAND [ARGS]...

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --version                     Show the version and exit.                                                                                                               │
│ --install-completion          Install completion for the current shell.                                                                                                │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                                                         │
│ --help                        Show this message and exit.                                                                                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ build     Build the project.                                                                                                                                           │
│ clean     Clean the workspace's configured clean targets.                                                                                                              │
│ doctor    Diagnose and fix issues with the repository and your development environment.                                                                                │
│ hook      Run Git hooks.                                                                                                                                               │
│ premake   Generate project files using premake.                                                                                                                        │
│ rebuild   Rebuild the project.                                                                                                                                         │
│ run       Build and run an executable project or run raptor tasks.                                                                                                     │
│ setup     Setup the development environment and all project dependencies.                                                                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

---

## License

Raptor is licensed under the MIT License, see [LICENSE](LICENSE):

``` text
MIT License

Copyright (c) 2026 Intrynzic Software

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
