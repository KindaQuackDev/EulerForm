# EulerForm

## 1. Purpose

EulerForm is a Python program that performs complex-number operations.
Run the program on the TI-Nspire CX II CAS calculator (OS 6.x) or on a PC.

The program uses Euler's formula to convert a complex number
between three equal forms:

1. Rectangular form: `a + b*i`.
2. Trigonometric form: `r*(cos θ + i*sin θ)`.
3. Exponential form: `r*e^(iθ)`.

EulerForm's primary function is to perform complex algebra, but can also add, subtract,
multiply, and divide complex numbers. EulerForm is also able to compute powers/n-th
roots and return the modulus, argument, and conjugate of a complex number. 

## 2. Symbolic output

The program shows exact values when it can, and gives an exact result
when the input parts are integers.

Modulus examples:

- `|1+i|` shows `√2`.
- `|2+3i|` shows `√13`.
- `|3+4i|` shows `5`.

Arguments are shown in one of three forms:

1. A fraction of π. The argument of `1+i` shows as `π/4`.
2. A symbolic inverse tangent. The argument of `3+4i` shows as `atan(4/3)`.
3. A decimal value. This form occurs when the real part and the imaginary
   part are not integers.

Example. Convert `3+4i` to exponential form. The program shows:

- `5 * e^(i * atan(4/3))`

It does not show a rounded decimal angle for integer input.

### Exact mode

EulerForm has an exact mode. In this mode, the program calls the CAS engine
of the calculator. The CAS engine returns exact symbolic values. The menu
item `7` toggles the exact mode.

The exact mode is OFF on PC. The exact mode is ON on the calculator by
default. The exact mode won't do anything on a PC due to the lack of a CAS engine.
Symbolic angles ARE still shown on PC. This is possible because EulerForm computes the symbolic angle in Python code.

## 3. Files

This table lists the files of the project.

| File | Purpose |
|------|---------|
| `eulerform.py` | The main program. |
| `test_eulerform.py` | The self-test which runs on PC. |
| `README.md` | This file. |

## 4. To change the display characters

EulerForm shows these characters: `π`, `√`, `·`.

If your device can not show these characters, change the constants at the
top of `eulerform.py`, using ASCII text instead.

Change the constants to these values:

- `SYMPI = "pi"`
- `SQRT = "sqrt"`
- `DOT = "*"`

## 5. To run the program on PC

Create a virtual environment in the project folder. Use this command:

```
python -m venv .venv
```

Run the self-test. Use this command:

```
python test_eulerform.py
```

The self-test passes when it shows `ALL TESTS PASSED`.

Run the program. Use this command:

```
python eulerform.py
```

Note: The PC version has no CAS engine so exact mode stays OFF, meaning the
program will work in numeric mode.

## 6. To load the program on the calculator

### Method 1: Use the computer software

1. Connect the calculator to the computer with a USB cable.
2. Open the TI-Nspire CX software on the computer.
3. Select **File > New > Python Program**.
4. Paste the contents of `eulerform.py`.
5. Save the document.
6. Transfer the document to the calculator.

### Method 2: Type directly on the calculator

1. Select **Home > New > Python > Python Program**.
2. Type the name of the program. For example, type `eulerform`.
3. Type or paste the contents of the file.
4. Press **Ctrl+B** to run the program.

### Method 3: Install the program as a module

1. Use the software command **Tools > Install as Python Module**.
2. The software moves the file to the `PyLib` folder.
3. In another program, type this command:

```
from eulerform import Cplx, fmt_rect
```

## 7. To use the program

Start EulerForm. The program will shows the main menu with seven items
and a quit command.

| Item | Function |
|------|----------|
| `1` | Convert the forms of a number. |
| `2` | Add, subtract, multiply, or divide two numbers. |
| `3` | Compute a power or the n-th roots. |
| `4` | Show the modulus, the argument, and the conjugate. |
| `5` | Save or recall a result. |
| `6` | Toggle the angle mode. |
| `7` | Toggle the exact mode. |
| `q` | Quit the program. |

### To enter a number

EulerForm will ask for the form of the number. Select one of these items:

1. **Rectangular**. Type the real part `a`. Type the imaginary part `b`.
2. **Polar**. Type the modulus `r`. Type the argument `θ`.
3. **Exponential**. The program uses the same prompts as polar.

Type `q` to quit a prompt.

### To enter an angle

The angle mode is `RAD` or `DEG`. The mode determines how you type the angle.

In `RAD` mode:

- Type a fraction of π. For example, type `1/4`. The program reads this as `π/4`.
- Type a decimal value. The program reads this value as radians.

In `DEG` mode:

- Type the angle in degrees. For example, type `45`.

## 8. Notes

- The exact display is a "snap". EulerForm compares a computed value with a
  set of simple values. If the difference is below a limit (`1e-5`), the simple 
  value is shown. The program shows a clean decimal value when no simple 
  value matches.
- Angles are shown as a fraction of π when the angle is a multiple
  of π. EulerForm will show the angle as `atan(b/a)` when the parts are
  integers, and shows a decimal value in other cases.
