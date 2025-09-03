#!/usr/bin/env python3
"""
Publishing script for CSV Editor package.
Handles building, testing, and publishing to PyPI.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    return result


def main():
    """Main publishing workflow."""
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("🚀 Starting CSV Editor publishing process...")

    # 1. Clean previous builds
    print("\n📦 Cleaning previous builds...")
    run_command("rm -rf dist/ build/ *.egg-info/")

    # 2. Run tests
    print("\n🧪 Running tests...")
    run_command("uv run pytest tests/ -v")

    # 3. Run linting
    print("\n🔍 Running linting...")
    run_command("uv run ruff check src/")
    run_command("uv run black --check src/")

    # 4. Type checking
    print("\n📝 Running type checking...")
    run_command("uv run mypy src/")

    # 5. Build package
    print("\n🔨 Building package...")
    run_command("uv build")

    # 6. Check package
    print("\n✅ Checking package...")
    run_command("uv run twine check dist/*")

    # 7. Test installation
    print("\n📥 Testing package installation...")
    run_command("uv pip install dist/*.whl --force-reinstall")

    print("\n✨ Package built successfully!")
    print("\nNext steps:")
    print("1. Test publish: uv run twine upload --repository testpypi dist/*")
    print("2. Real publish: uv run twine upload dist/*")
    print("3. Or create a GitHub release to trigger automatic publishing")


if __name__ == "__main__":
    main()
