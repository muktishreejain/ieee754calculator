"""
Module: ops.py

Performs IEEE-754 style addition and multiplication on 32/64-bit floats.
"""

from convert import float_to_ieee754, ieee754_to_float, \
                    float_to_ieee754_64, ieee754_to_float_64

def add_floats(a: float, b: float) -> float:
    return a + b

def multiply_floats(a: float, b: float) -> float:
    return a * b

def add_ieee754(bin_a: str, bin_b: str) -> str:
    a = ieee754_to_float(bin_a)
    b = ieee754_to_float(bin_b)
    return float_to_ieee754(a + b)

def multiply_ieee754(bin_a: str, bin_b: str) -> str:
    a = ieee754_to_float(bin_a)
    b = ieee754_to_float(bin_b)
    return float_to_ieee754(a * b)

# --- NEW 64-bit functions ---
def add_floats_64(a: float, b: float) -> float:
    return a + b

def multiply_floats_64(a: float, b: float) -> float:
    return a * b

def add_ieee754_64(bin_a: str, bin_b: str) -> str:
    a = ieee754_to_float_64(bin_a)
    b = ieee754_to_float_64(bin_b)
    return float_to_ieee754_64(a + b)

def multiply_ieee754_64(bin_a: str, bin_b: str) -> str:
    a = ieee754_to_float_64(bin_a)
    b = ieee754_to_float_64(bin_b)
    return float_to_ieee754_64(a * b)
