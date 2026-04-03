import re
import json
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


def get_latest_version(package_name):
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data["info"]["version"]
    except Exception:
        pass
    return None


def parse_dependencies(root_dir="."):
    root = Path(root_dir)
    pyproject = root / "pyproject.toml"
    requirements = root / "requirements.txt"

    deps = {}

    if pyproject.exists():
        content = pyproject.read_text()
        # Find dependencies in [project] dependencies = [...] or [tool.poetry.dependencies]
        # This regex is simplified for general use
        matches = re.findall(r'"([^"<>=\s]+)([~^>=<]+[^"]+)?"', content)
        for name, ver in matches:
            if name.lower() not in ["python"]:
                deps[name] = ver or "Any"

    elif requirements.exists():
        content = requirements.read_text()
        matches = re.findall(r"^([^#<>=\s]+)([~^>=<]+[\d\.]+)?", content, re.MULTILINE)
        for name, ver in matches:
            deps[name] = ver or "Any"

    return deps


def check_updates(root_dir="."):
    deps = parse_dependencies(root_dir)
    results = {}

    # Check in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_package = {
            executor.submit(get_latest_version, pkg): pkg for pkg in deps
        }
        for future in future_to_package:
            pkg = future_to_package[future]
            latest = future.result()
            if latest:
                results[pkg] = {
                    "current": deps[pkg],
                    "latest": latest,
                    "update_available": latest not in (deps[pkg] or ""),
                }

    return results


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "."
    updates = check_updates(target)
    print(json.dumps(updates, indent=2))
