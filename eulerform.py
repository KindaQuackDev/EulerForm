# Complex Number Calculator
# For TI-Nspire CX II CAS (OS 6.x) and desktop Python 3.
#
# Features:
#   * Euler conversion between rectangular, trigonometric and
#     exponential forms (both directions)
#   * Full complex algebra: + - * / , powers (De Moivre), n-th roots,
#     conjugate, modulus and argument
#   * Exact symbolic output on the CAS: when EXACT mode is on and the
#     result has exact integer parts, the modulus and argument are
#     computed by the device CAS engine (sqrt(13), pi/4, ...) instead
#     of being snapped. Entering polar form with a fraction of pi
#     yields exact radicals (e.g. r=2, theta=pi/3 -> 1 + sqrt(3) i).
#   * Falls back to clean decimals / snapping when no CAS is present
#     (e.g. on a desktop) or when values are not exact.
#   * Angle mode (radians-fractions-of-pi or degrees) toggled at run
#     time.
#
# The imaginary unit is shown as "i" (math convention); internally
# Python uses "j". On a non-CAS calculator or a PC the program is
# still fully functional (numeric + snap output).
#
#     python eulerform.py            (interactive)
#     python test_eulerform.py       (self-test)

import math


def is_integer(x):
    """Check if float x is an integer value, compatible with MicroPython."""
    return abs(x - round(x)) < 1e-9


try:
    from ti_system import writeST, readST, recall_value
    HAS_TI = True
except ImportError:
    HAS_TI = False

# Display symbols. Auto-switch: ASCII on calculator, Unicode on desktop.
if HAS_TI:
    # Calculator: ASCII-safe characters
    SQRT = "sqrt"
    SYMPI = "pi"
    DOT = "*"
    I_UNIT = "i"
else:
    # Desktop: pretty Unicode
    SQRT = "\u221A"      # sqrt sign
    SYMPI = "\u03C0"     # pi sign
    DOT = "\u00B7"       # multiplication dot
    I_UNIT = "i"         # imaginary unit as shown to the user

ANGLE_MODE = "RAD"   # "RAD" = radians (fractions of pi), "DEG" = degrees
EXACT_MODE = HAS_TI  # CAS-exact display: on by default only on the device

# ==========================================================================
#  CAS bridge (vendored from the public-domain TI-Planet eval_expr trick)
# ==========================================================================

def _try_cas(expr):
    """Evaluate a TI-Basic expression on the device CAS and return its
    exact string, or None if unavailable/failed."""
    if not HAS_TI or not EXACT_MODE:
        return None
    try:
        writeST("pyzz_", "string(" + expr + ")")
    except Exception:
        return None
    try:
        s = str(readST("pyzz_"))
    except Exception:
        return None
    s = s.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    s = s.replace("$%$", "/")
    if s == "" or len(s) > 40:
        return None
    return s


def _is_plain_number(s):
    """True when a CAS result is just a plain number (nothing symbolic)."""
    if s is None:
        return True
    try:
        float(s)
        return True
    except Exception:
        return False


def _cas_number(v):
    """A clean numeric token for a CAS expression."""
    x = float(v)
    if is_integer(x):
        return str(int(x))
    return repr(x)


def cas_modulus(re, im):
    """Exact |re + i*im| via CAS when both parts are integers."""
    if not (is_integer(float(re)) and is_integer(float(im))):
        return None
    return _try_cas("sqrt(" + str(int(re)) + "^2+" + str(int(im)) + "^2)")


def cas_angle(re, im):
    """Exact arg(re + i*im) via CAS, but only when it is a nice pi
    multiple (otherwise None so the numeric angle is shown)."""
    if not (is_integer(float(re)) and is_integer(float(im))):
        return None
    s = _try_cas("atan2(" + str(int(im)) + "," + str(int(re)) + ")")
    if s and SYMPI in s:
        return s
    return None


class Quit(Exception):
    """Raised when the user types q to leave the program (main menu only)."""
    pass


class Return(Exception):
    """Raised when the user types q to return to parent menu (submenus)."""
    pass


