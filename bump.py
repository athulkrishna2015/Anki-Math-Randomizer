import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_INITIAL_VERSION = "1.0.0"
VERSION_FILE_NAME = "VERSION"
MANIFEST_FILE_NAME = "manifest.json"

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
SHORT_VERSION_RE = re.compile(r"^\d+\.\d+$")
BUMP_PART_ALIASES = {
    "major": "major",
    "minor": "minor",
    "patch": "patch",
    "path": "patch",
}


def normalize_version(version_string: str) -> str:
    version = (version_string or "").strip()
    if SHORT_VERSION_RE.fullmatch(version):
        return f"{version}.0"
    return version


def validate_version(version_string: str) -> str:
    normalized = normalize_version(version_string)
    if not VERSION_RE.fullmatch(normalized):
        raise ValueError(
            f"Invalid version '{version_string}'. Expected format: major.minor.patch"
        )
    return normalized


def version_file_path(addon_root: Path) -> Path:
    return addon_root / VERSION_FILE_NAME


def manifest_file_path(addon_root: Path) -> Path:
    return addon_root / MANIFEST_FILE_NAME


def normalize_bump_part(part: str) -> str:
    normalized = (part or "").strip().lower()
    mapped = BUMP_PART_ALIASES.get(normalized)
    if not mapped:
        valid = ", ".join(sorted(key for key in BUMP_PART_ALIASES if key != "path"))
        raise ValueError(f"Invalid bump part '{part}'. Expected one of: {valid}")
    return mapped


def increment_version(version_string: str, bump_part: str = "patch") -> str:
    try:
        major, minor, patch = map(int, version_string.split("."))
    except ValueError as error:
        raise ValueError(
            f"Invalid version '{version_string}'. Expected major.minor.patch"
        ) from error

    part = normalize_bump_part(bump_part)
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1

    return f"{major}.{minor}.{patch}"


def increment_patch(version_string: str) -> str:
    return increment_version(version_string, "patch")


def write_version_file(addon_root: Path, version_string: str) -> None:
    version_file_path(addon_root).write_text(f"{version_string}\n", encoding="utf-8")


def sync_manifest_version(addon_root: Path, version_string: str) -> bool:
    manifest_path = manifest_file_path(addon_root)
    if not manifest_path.exists():
        return False

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = version_string
    manifest["human_version"] = version_string
    manifest_path.write_text(f"{json.dumps(manifest, indent=2)}\n", encoding="utf-8")
    return True


def sync_version(version_string: str, addon_root: Path) -> list[str]:
    normalized_version = validate_version(version_string)
    if not addon_root.is_dir():
        raise FileNotFoundError(f"Addon directory not found: {addon_root}")

    targets = []
    write_version_file(addon_root, normalized_version)
    targets.append(VERSION_FILE_NAME)

    if sync_manifest_version(addon_root, normalized_version):
        targets.append(MANIFEST_FILE_NAME)

    return targets


def read_current_version(addon_dir: Path) -> str:
    version_path = version_file_path(addon_dir)
    if version_path.exists():
        return validate_version(version_path.read_text(encoding="utf-8").strip())

    manifest_path = manifest_file_path(addon_dir)
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for key in ("human_version", "version"):
            value = str(manifest.get(key, "")).strip()
            if not value:
                continue

            try:
                return validate_version(value)
            except ValueError:
                continue

    raise FileNotFoundError(
        f"Could not determine current version from {version_path} or {manifest_path}"
    )


def bootstrap_version(
    addon_dir: Path,
    initial_version: str = DEFAULT_INITIAL_VERSION,
) -> str:
    version = validate_version(initial_version)
    sync_version(version, addon_dir)
    return version


def bump_version(addon_dir: Path = Path("addon"), bump_part: str = "patch") -> int:
    try:
        part = normalize_bump_part(bump_part)
        try:
            current_version = read_current_version(addon_dir)
        except FileNotFoundError:
            bootstrapped = bootstrap_version(addon_dir)
            print(
                "No version metadata found. "
                f"Bootstrapped {VERSION_FILE_NAME} to {bootstrapped}"
            )
            return 0

        new_version = increment_version(current_version, part)
        print(f"Bumping {part} version: {current_version} -> {new_version}")
        synced_targets = sync_version(new_version, addon_dir)
        print(f"Updated {', '.join(synced_targets)} to {new_version}")
        return 0
    except Exception as error:
        print(f"Failed to bump version: {error}")
        return 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Bump add-on version metadata. "
            f"If no version metadata exists yet, {DEFAULT_INITIAL_VERSION} is created."
        )
    )
    parser.add_argument(
        "part",
        nargs="?",
        default="patch",
        help="Bump part: major, minor, patch (or 'path' alias).",
    )
    parser.add_argument(
        "--addon-dir",
        default="addon",
        help="Path to the addon directory (default: addon).",
    )
    return parser.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    return bump_version(Path(args.addon_dir), args.part)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
