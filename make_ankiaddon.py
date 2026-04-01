import argparse
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path

from bump import bump_version, read_current_version, sync_version, validate_version

ADDON_NAME = "Math_Randomizer"
ADDON_DIR = "addon"
EXCLUDE_DIRS = {"__pycache__", ".git", ".github", ".vscode", "tests"}
EXCLUDE_EXTENSIONS = {".ankiaddon", ".pyc"}
EXCLUDE_FILES = {".gitignore", ".gitmodules", "meta.json", "mypy.ini"}


def artifact_paths(
    output_dir: Path,
    addon_name: str,
    version: str,
    when: datetime | None = None,
) -> tuple[Path, Path]:
    dt = when or datetime.today()
    timestamp = dt.strftime("%Y%m%d%H%M")
    base_name = f"{addon_name}_v{version}_{timestamp}"
    return output_dir / f"{base_name}.zip", output_dir / f"{base_name}.ankiaddon"


def iter_addon_files(addon_path: Path):
    for root, dirs, files in os.walk(addon_path):
        dirs[:] = sorted(directory for directory in dirs if directory not in EXCLUDE_DIRS)
        for file_name in sorted(files):
            file_path = Path(root) / file_name
            if file_name in EXCLUDE_FILES or file_path.suffix in EXCLUDE_EXTENSIONS:
                continue
            yield file_path


def prepare_build_version(
    addon_path: Path,
    explicit_version: str | None = None,
    bump_part: str = "patch",
) -> str:
    if explicit_version is not None:
        version = validate_version(explicit_version)
        sync_version(version, addon_path)
        print(f"Using explicit version: {version}")
        return version

    exit_code = bump_version(addon_path, bump_part)
    if exit_code != 0:
        raise RuntimeError("Failed to prepare the build version.")
    return read_current_version(addon_path)


def create_ankiaddon(
    explicit_version: str | None = None,
    bump_part: str = "patch",
    output_dir: Path | None = None,
) -> int:
    root_dir = Path(__file__).resolve().parent
    addon_path = root_dir / ADDON_DIR
    build_output_dir = (output_dir or root_dir).resolve()

    if not addon_path.is_dir():
        print(f"Error: {addon_path} directory not found.")
        return 1

    build_output_dir.mkdir(parents=True, exist_ok=True)

    try:
        build_version = prepare_build_version(addon_path, explicit_version, bump_part)
    except Exception as error:
        print(f"Error: Could not prepare build version: {error}")
        return 1

    zip_path, addon_package_path = artifact_paths(
        build_output_dir,
        ADDON_NAME,
        build_version,
    )

    print(f"Creating {addon_package_path.name} from {addon_path}...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in iter_addon_files(addon_path):
            zip_file.write(file_path, file_path.relative_to(addon_path))

    addon_package_path.unlink(missing_ok=True)
    zip_path.replace(addon_package_path)
    print(f"Successfully created: {addon_package_path}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create an .ankiaddon package from the addon directory. "
            "If no version is provided, the selected version part is bumped first."
        )
    )
    parser.add_argument(
        "version",
        nargs="?",
        help="Optional explicit version (major.minor.patch) to set before packaging.",
    )
    parser.add_argument(
        "--part",
        default="patch",
        help="Version part to bump when no explicit version is supplied.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory where the .ankiaddon artifact should be written. Defaults to the project root.",
    )
    return parser.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    output_dir = Path(args.output_dir) if args.output_dir else None
    return create_ankiaddon(args.version, args.part, output_dir)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
