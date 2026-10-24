"""Accept all tracked changes in a DOCX file using LibreOffice.

Requires LibreOffice (soffice) to be installed.
"""

import argparse
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from office.soffice import get_soffice_env

logger = logging.getLogger(__name__)

ACCEPT_CHANGES_MACRO = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Module1" script:language="StarBasic">
    Sub AcceptAllTrackedChanges()
        Dim document As Object
        Dim dispatcher As Object

        document = ThisComponent.CurrentController.Frame
        dispatcher = createUnoService("com.sun.star.frame.DispatchHelper")

        dispatcher.executeDispatch(document, ".uno:AcceptAllTrackedChanges", "", 0, Array())
        ThisComponent.store()
        ThisComponent.close(True)
    End Sub
</script:module>"""


def accept_changes(
    input_file: str,
    output_file: str,
) -> tuple[None, str]:
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.is_file() or input_path.is_symlink():
        return None, "Error: configured input file was not found"

    if not input_path.suffix.lower() == ".docx":
        return None, "Error: configured input file is not a DOCX file"

    if output_path.is_symlink() or (output_path.exists() and not output_path.is_file()):
        return None, "Error: configured output path is not a regular file"

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(input_path, output_path)
    except Exception as e:
        return None, f"Error: Failed to copy input file to output location: {type(e).__name__}"

    # A private, per-invocation profile prevents predictable /tmp symlink attacks and
    # keeps concurrent conversions from sharing executable macro state.
    with tempfile.TemporaryDirectory(prefix="libreoffice-docx-") as profile_name:
        profile_dir = Path(profile_name)
        if not _setup_libreoffice_macro(profile_dir):
            return None, "Error: Failed to setup LibreOffice macro"

        cmd = [
            "soffice",
            "--headless",
            f"-env:UserInstallation={profile_dir.resolve().as_uri()}",
            "--norestore",
            "vnd.sun.star.script:Standard.Module1.AcceptAllTrackedChanges?language=Basic&location=application",
            str(output_path.resolve()),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                env=get_soffice_env(),
            )
        except subprocess.TimeoutExpired:
            return None, "Error: LibreOffice conversion timed out"

    if result.returncode != 0:
        return None, "Error: LibreOffice conversion failed"

    return None, "Successfully accepted all tracked changes"


def _setup_libreoffice_macro(profile_dir: Path) -> bool:
    macro_dir = profile_dir / "user" / "basic" / "Standard"
    macro_file = macro_dir / "Module1.xba"

    if macro_file.exists() and "AcceptAllTrackedChanges" in macro_file.read_text():
        return True

    if not macro_dir.exists():
        subprocess.run(
            [
                "soffice",
                "--headless",
                f"-env:UserInstallation={profile_dir.resolve().as_uri()}",
                "--terminate_after_init",
            ],
            capture_output=True,
            timeout=10,
            check=False,
            env=get_soffice_env(),
        )
        macro_dir.mkdir(parents=True, exist_ok=True)

    try:
        macro_file.write_text(ACCEPT_CHANGES_MACRO, encoding="utf-8")
        macro_file.chmod(0o600)
        return True
    except Exception as e:
        logger.warning(f"Failed to setup LibreOffice macro: {type(e).__name__}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Accept all tracked changes in a DOCX file"
    )
    parser.add_argument("input_file", help="Input DOCX file with tracked changes")
    parser.add_argument(
        "output_file", help="Output DOCX file (clean, no tracked changes)"
    )
    args = parser.parse_args()

    _, message = accept_changes(args.input_file, args.output_file)
    print(message)

    if "Error" in message:
        raise SystemExit(1)