class Cplx:
    """A complex number stored in rectangular form, with full algebra.
    Optional _rexs/_imxs hold exact (CAS) strings for display."""

    def __init__(self, re, im):
        self.re = float(re)
        self.im = float(im)
        self._rexs = None
        self._imxs = None

    @staticmethod
    def from_polar(r, theta):
        return Cplx(r * math.cos(theta), r * math.sin(theta))

    def mod(self):
        return math.hypot(self.re, self.im)

    def arg(self):
        return math.atan2(self.im, self.re)

    def conjugate(self):
        return Cplx(self.re, -self.im)

    def __add__(self, o):
        return Cplx(self.re + o.re, self.im + o.im)

    def __sub__(self, o):
        return Cplx(self.re - o.re, self.im - o.im)

    def __mul__(self, o):
        return Cplx(self.re * o.re - self.im * o.im,
                    self.re * o.im + self.im * o.re)

    def __truediv__(self, o):
        den = o.re * o.re + o.im * o.im
        if den < 1e-300:
            raise ValueError("division by zero")
        return Cplx((self.re * o.re + self.im * o.im) / den,
                    (self.im * o.re - self.re * o.im) / den)

    def __neg__(self):
        return Cplx(-self.re, -self.im)

    def power(self, n):
        """z**n by De Moivre (n any real number)."""
        r = self.mod()
        if r == 0.0 and n < 0:
            raise ValueError("0 raised to a negative power")
        rr = r ** n
        th = self.arg()
        return Cplx(rr * math.cos(n * th), rr * math.sin(n * th))

    def roots(self, n):
        """All n-th roots of z (De Moivre)."""
        if n < 1:
            raise ValueError("n must be >= 1")
        r = self.mod() ** (1.0 / n)
        th = self.arg()
        return [Cplx.from_polar(r, (th + 2 * math.pi * k) / n)
                for k in range(n)]


# ==========================================================================
#  Display helpers
# ==========================================================================

def _gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a


def fmt_num(x):
    """Plain decimal string, cleaned of trailing noise."""
    if abs(x) < 1e-9:
        return "0"
    r = round(x, 6)
    if abs(r - round(r)) < 1e-9:
        return str(int(round(r)))
    s = ("%.6f" % r).rstrip("0").rstrip(".")
    if s == "-0" or s == "":
        return "0"
    return s


RADICALS = (2, 3, 5, 6, 7, 10, 11, 13)


def _rad_label(k, n, d):
    s = ""
    if k != 1:
        s += str(k)
    s += SQRT + str(n)
    if d != 1:
        s += "/" + str(d)
    return s


def _frac_label(k, d):
    g = _gcd(k, d)
    k //= g
    d //= g
    if k == 0:
        return "0"
    if d == 1:
        return str(k)
    return str(k) + "/" + str(d)


def snap_value(v):
    """Return an exact-looking string if v is close to a simple fraction
    or radical, otherwise a decimal. Used for moduli and trig parts."""
    if abs(v) < 1e-9:
        return "0"
    sign = ""
    a = v
    if v < 0:
        sign = "-"
        a = -v
    for d in range(1, 13):
        for k in range(0, 41):
            c = k / float(d)
            if abs(a - c) < 1e-5:
                label = _frac_label(k, d)
                if label == "0":
                    return "0"
                return sign + label
    for n in RADICALS:
        sn = math.sqrt(n)
        for d in range(1, 4):
            for k in range(1, 8):
                c = k * sn / float(d)
                if abs(a - c) < 1e-5:
                    return sign + _rad_label(k, n, d)
    return fmt_num(v)


def fmt_angle(theta):
    """Render an angle in radians as a fraction of pi when possible."""
    ratio = theta / math.pi
    for d in range(1, 13):
        k = int(round(ratio * d))
        if abs(ratio - k / float(d)) < 1e-5:
            g = _gcd(k, d)
            num = k // g
            den = d // g
            if num == 0:
                return "0"
            if den == 1:
                if num == 1:
                    return SYMPI
                if num == -1:
                    return "-" + SYMPI
                return str(num) + SYMPI
            if abs(num) == 1:
                if num == 1:
                    return SYMPI + "/" + str(den)
                return "-" + SYMPI + "/" + str(den)
            return str(num) + SYMPI + "/" + str(den)
    return fmt_num(theta) + " rad"


def fmt_angle_deg(theta):
    deg = theta * 180.0 / math.pi
    r = round(deg, 6)
    if abs(r - round(r)) < 1e-5:
        return str(int(round(r))) + " deg"
    return fmt_num(deg) + " deg"


def _rat(num, den):
    """Reduced integer ratio string, e.g. _rat(4,3) -> '4/3'."""
    g = _gcd(num, den)
    n = num // g
    d = den // g
    if d == 1:
        return str(n)
    return str(n) + "/" + str(d)


