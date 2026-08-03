# ComplexCalc

A self-contained Python program for the **TI-Nspire CX II CAS** (OS 6.x) and
desktop Python 3 that does complex-number math, including **Euler's formula**
conversions between rectangular, trigonometric and exponential forms.

## Features

- **Euler conversions (both directions)**
  - Rectangular `a + bi`  ⇄  Trigonometric `r(cos θ + i sin θ)`  ⇄  Exponential `r·e^(iθ)`
  - Select **1 Convert forms** in the main menu, enter the number in any of the
    three forms, and all forms are shown at once.
- **Full complex algebra**: `+`, `-`, `*`, `/`, powers (`z^n`, De Moivre),
  all `n`-th roots, conjugate, modulus, argument.
- **CAS-exact radicals (true symbolic output)**: on the device the program asks
  the CAS engine itself for exact values, instead of guessing.
  - Modulus of any number with integer parts is exact: `|3+4i| = 5`,
    `|1+i| = √(2)`, `|2+3i| = √(13)`.
  - Argument is exact when it is a nice multiple of `π`: `arg(1+i) = π/4`.
  - Entering polar form with a fraction of `π` gives exact radicals:
    `r=2, θ=π/4  →  √2 + √2i` ; `r=2, θ=π/3  →  1 + √3i`.
  - Everywhere a CAS answer is not available or not symbolic, the program falls
    back to a snapped exact-looking value or a clean decimal — it never errors.
- **Angle mode toggled at run time**: radians as fractions of `π`, or degrees.
- The imaginary unit is shown as `i` (math convention); internally Python uses `j`.

## CAS bridge

Exact output is obtained with the same technique as the public-domain
TI-Planet `eval_expr` library: the Python program asks `ti_system` to
`string(...)`-evaluate a TI-Basic expression on the device CAS and reads back
the exact text (e.g. `√(13)`, `π/4`). It is:

- **Self-contained** (no third-party module to install).
- **Optional**: toggled with **7 toggle exact (CAS) display** in the main menu.
- **Portable**: on a non-CAS calculator or a desktop (`HAS_TI` is false) the
  CAS bridge is never called and the program runs purely numerically.

## Files

| File | Purpose |
|------|---------|
| `complexcalc.py` | The program. Runs on the calculator and on a PC. |
| `test_complexcalc.py` | Desktop self-test for the math engine, renderer and CAS fallbacks. |

## Run on a PC

```
python test_complexcalc.py     # self-test (note: exact-mode tests simulate CAS)
python complexcalc.py          # interactive
```

Everything is pure `math`/`cmath`, identical between desktop Python and the
calculator's Python, so passing the desktop tests predicts on-device behavior.
On a PC there is no `ti_system`, so the CAS bridge stays off and output is the
numeric/snap form.

## Load onto the TI-Nspire CX II CAS (OS 6.2)

Option A – Student Software / Teacher Software:
1. Connect the handheld.
2. In TI-Nspire CX software: **File ▸ New ▸ Python Program**.
3. Paste the contents of `complexcalc.py`, then save.
4. Transfer the resulting document to the handheld.

Option B – direct on the handheld:
1. **Home ▸ New ▸ Python ▸ Python Program**, name it (e.g. `complexcalc`).
2. Type or paste the file contents (only if you have the TI keyboard/menu
   chars for `π`, `√`, `·`; otherwise see note below).
3. **Ctrl + B** (or the play key) to run.

Option C – as a reusable module (advanced):
1. Install into `PyLib` (in the software: **Tools ▸ Install as Python Module**).
2. Then in any other Python program: `from complexcalc import Cplx, fmt_rect`.

> On-device exact mode is enabled by default. If the CAS bridge does not behave
> on your exact OS version (older/different firmware), toggle exact OFF with
> menu item **7** and the program still works with snapped/numeric output.

## Usage

```
MAIN MENU
  1 convert forms (Euler)      — enter a number any way, see all 3 forms
  2 arithmetic (+ - * /)       — enter two numbers, pick an operation
  3 powers and roots           — z^n, or the n-th roots (De Moivre)
  4 modulus / argument / conjugate
  5 save / recall              — keep a result under a name for the session
  6 toggle angle mode (RAD/DEG)
  7 toggle exact (CAS) display
  q quit
```

- `q` at any prompt quits.
- Entering a number: choose **1** (rectangular, enter `a` then `b`), **2**
  (polar, enter `r` and `θ`), or **3** (exponential, same as polar).
- For `θ` in RAD mode, type a fraction of `π` (e.g. `1/4` = `π/4`) or a
  decimal in radians. In DEG mode, type degrees.

## Notes

- The non-CAS exact display is a **snap**: if a computed value is within `1e-5`
  of a nice fraction of `π` or a common radical, it is shown exactly; otherwise
  a clean decimal is shown.
- If `π` / `√` / `·` do not appear correctly on your calculator, replace the
  constants at the top of `complexcalc.py` (`SYMPI`, `SQRT`, `DOT`) with ASCII,
  e.g. `SYMPI = "pi"`, `SQRT = "sqrt"`, `DOT = "*"`.