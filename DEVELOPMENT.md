# Anki Math Randomizer - Development Notes

This repository contains the source for the **Anki Math Randomizer** add-on.

## Quick Links

- Repository: <https://github.com/athulkrishna2015/Anki-Math-Randomizer>
- AnkiWeb: <https://ankiweb.net/shared/info/263752551>
- Issues: <https://github.com/athulkrishna2015/Anki-Math-Randomizer/issues>
- Releases: <https://github.com/athulkrishna2015/Anki-Math-Randomizer/releases>

## Project Structure

- `addon/__init__.py`: Thin entry point that registers hooks.
- `addon/constants.py`: Shared constants, regexes, symbol pools, support metadata, and default config values.
- `addon/settings.py`: Config loading, normalization, persistence, and defaults.
- `addon/model.py`: Note-type creation and repair logic.
- `addon/randomizer.py`: Variable parsing, replacement, and review-time update flow.
- `addon/ui.py`: Tabbed addon configuration window, including the Support tab.
- `addon/Support/`: Donation QR codes used by the in-app Support tab.
- `addon/VERSION`: Current add-on version used by the release scripts.
- `bump.py`: Version management helper.
- `make_ankiaddon.py`: Packaging helper that creates the `.ankiaddon` artifact.
- `README.md`: User-facing documentation.

`addon/manifest.json` is optional. If you add one later, `bump.py` will keep its `version` and `human_version` fields in sync with `addon/VERSION`.

## Local Development

For fast iteration, symlink the `addon/` directory into your Anki add-ons folder.

Linux:

```shell
ln -s "$(pwd)/addon" ~/.local/share/Anki2/addons21/math_randomizer_dev
```

Windows PowerShell:

```powershell
New-Item -ItemType SymbolicLink -Path "$env:APPDATA\Anki2\addons21\math_randomizer_dev" -Target "$pwd\addon"
```

## Manual Verification Checklist

Use this checklist after changing the add-on logic:

1. Start Anki and confirm the note type `Math Randomizer (Daily Static)` exists.
2. Create or migrate a note with placeholders in `Source Front` and `Source Back`.
3. Enter review for a deck with spaces in its name and confirm matching notes update.
4. Test a subdeck and confirm the selected deck query still finds the right notes.
5. Put HTML such as `<div>` or `<br>` into the source fields and confirm the scanner does not treat those letters as static variables.
6. Verify the same placeholder maps to the same symbol on both the front and the back.
7. Verify lower-case Greek randomization can emit `\iota` and `\upsilon`.
8. Review the same note again on the same day and confirm it stays stable.
9. Confirm the stability is controlled by the `LastUpdate` field, then clear `LastUpdate`, review again, and confirm the note is regenerated.
10. Open `Tools -> Add-ons -> Math Randomizer -> Config` and verify the `General` and `Support` tabs both load using native Qt widgets.
11. Change the `General` tab settings, save them, reopen the dialog, and confirm the settings persist.
12. Disable one or more review states and confirm the randomizer respects the saved selection.
13. Disable the tooltip and confirm updates happen without the summary popup.
14. Open the `Support` tab and verify the Ko-fi section plus large QR cards for UPI, BTC, and ETH.
15. Test each copy button and confirm the clipboard content matches the shown payment ID.

## Lightweight Validation

There is no dedicated automated test suite in this repository yet. The quickest sanity checks are:

```shell
python -m py_compile addon/__init__.py addon/constants.py addon/settings.py addon/model.py addon/randomizer.py addon/ui.py bump.py make_ankiaddon.py
python make_ankiaddon.py 1.0.0 --output-dir /tmp
```

The build command writes the packaged `.ankiaddon` to `/tmp` so the repository tree stays clean.

## Versioning

`addon/VERSION` is the source of truth for release versioning.

Examples:

```shell
python bump.py
python bump.py minor
python bump.py major
python make_ankiaddon.py
python make_ankiaddon.py --part minor
python make_ankiaddon.py 1.2.0
```

Behavior summary:

- `python bump.py` bumps the patch version.
- If version metadata is missing, `bump.py` bootstraps `addon/VERSION` to `1.0.0`.
- `python make_ankiaddon.py` bumps the requested version part and then packages the add-on.
- `python make_ankiaddon.py 1.2.0` sets that exact version before packaging.

## Release Flow

1. Verify the add-on manually in Anki.
2. Run `python make_ankiaddon.py` or set an explicit version.
3. Commit the version change and source updates.
4. Create a git tag that matches the release version.
5. Upload the generated `.ankiaddon` file to the GitHub release page and AnkiWeb as needed.