def _atan_symbolic(re, im):
    """Exact quadrant-aware arg(re + i*im) as an atan expression.
    Only meaningful when re and im are integers."""
    R = int(round(re))
    I = int(round(im))
    if R == 0 and I == 0:
        return "0"
    if R > 0:
        return "atan(" + _rat(I, R) + ")"
    if I > 0:
        return SYMPI + " - atan(" + _rat(I, -R) + ")"
    if I < 0:
        return "-" + SYMPI + " + atan(" + _rat(-I, -R) + ")"
    return SYMPI


def symbolic_angle(re, im, th):
    """Exact angle string: a fraction of pi when the angle is a nice
    multiple of pi; otherwise a symbolic atan(b/a) when the real and
    imaginary parts are integers; otherwise a decimal label."""
    frac = fmt_angle(th)
    if not frac.endswith(" rad"):
        return frac
    if abs(re - round(re)) < 1e-9 and abs(im - round(im)) < 1e-9:
        a = _atan_symbolic(re, im)
        if a:
            return a
    return frac


def fmt_mod(z):
    """Modulus string: CAS-exact when possible, else snapped."""
    if EXACT_MODE:
        m = cas_modulus(z.re, z.im)
        if m:
            return m
    return snap_value(z.mod())


def fmt_ang(z):
    """Argument string: CAS exact when possible, else a symbolic
    fraction of pi / atan expression, else a numeric label."""
    if EXACT_MODE and ANGLE_MODE == "RAD":
        a = cas_angle(z.re, z.im)
        if a:
            return a
    if ANGLE_MODE == "DEG":
        return fmt_angle_deg(z.arg())
    return symbolic_angle(z.re, z.im, z.arg())


def fmt_rect(z):
    re_s = z._rexs if z._rexs is not None else snap_value(z.re)
    im_s = z._imxs if z._imxs is not None else snap_value(z.im)
    if im_s == "0":
        return re_s
    if re_s == "0":
        if im_s.startswith("-"):
            return "-" + im_s[1:] + I_UNIT
        return im_s + I_UNIT
    if im_s.startswith("-"):
        return re_s + " - " + im_s[1:] + I_UNIT
    return re_s + " + " + im_s + I_UNIT


def fmt_trig(z):
    th = fmt_ang(z)
    return (fmt_mod(z) + " " + DOT + " (cos " + th + " + "
            + I_UNIT + " " + DOT + " sin " + th + ")")


def fmt_exp(z):
    th = fmt_ang(z)
    return (fmt_mod(z) + " " + DOT + " e^(" + I_UNIT + " " + DOT
            + " " + th + ")")


ANS = Cplx(0, 0)


def show(z):
    global ANS
    ANS = z
    print("z = " + fmt_rect(z))
    print("|z| = " + fmt_mod(z) + "   arg = " + fmt_ang(z))
    print("trig  " + fmt_trig(z))
    print("exp   " + fmt_exp(z))


# ==========================================================================
#  Input helpers
# ==========================================================================

def get_num(prompt, allow_quit=False):
    while True:
        s = input(prompt).strip()
        if s.lower() == "q":
            if allow_quit:
                raise Quit()
            raise Return()
        try:
            return float(s)
        except Exception:
            print("Enter a valid number.")


def get_choice(prompt, lo, hi, allow_quit=False):
    while True:
        s = input(prompt).strip()
        if s.lower() == "q":
            if allow_quit:
                raise Quit()
            raise Return()
        try:
            v = int(s)
            if lo <= v <= hi:
                return v
        except Exception:
            pass
        print("Enter " + str(lo) + "-" + str(hi) + ".")


def get_theta(prompt, allow_quit=False):
    """Return (radians, exact_pi_frac) where exact_pi_frac is a TI-Basic
    pi-fraction string (or None if the angle was a plain decimal)."""
    if ANGLE_MODE == "DEG":
        d = get_num(prompt + " (degrees): ", allow_quit)
        return d * math.pi / 180.0, (SYMPI + "*" + _cas_number(d) + "/180")
    print(prompt + ": fraction of pi (e.g. 1/4 = pi/4) or decimal radians")
    while True:
        s = input("  theta: ").strip()
        if s.lower() == "q":
            if allow_quit:
                raise Quit()
            raise Return()
        try:
            if "/" in s:
                parts = s.split("/")
                if len(parts) == 2:
                    n = float(parts[0])
                    d = float(parts[1])
                    return (n / d) * math.pi, (
                        SYMPI + "*" + _cas_number(n) + "/" + _cas_number(d))
            else:
                return float(s), None
        except Exception:
            pass
        print("Enter a valid number or fraction.")


