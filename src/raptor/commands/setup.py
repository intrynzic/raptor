from raptor.config.loader import CONFIG
from raptor.core.log import info
from raptor.setup import dotnet, doxygen, git, hooks, vulkan
import typer


app = typer.Typer(help = "Setup the development environment and all project dependencies.")

@app.command(name = "all", help = "Setup everything required for development.")
def all():
    info("Setting-up repository and development environment...")

    if CONFIG.setup.git:
        setup_git(False)

    if CONFIG.setup.git_hooks:
        setup_hooks()

    if CONFIG.setup.vulkan:
        setup_vulkan(False)

    if CONFIG.setup.dotnet:
        setup_dotnet(False)

    if CONFIG.setup.doxygen:
        setup_doxygen(False)

    info("Setup complete.")
    info("You may want to run \"raptor doctor diagnose\" to ensure your development environment is correctly setup.")

if CONFIG.setup.git:
    @app.command(name = "git", help = "Setup Git for Windows.")
    def setup_git(
        download_installer: bool = typer.Option(False, "--download-installer", help = "Download the Git installer and do nothing else.")
    ):
        if download_installer:
            git.download_installer()
            return

        info("Setting-up Git...")
        git.ensure()

if CONFIG.setup.git_hooks:
    @app.command(name = "hooks", help = "Setup Git hooks.")
    def setup_hooks():
        info("Setting-up Git hooks...")
        hooks.ensure()

if CONFIG.setup.vulkan:
    @app.command(name = "vulkan", help = "Setup the Vulkan SDK.")
    def setup_vulkan(
        download_installer: bool = typer.Option(False, "--download-installer", help = "Download the Vulkan SDK installer and do nothing else.")
    ):
        if download_installer:
            vulkan.download_installer()
            return

        info("Setting-up Vulkan...")
        vulkan.ensure()

if CONFIG.setup.dotnet:
    @app.command(name = "dotnet", help = "Setup the .NET SDK.")
    def setup_dotnet(
        download_installer: bool = typer.Option(False, "--download-installer", help = "Download the .NET SDK installer and do nothing else.")
    ):
        if download_installer:
            dotnet.download_installer()
            return

        info("Setting-up .NET...")
        dotnet.ensure()

if CONFIG.setup.doxygen:
    @app.command(name = "doxygen", help = "Setup Doxygen.")
    def setup_doxygen(
        download_archive: bool = typer.Option(False, "--download-archive", help = "Download the Doxygen release archive and do nothing else.")
    ):
        if download_archive:
            doxygen.download_archive()
            return

        info("Setting-up Doxygen...")
        doxygen.ensure()
