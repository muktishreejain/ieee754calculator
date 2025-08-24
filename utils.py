"""
Module: utils.py
Helper functions for bit manipulations, shifts, etc.
"""

def shift_right(binary: str, n: int) -> str:
    return ("0" * n + binary)[:len(binary)]

def shift_left(binary: str, n: int) -> str:
    return (binary[n:] + "0" * n)[:len(binary)]
