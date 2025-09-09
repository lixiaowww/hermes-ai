from pathlib import Path
import typer
import re

class ConstitutionGenerator:
    """
    Generates a dynamic "constitution" based on the current project state.
    This constitution serves as a meta-context for all agents.
    """
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()

    def generate(self) -> str:
        """
        Scans the project and generates the constitution text.
        """
        typer.secho("Generating project constitution...", fg=typer.colors.CYAN)
        
        constitution_parts = []
        constitution_parts.append("--- Project Constitution ---")
        constitution_parts.append("All agents must adhere to the following rules and context.")

        # 1. List project files
        try:
            files = self._list_project_files()
            constitution_parts.append("\n**Project File Structure:**")
            constitution_parts.append(files)
        except Exception as e:
            constitution_parts.append(f"\nCould not list project files: {e}")

        # 2. Extract coding standards and style
        try:
            coding_standards = self._extract_coding_standards()
            if coding_standards:
                constitution_parts.append("\n**Coding Standards:**")
                constitution_parts.append(coding_standards)
        except Exception as e:
            constitution_parts.append(f"\nCould not extract coding standards: {e}")

        # 3. Extract project configuration
        try:
            project_config = self._extract_project_config()
            if project_config:
                constitution_parts.append("\n**Project Configuration:**")
                constitution_parts.append(project_config)
        except Exception as e:
            constitution_parts.append(f"\nCould not extract project configuration: {e}")

        # 4. Extract architectural patterns
        try:
            arch_patterns = self._extract_architectural_patterns()
            if arch_patterns:
                constitution_parts.append("\n**Architectural Patterns:**")
                constitution_parts.append(arch_patterns)
        except Exception as e:
            constitution_parts.append(f"\nCould not extract architectural patterns: {e}")

        # 5. Add general coding guidelines
        constitution_parts.append("\n**General Coding Guidelines:**")
        constitution_parts.append(self._get_general_guidelines())

        constitution_parts.append("\n--- End of Constitution ---")
        return "\n".join(constitution_parts)

    def _list_project_files(self) -> str:
        """
        Lists all files in the project, ignoring common temporary files.
        Returns a string representation of the file tree.
        """
        tree = []
        for path in sorted(self.project_root.rglob("*")):
            if self._is_ignored(path):
                continue
            
            depth = len(path.relative_to(self.project_root).parts) - 1
            indent = "    " * depth
            if path.is_dir():
                tree.append(f"{indent}├── {path.name}/")
            else:
                tree.append(f"{indent}└── {path.name}")
        return "\n".join(tree)

    def _extract_coding_standards(self) -> str:
        """
        Extract coding standards from project configuration files.
        """
        standards = []
        
        # Check for pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            try:
                content = pyproject_path.read_text()
                if "black" in content.lower():
                    standards.append("- Use Black code formatter")
                if "flake8" in content.lower() or "pylint" in content.lower():
                    standards.append("- Follow PEP 8 style guidelines")
                if "mypy" in content.lower():
                    standards.append("- Use type hints and mypy for static type checking")
            except Exception:
                pass
        
        # Check for .python-version or similar
        python_version_files = [".python-version", ".python-version.txt"]
        for file_name in python_version_files:
            version_path = self.project_root / file_name
            if version_path.exists():
                try:
                    version = version_path.read_text().strip()
                    standards.append(f"- Target Python version: {version}")
                except Exception:
                    pass
        
        return "\n".join(standards) if standards else "No specific coding standards detected"

    def _extract_project_config(self) -> str:
        """
        Extract project configuration information.
        """
        config_info = []
        
        # Check pyproject.toml for project metadata
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            try:
                content = pyproject_path.read_text()
                # Extract project name
                name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                if name_match:
                    config_info.append(f"- Project name: {name_match.group(1)}")
                
                # Extract Python version requirement
                python_match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
                if python_match:
                    config_info.append(f"- Python requirement: {python_match.group(1)}")
                
                # Extract dependencies
                deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
                if deps_match:
                    deps = deps_match.group(1)
                    # Count dependencies
                    dep_count = len([line for line in deps.split('\n') if '=' in line])
                    config_info.append(f"- Dependencies: {dep_count} packages")
                    
            except Exception:
                pass
        
        return "\n".join(config_info) if config_info else "No project configuration detected"

    def _extract_architectural_patterns(self) -> str:
        """
        Extract architectural patterns from the codebase.
        """
        patterns = []
        
        # Check for common architectural indicators
        if (self.project_root / "zswe_agent").exists():
            patterns.append("- Multi-agent architecture with separate agent modules")
        
        if (self.project_root / "tests").exists():
            patterns.append("- Test-driven development (TDD) approach")
        
        # Check for specific design patterns in code
        try:
            for py_file in self.project_root.rglob("*.py"):
                if py_file.is_file() and not self._is_ignored(py_file):
                    content = py_file.read_text()
                    if "class" in content and "def" in content:
                        patterns.append("- Object-oriented design with classes and methods")
                        break
        except Exception:
            pass
        
        # Check for configuration management
        config_files = ["config.py", "settings.py", ".env", ".env.example"]
        for config_file in config_files:
            if (self.project_root / config_file).exists():
                patterns.append("- Configuration management with external config files")
                break
        
        return "\n".join(patterns) if patterns else "No specific architectural patterns detected"

    def _get_general_guidelines(self) -> str:
        """
        Return general coding guidelines that apply to all projects.
        """
        return """- Write clear, readable code with meaningful variable and function names
- Include docstrings for all public functions and classes
- Handle errors gracefully with appropriate exception handling
- Write unit tests for all new functionality
- Follow the DRY (Don't Repeat Yourself) principle
- Keep functions small and focused on a single responsibility
- Use type hints where appropriate
- Ensure code is well-documented and self-explanatory"""

    def _is_ignored(self, path: Path) -> bool:
        """
        Checks if a path should be ignored (e.g., .git, __pycache__).
        """
        ignored_patterns = [".git", "__pycache__", ".DS_Store", ".venv", "node_modules", "*.pyc", "*.pyo", "__pycache__"]
        return any(part in ignored_patterns for part in path.parts) or path.name.endswith(('.pyc', '.pyo'))
