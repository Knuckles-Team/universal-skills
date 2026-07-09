#!/usr/bin/env python3
import shutil
import sys
from pathlib import Path


def init_scaffold():
    """Initializes the Next.js scaffold for website cloning."""
    try:
        # Determine the skill's root directory
        skill_root = Path(__file__).parent.parent.resolve()
        scaffold_path = skill_root / "assets" / "scaffold"

        if not scaffold_path.exists():
            print(f"Error: Scaffold directory not found at {scaffold_path}")
            sys.exit(1)

        target_dir = Path.cwd()

        # Check if the target directory is empty or if the user wants to force
        if any(target_dir.iterdir()):
            print("Warning: Current directory is not empty.")
            confirm = input(
                "Are you sure you want to initialize the scaffold here? (y/n): "
            )
            if confirm.lower() != "y":
                print("Initialization cancelled.")
                sys.exit(0)

        print(f"Initializing website-cloner scaffold from {scaffold_path}...")

        # Copy files
        for item in scaffold_path.iterdir():
            if item.is_dir():
                shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target_dir / item.name)

        print("\nScaffold initialized successfully!")
        print("\nNext steps:")
        print("1. npm install")
        print("2. npm run dev")
        print("3. Start cloning using the instructions in SKILL.md")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_scaffold()
