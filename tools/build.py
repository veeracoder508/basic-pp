import subprocess
import sys
import logging
from pathlib import Path
from typing import List, Tuple
from rich.logging import RichHandler

# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=True)]
)
logger = logging.getLogger("build_script")

# Try to import the built-in tomllib (Python 3.11+), fallback to tomli
try:
    import tomllib
except ImportError:
    logger.warning("python version is low, trying tomli...")
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


# ---------------------------------------------------------
# Classes
# ---------------------------------------------------------
class CommandRunner:
    """Utility class to run shell commands."""
    
    @staticmethod
    def run(command: List[str], task_name: str) -> str:
        """Executes a subprocess command and returns the output."""
        logger.info(f"Starting task: {task_name}")
        try:
            result = subprocess.run(
                command, 
                check=True, 
                text=True, 
                capture_output=True
            )
            logger.info(f"Successfully completed: {task_name}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Task failed: {task_name}")
            logger.error(f"Error output: {e.stderr}")
            sys.exit(1)


class ProjectConfigReader:
    """Reads project configuration from pyproject.toml."""
    
    def __init__(self, filepath: str = "pyproject.toml"):
        self.filepath = Path(filepath)

    def get_project_details(self) -> Tuple[str, str]:
        """Extracts the package name and version from pyproject.toml."""
        if not self.filepath.exists():
            logger.error(f"Configuration file not found: {self.filepath}")
            sys.exit(1)
            
        if tomllib is None:
            logger.error("Python 3.11+ (tomllib) or the 'tomli' package is required to parse pyproject.toml.")
            sys.exit(1)

        try:
            with open(self.filepath, "rb") as f:
                data = tomllib.load(f)
            
            # Standard PEP 621 pyproject.toml structure
            project_data = data.get("project", {})
            
            # Fallback for tools like Poetry which use [tool.poetry]
            if not project_data:
                project_data = data.get("tool", {}).get("poetry", {})

            name = project_data.get("name")
            version = project_data.get("version")

            if not name or not version:
                logger.error("Could not find 'name' or 'version' in pyproject.toml.")
                sys.exit(1)

            # Ensure module name is safe for python imports (replace hyphens with underscores)
            module_name = name.replace("-", "_")
            
            logger.info(f"Auto-detected project: {name} (module: {module_name}), version: {version}")
            return module_name, version

        except Exception as e:
            logger.error(f"Failed to read pyproject.toml: {e}")
            sys.exit(1)


class DocsBuilder:
    """Handles the generation of API and User documentation."""
    
    def __init__(self, module_name: str, pdoc_output_dir: str = "docs/api"):
        self.module_name = module_name
        self.pdoc_output_dir = pdoc_output_dir

    def build_api_docs(self):
        """Generates API documentation using pdoc3."""
        # Dynamically find the source directory matching the module name,
        # falling back safely to 'src/basicpp' if the folder doesn't use underscores.
        module_path = f"src/{self.module_name}"
        if not Path(module_path).exists() and Path("src/basicpp").exists():
            module_path = "src/basicpp"

        # Explicitly invoking via sys.executable avoids environment PATH hijacking
        command = [
            sys.executable,
            "-m",
            "pdoc",
            "--html",
            "--output-dir", self.pdoc_output_dir,
            "--force", 
            module_path
        ]
        CommandRunner.run(command, "Build API Docs (pdoc3)")

    def build_user_docs(self):
        """Generates user documentation using Zensical if `docs.yml` is not found in .github/workflows."""
        if not Path(".github/workflows/docs.yml").exists():
            command = ["zensical", "build"]
            CommandRunner.run(command, "Build User Docs (Zensical)")
        else:
            logger.info("github workflow is found for zensical, skipping build.")


class ChangelogGenerator:
    """Handles the generation of the changelog."""
    
    def __init__(self, output_file: str = "CHANGELOG.md"):
        self.output_file = output_file

    def generate(self, version: str):
        """Generates a changelog from git commit history."""
        try:
            latest_tag = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"], 
                capture_output=True, text=True, check=True
            ).stdout.strip()
            revision_range = f"{latest_tag}..HEAD"
        except subprocess.CalledProcessError:
            revision_range = "HEAD"

        command = ["git", "log", revision_range, "--oneline"]
        commits = CommandRunner.run(command, f"Fetch Git Commits for {version}")

        # Ensure the documentation directory exists before appending files
        Path("docs").mkdir(parents=True, exist_ok=True)

        with open(self.output_file, "a") as f:
            f.write(f"\n## Version {version}\n\n")
            if commits.strip():
                for line in commits.splitlines():
                    f.write(f"* {line}\n")
            else:
                f.write("* No significant changes or first release.\n")

        with open("docs/changelog.md", "a") as f:
            f.write(f"\n## Version {version}\n\n")
            if commits.strip():
                for line in commits.splitlines():
                    f.write(f"* {line}\n")
            else:
                f.write("* No significant changes or first release.\n")
                
        logger.info(f"Changelog updated for version {version} in {self.output_file}")


class GitReleaser:
    """Handles Git tagging and releasing."""
    
    def release(self, version: str):
        """Creates a git tag and pushes it to origin."""
        tag_command = ["git", "tag", "-a", f"v{version}", "-m", f"Release version {version}"]
        CommandRunner.run(tag_command, f"Create Git Tag v{version}")
        
        push_command = ["git", "push", "origin", f"v{version}"]
        CommandRunner.run(push_command, f"Push Git Tag v{version} to Origin")


class BuildOrchestrator:
    """Coordinates the entire build and release process."""
    
    def __init__(self, module_name: str, version: str):
        self.version = version
        self.docs_builder = DocsBuilder(module_name=module_name)
        self.changelog_generator = ChangelogGenerator()
        self.git_releaser = GitReleaser()

    def run_all(self):
        """Executes all build steps sequentially."""
        logger.info(f"Starting build process for version {self.version}...")
        
        self.docs_builder.build_api_docs()
        self.docs_builder.build_user_docs()
        
        self.changelog_generator.generate(self.version)
        
        CommandRunner.run(["git", "add", "CHANGELOG.md"], "Stage Changelog")
        CommandRunner.run(
            ["git", "commit", "-m", f"Update changelog for v{self.version}"], 
            "Commit Changelog"
        )
        
        self.git_releaser.release(self.version)
        
        logger.info(f"Build and release for version {self.version} completed successfully.")


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------
if __name__ == "__main__":
    # Check if arguments are provided
    if len(sys.argv) == 3:
        target_module = sys.argv[1]
        target_version = sys.argv[2]
        logger.info(f"Using provided arguments: module '{target_module}', version '{target_version}'")
        
    elif len(sys.argv) == 1:
        logger.info("No arguments provided. Reading configuration from pyproject.toml...")
        config_reader = ProjectConfigReader()
        target_module, target_version = config_reader.get_project_details()
        
    else:
        logger.error("Usage Error.")
        logger.error("Option 1 (Auto): python build.py")
        logger.error("Option 2 (Manual): python build.py <module_name> <version>")
        sys.exit(1)

    orchestrator = BuildOrchestrator(module_name=target_module, version=target_version)
    orchestrator.run_all()