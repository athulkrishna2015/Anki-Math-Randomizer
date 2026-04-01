# [Anki Math Randomizer](https://github.com/athulkrishna2015/Anki-Math-Randomizer)

Install via [AnkiWeb](https://ankiweb.net/shared/info/263752551).

Anki Math Randomizer is a desktop add-on that rewrites placeholder variables in your math cards into visually distinct symbols. The generated result is stored directly in the note, so the same randomized card also syncs cleanly to AnkiDroid and AnkiMobile.

## What It Does

- Creates or updates a dedicated note type named `Math Randomizer (Daily Static)`.
- Reads placeholders from `Source Front` and `Source Back`.
- Writes the rendered result to `Front` and `Back`.
- Randomizes each matching note at most once per day.
- Keeps front/back substitutions consistent for the same note.
- Avoids visually confusing combinations such as `I`, `l`, `1`, and `|`.
- Detects existing static symbols in LaTeX and regular text so they are less likely to be reused.

## Placeholder Tags

Use any numeric suffix you want, such as `VL1`, `Vg2`, or `VV99`.

| Tag | Pool | Example outputs |
| --- | --- | --- |
| `VL[n]` | Uppercase Latin | `A`, `M`, `X` |
| `Vl[n]` | Lowercase Latin | `a`, `m`, `x` |
| `VG[n]` | Uppercase Greek | `\Gamma`, `\Lambda`, `\Omega` |
| `Vg[n]` | Lowercase Greek | `\alpha`, `\iota`, `\upsilon` |
| `VN[n]` | Numbers | `2`, `5`, `9` |
| `VV[n]` | Mixed Latin/Greek | `Q`, `\phi`, `\Psi` |

## Setup

1. Install the add-on and restart Anki.
2. Open the Browser and select the notes you want to migrate.
3. Use `Change Note Type...` and pick `Math Randomizer (Daily Static)`.
4. Map your original prompt/content field to `Source Front`.
5. Map your original answer/solution field to `Source Back`.
6. Leave `Front`, `Back`, and `LastUpdate` empty so the add-on can manage them.

If the note type already exists, the add-on now fills in any missing required fields automatically.

## Example

`Source Front`

```tex
\( \int VL1 \, dVL1 \)
```

`Source Back`

```tex
\( \frac{VL1^2}{2} + C \)
```

One day the generated card may become:

```tex
\( \int X \, dX \)
\( \frac{X^2}{2} + C \)
```

On another day it may become:

```tex
\( \int \lambda \, d\lambda \)
\( \frac{\lambda^2}{2} + C \)
```

## When Randomization Runs

The add-on checks for matching notes when you enter the review screen for the currently selected deck. It updates due, new, and learning cards in that deck before review continues.

## Configuration

Open `Tools -> Add-ons -> Math Randomizer -> Config` to manage the addon.

The `General` tab lets you:

- Enable or disable automatic randomization on review.
- Choose whether due, new, and learning cards should be processed.
- Control whether a summary tooltip is shown and how long it stays visible.
- Decide whether the reviewer should refresh immediately after the current card is updated.
- Decide whether the Math Randomizer note type should be created or repaired on profile open.
- Keep using the `LastUpdate` field so each note stays stable for the rest of the day after it has been randomized.

The config window now uses native Qt widgets. The `Support` tab keeps Ko-fi, UPI, BTC, and ETH options in the same native window without embedding a webpage.

## Troubleshooting

`The card stayed the same today`

Each note is randomized once per day. The addon still uses the `LastUpdate` field to enforce that. Clear the `LastUpdate` field if you want to force a refresh before the next day.

`My variables are not changing`

Make sure your placeholders are in `Source Front` or `Source Back`, not directly in `Front` or `Back`.

`My deck name has spaces or subdecks`

That is supported. The review query now escapes deck names correctly.

`My cards contain HTML from the editor`

That is supported too. The static-symbol scan strips HTML markup before choosing replacements.

## Support

Open `Tools -> Add-ons -> Math Randomizer -> Config` and switch to the `Support` tab. It includes:

- Large, scrollable QR codes for UPI, BTC, and ETH.
- One-click copy buttons for the UPI ID and wallet addresses.
- A Ko-fi section with native Qt controls and a direct support link.

Ko-fi:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/D1D01W6NQT)

Direct payment IDs:

- `UPI`: `athulkrishnasv2015-2@okhdfcbank`
- `BTC`: `bc1qrrek3m7sr33qujjrktj949wav6mehdsk057cfx`
- `ETH`: `0xce6899e4903EcB08bE5Be65E44549fadC3F45D27`

## Changelog

### 2026-04-01

- Added deck-aware daily randomization for notes using the `Math Randomizer (Daily Static)` note type.
- Added conflict-aware variable selection across Latin, Greek, mixed-symbol, and number pools.
- Improved parsing so existing HTML and LaTeX content do not interfere with variable replacement choices.
- Added automatic note-type setup and missing-field repair on profile open.
- Added a tabbed configuration window with `General` and `Support` tabs under `Tools -> Add-ons -> Math Randomizer -> Config`.
- Added saved runtime settings for review-state filtering, tooltip behavior, reviewer refresh, and note-type maintenance.
- Kept `LastUpdate` as the once-per-day guard for note regeneration.
- Added large QR-based support options for UPI, BTC, and ETH, plus copy buttons for payment IDs.
- Added Ko-fi links inside the native Qt support tab.
- Added local versioning and packaging workflow via `bump.py`, `make_ankiaddon.py`, and `addon/VERSION`.
- Split the addon implementation into smaller modules for easier maintenance.

## Development

Release tooling lives in [make_ankiaddon.py](make_ankiaddon.py) and [bump.py](bump.py). The current add-on version is stored in [addon/VERSION](addon/VERSION).

For local development and release steps, see [DEVELOPMENT.md](DEVELOPMENT.md).
