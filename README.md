# Anki Math Randomizer (Static Daily & Deck-Aware)

A robust Anki add-on that randomizes mathematical variables in your flashcards to prevent rote pattern recognition.

## Key Features

* **Static Rendering:** Converts your template variables (e.g., `VL1`) into actual characters (e.g., `X`) inside the card fields. Zero render-time glitches.
* **Deck-Aware Trigger:** Automatically checks for cards needing updates when you enter the **Review Screen** for a specific deck.
* **Daily Frequency:** Randomizes cards once per day. If you review a card multiple times in one day, it stays consistent to avoid confusion.
* **Smart Conflict Avoidance:**
    * **Static Scanning:** Scans your equation for existing variables (e.g., if you wrote `x + y`, it won't pick `x` or `y` as random variables).
    * **Visual Safety:** Prevents visually similar symbols from appearing together (e.g., never mixes `l`, `I`, `1`, and `|`).
* **Variable Pools:** Supports Upper/Lower Latin, Upper/Lower Greek, and Numbers.

## Setup & Migration (Crucial Step)

Because this add-on writes data to specific fields, you must set up the Note Type correctly.

1.  **Restart Anki** after installing.
2.  Go to the **Browser** and select your math cards.
3.  Right-click → **Change Note Type**.
4.  Select **"Math Randomizer (Daily Static)"**.
5.  **Map your fields carefully:**
    * Map your **Old Code/Question** → **Source Front**
    * Map your **Old Answer** → **Source Back**
    * **Front** → *(Leave Empty / Ignore)*
    * **Back** → *(Leave Empty / Ignore)*
    * **LastUpdate** → *(Leave Empty / Ignore)*

## How to Use

### 1. Creating Cards
You no longer type into the "Front" field. Instead, use the **Source** fields.

* **Source Front:** Enter your equation with variable tags.
    * *Example:* `\( \int VL1 \, dVL1 \)`
* **Source Back:** Enter the answer.
    * *Example:* `\( \frac{VL1^2}{2} + C \)`
* **Front / Back:** Leave these empty. The add-on will fill them automatically.

### 2. Studying
1.  Click on a Deck.
2.  Click **"Study Now"**.
3.  The add-on instantly scans all **Due** or **New** cards in that deck.
4.  If a card hasn't been randomized today, it swaps the variables (e.g., changing `VL1` to `X`).
5.  You see `\( \int X \, dX \)` on your screen.

## Variable Tags Reference

You can use any index number (e.g., `VL1`, `VL2`, `Vg99`).

| Tag | Type | Description | Example Output |
| :--- | :--- | :--- | :--- |
| **VL[n]** | **Upper Latin** | Uppercase A-Z | $A, X, M$ |
| **Vl[n]** | **Lower Latin** | Lowercase a-z | $a, x, m$ |
| **VG[n]** | **Upper Greek** | Uppercase Greek | $\Gamma, \Delta, \Omega$ |
| **Vg[n]** | **Lower Greek** | Lowercase Greek | $\alpha, \beta, \theta$ |
| **VN[n]** | **Numbers** | Integers (2-9) | $2, 5, 9$ |
| **VV[n]** | **Mixed** | Any Latin or Greek | $X, \lambda, \Omega, m$ |

## Visual Conflict Safety

The add-on ensures the following groups of symbols never appear together in the same equation:

* **Verticals:** `I`, `l`, `1`, `|`
* **Circles:** `O`, `o`, `0`, `Q`, `\Theta`, `\theta`
* **V-shapes:** `v`, `\nu`, `\upsilon`
* **U-shapes:** `u`, `\mu`
* **W-shapes:** `w`, `\omega`
* **X-shapes:** `x`, `\chi`, `\times`
* **P-shapes:** `p`, `\rho`
* **B-shapes:** `B`, `\beta`

## Troubleshooting

**"My cards are empty!"**
Check your Field Mapping. The data must be in **Source Front**, not Front. The "Front" field is overwritten by the script.

**"The variable didn't change!"**
The script only updates a card **once per day** to save processing power and avoid confusion during re-learning steps. Wait until tomorrow, or manually clear the `LastUpdate` field in the browser if you want to force a refresh.

**"It's not working on AnkiDroid."**
Sync your devices. Since the logic runs on the Desktop and saves the result as standard text, AnkiDroid just needs to sync to see the updated equations.