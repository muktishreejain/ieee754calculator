"""
Module: convert.py
Handles conversion between decimal and IEEE-754 32-bit binary representation.
"""

import struct

def float_to_ieee754(num: float) -> str:
    bits = struct.unpack('!I', struct.pack('!f', num))[0]
    return f"{bits:032b}"

def ieee754_to_float(binary: str) -> float:
    bits = int(binary, 2)
    return struct.unpack('!f', struct.pack('!I', bits))[0]
