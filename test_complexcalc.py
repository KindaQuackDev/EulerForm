# Self-test for complexcalc. Run on the desktop:
#     python test_complexcalc.py
# Exercises the pure-math engine, the exact-pi/radical renderer, and the
# CAS-exact fallbacks (with HAS_TI False, the CAS layer must never run
# and every display path degrades to snapping / numerics).

import math
import complexcalc as cc


def check(cond, msg):
    if not cond:
        raise AssertionError("FAIL: " + msg)


# --- Euler identity: e^(i*pi) = -1
z = cc.Cplx.from_polar(1, math.pi)
check(abs(z.re - -1.0) < 1e-9 and abs(z.im) < 1e-9, "e^(i*pi) value")
check(cc.fmt_rect(z) == "-1", "e^(i*pi) rect")

# --- e^(i*pi/4) = sqrt(2)/2 + sqrt(2)/2 i
z = cc.Cplx.from_polar(1, math.pi / 4)
check(cc.fmt_rect(z) == "\u221A2/2 + \u221A2/2i", "pi/4 rect")

# --- angle rendering (radians as fractions of pi)
check(cc.fmt_angle(0.0) == "0", "angle 0")
check(cc.fmt_angle(math.pi) == "\u03C0", "angle pi")
check(cc.fmt_angle(-math.pi) == "-\u03C0", "angle -pi")
check(cc.fmt_angle(math.pi / 2) == "\u03C0/2", "angle pi/2")
check(cc.fmt_angle(3 * math.pi / 2) == "3\u03C0/2", "angle 3pi/2")
check(cc.fmt_angle(7 * math.pi / 6) == "7\u03C0/6", "angle 7pi/6")
check(cc.fmt_angle(2 * math.pi) == "2\u03C0", "angle 2pi")
check(cc.fmt_angle(math.pi / 6) == "\u03C0/6", "angle pi/6")

# --- degrees mode
cc.ANGLE_MODE = "DEG"
check(cc.fmt_angle_deg(math.pi / 4) == "45 deg", "deg 45")
check(cc.fmt_ang(cc.Cplx(-1, 0)) == "180 deg", "deg 180")
cc.ANGLE_MODE = "RAD"

# --- arithmetic
a = cc.Cplx(3, 4)
b = cc.Cplx(1, -2)
check(cc.fmt_rect(a + b) == "4 + 2i", "add")
check(cc.fmt_rect(a - b) == "2 + 6i", "sub")
check(cc.fmt_rect(a * b) == "11 - 2i", "mul")
check(cc.fmt_rect(a / b) == "-1 + 2i", "div")

# --- division by zero
try:
    a / cc.Cplx(0, 0)
    check(False, "div zero should raise")
except ValueError:
    pass

# --- powers (De Moivre)
z = cc.Cplx(1, 1)  # sqrt(2) * e^(i*pi/4)
check(cc.fmt_rect(z.power(2)) == "2i", "square of 1+i")
check(cc.fmt_rect(z.power(-1)) == "1/2 - 1/2i", "inverse of 1+i")

# --- roots of unity z^3 = 1
rs = cc.Cplx(1, 0).roots(3)
check(len(rs) == 3, "root count")
check(cc.fmt_rect(rs[0]) == "1", "root 0")
check(cc.fmt_rect(rs[1]) == "-1/2 + \u221A3/2i", "root 1")
check(cc.fmt_rect(rs[2]) == "-1/2 - \u221A3/2i", "root 2")

# --- modulus / argument / conjugate
z = cc.Cplx(1, 1)
check(cc.snap_value(z.mod()) == "\u221A2", "mod sqrt2")
check(cc.fmt_angle(z.arg()) == "\u03C0/4", "arg pi/4")
check(cc.fmt_rect(z.conjugate()) == "1 - 1i", "conj")

# --- trig / exp rendering (Euler forms)
z = cc.Cplx.from_polar(2, math.pi / 3)
check(cc.fmt_trig(z) == "2 \u00B7 (cos \u03C0/3 + i \u00B7 sin \u03C0/3)",
      "trig render")
check(cc.fmt_exp(z) == "2 \u00B7 e^(i \u00B7 \u03C0/3)", "exp render")
check(cc.fmt_rect(z) == "1 + \u221A3i", "polar to rect")