def input_cplx(prompt):
    print(prompt)
    print("  1 rectangular (a + b" + I_UNIT + ")")
    print("  2 polar (r, theta)")
    print("  3 exponential r*e^(i*theta)")
    c = get_choice("  choice: ", 1, 3, False)
    if c == 1:
        re = get_num("  real part a: ", False)
        im = get_num("  imaginary part b: ", False)
        return Cplx(re, im)
    r = get_num("  modulus r: ", False)
    th, thx = get_theta("  argument", False)
    z = Cplx.from_polar(r, th)
    if thx is not None and is_integer(float(r)) and EXACT_MODE:
        r_s = str(int(r))
        re = _try_cas("cos(" + thx + ")*" + r_s)
        im = _try_cas("sin(" + thx + ")*" + r_s)
        if re and not _is_plain_number(re):
            z._rexs = re
        if im and not _is_plain_number(im):
            z._imxs = im
    return z


# ==========================================================================
#  Menus
# ==========================================================================

def menu_convert():
    z = input_cplx("Enter a number:")
    print("")
    show(z)
    input("Press Enter to continue...")


def menu_arithmetic():
    z1 = input_cplx("First number:")
    z2 = input_cplx("Second number:")
    print("operation:  1 +    2 -    3 *    4 /")
    op = get_choice("  choice: ", 1, 4, False)
    if op == 1:
        r = z1 + z2
    elif op == 2:
        r = z1 - z2
    elif op == 3:
        r = z1 * z2
    else:
        r = z1 / z2
    print("")
    show(r)
    input("Press Enter to continue...")


def menu_powers():
    z = input_cplx("Enter a number:")
    print("  1 raise to power z^n (De Moivre)")
    print("  2 find the n-th roots")
    c = get_choice("  choice: ", 1, 2, False)
    if c == 1:
        n = get_num("  exponent n: ", False)
        print("")
        show(z.power(n))
        input("Press Enter to continue...")
    else:
        nv = get_num("  n (positive integer): ", False)
        if nv < 1 or not is_integer(nv):
            raise ValueError("n must be a positive integer")
        n = int(nv)
        rs = z.roots(n)
        print(str(n) + " roots:")
        for r in rs:
            print("    " + fmt_rect(r) + "   | " + fmt_trig(r))
        input("Press Enter to continue...")


def menu_metrics():
    z = input_cplx("Enter a number:")
    print("")
    print("|z|       = " + fmt_mod(z))
    print("arg(z)    = " + fmt_ang(z))
    print("conjugate = " + fmt_rect(z.conjugate()))
    input("Press Enter to continue...")


def menu_toggle_angle():
    global ANGLE_MODE
    if ANGLE_MODE == "RAD":
        ANGLE_MODE = "DEG"
    else:
        ANGLE_MODE = "RAD"
    print("angle mode is now " + ANGLE_MODE)


def menu_toggle_exact():
    global EXACT_MODE
    EXACT_MODE = not EXACT_MODE
    print("exact (CAS) mode is now " + ("ON" if EXACT_MODE else "OFF"))


# ==========================================================================

def main():
    print("EULERFORM")
    print("angle mode: " + ANGLE_MODE
          + "   exact(CAS): " + ("ON" if EXACT_MODE else "OFF"))
    print("type q at any prompt to quit (main menu: exit program; submenus: return)")
    running = True
    while running:
        print("")
        print("MAIN MENU")
        print("  1 convert forms (Euler)")
        print("  2 arithmetic (+  -  *  /)")
        print("  3 powers and roots")
        print("  4 modulus / argument / conjugate")
        print("  5 toggle angle mode (RAD/DEG)")
        print("  6 toggle exact (CAS) display")
        print("  q quit")
        try:
            c = get_choice("  choice: ", 1, 6, True)
        except Quit:
            break
        except Return:
            continue
        try:
            if c == 1:
                menu_convert()
            elif c == 2:
                menu_arithmetic()
            elif c == 3:
                menu_powers()
            elif c == 4:
                menu_metrics()
            elif c == 5:
                menu_toggle_angle()
            else:
                menu_toggle_exact()
        except Return:
            continue
        except Quit:
            running = False
        except Exception as e:
            print("error: " + str(e))
    print("done")


if __name__ == "__main__" or HAS_TI:
    try:
        main()
    except Exception as e:
        print("FATAL ERROR: " + str(e))
        try:
            input("Press Enter to exit...")
        except Exception:
            pass