# --- radical / fraction snapping
check(cc.snap_value(0.5) == "1/2", "snap 1/2")
check(cc.snap_value(-0.5) == "-1/2", "snap -1/2")
check(cc.snap_value(math.sqrt(3)) == "\u221A3", "snap sqrt3")
check(cc.snap_value(math.sqrt(2) / 2) == "\u221A2/2", "snap sqrt2/2")
check(cc.snap_value(2.0) == "2", "snap int")
check(cc.snap_value(0.0) == "0", "snap zero")
check(cc.snap_value(-0.0) == "0", "snap -0.0")

# ==========================================================================
#  CAS-exact layer: with HAS_TI False the CAS path must stay inert and
#  every exact helper degrade to the numeric/snap result.
# ==========================================================================

saved_ti = cc.HAS_TI
saved_exact = cc.EXACT_MODE
cc.HAS_TI = False
cc.EXACT_MODE = True  # simulate a CAS wanting exact, but no bridge present

check(cc._try_cas("sqrt(1+1)") is None, "no-CAS _try_cas is None")
check(cc.cas_modulus(1, 1) is None, "no-CAS cas_modulus is None")
check(cc.cas_angle(1, 1) is None, "no-CAS cas_angle is None")

z = cc.Cplx(3, 4)
check(cc.fmt_mod(z) == "5", "fmt_mod fallback (|3+4i| = 5)")
check(cc.fmt_ang(z) == "atan(4/3)", "fmt_ang symbolic atan (3+4i)")
z = cc.Cplx(1, 1)
check(cc.fmt_mod(z) == "\u221A2", "fmt_mod fallback sqrt2")
check(cc.fmt_ang(z) == "\u03C0/4", "fmt_ang fallback pi/4")

# --- symbolic angle rendering (pure Python, all quadrants)
check(cc.fmt_ang(cc.Cplx(2, 3)) == "atan(3/2)", "arg atan(3/2)")
check(cc.fmt_ang(cc.Cplx(1, 5)) == "atan(5)", "arg atan(5)")
check(cc.fmt_ang(cc.Cplx(3, -4)) == "atan(-4/3)", "arg Q4")
check(cc.fmt_ang(cc.Cplx(-3, 4)) == "\u03C0 - atan(4/3)", "arg Q2")
check(cc.fmt_ang(cc.Cplx(-3, -4)) == "-\u03C0 + atan(4/3)", "arg Q3")
check(cc.fmt_exp(cc.Cplx(3, 4)) == "5 \u00B7 e^(i \u00B7 atan(4/3))",
      "exp symbolic atan")

# stored exact strings are used by fmt_rect when present
z = cc.Cplx(1, 1)
z._rexs = "\u221A2"
z._imxs = "\u221A2"
check(cc.fmt_rect(z) == "\u221A2 + \u221A2i", "exact rect reuse")

# get_theta fraction parsing -> exact pi-fraction spec (no CAS needed)
cc.EXACT_MODE = saved_exact
check(cc._cas_number(2.0) == "2", "_cas_number int")
check(cc._cas_number(1.5) == "1.5", "_cas_number float")
check(cc._is_plain_number("5") is True, "plain number detected")
check(cc._is_plain_number("\u221A2") is False, "radical not plain")
check(cc._is_plain_number("1/2") is False, "fraction not plain")
check(cc._is_plain_number(None) is True, "None treated plain")

# --- simulated CAS: monkeypatch the bridge and verify exact rendering
cc.HAS_TI = True
cc.EXACT_MODE = True
calls = []


def fake_cas(expr):
    calls.append(expr)
    if "atan2" in expr:
        return "\u03C0/4"
    if expr.startswith("sqrt"):
        return "\u221A(2)"
    if "cos" in expr:
        return "\u221A2/2"
    if "sin" in expr:
        return "\u221A2/2"
    return None


cc._try_cas = fake_cas

z = cc.Cplx(1, 1)
check(cc.fmt_mod(z) == "\u221A(2)", "sim CAS modulus")
check(cc.fmt_ang(z) == "\u03C0/4", "sim CAS angle")
check(cc.fmt_trig(z).count("1/2") >= 0, "sim CAS trig no crash")
check(len(calls) >= 2, "sim CAS was called")

# restore for a clean module state
cc.HAS_TI = saved_ti
cc.EXACT_MODE = saved_exact
calls[:] = []

print("ALL TESTS PASSED")