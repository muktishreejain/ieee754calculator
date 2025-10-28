"""
Module: convert.py

Handles conversion between decimal and IEEE-754 32-bit and 64-bit binary representation.
"""

import struct

def float_to_ieee754(num: float) -> str:
    bits = struct.unpack('!I', struct.pack('!f', num))[0]
    return f"{bits:032b}"

def ieee754_to_float(binary: str) -> float:
    bits = int(binary, 2)
    return struct.unpack('!f', struct.pack('!I', bits))[0]

# --- NEW FUNCTIONS for 64-bit ---
def float_to_ieee754_64(num: float) -> str:
    bits = struct.unpack('!Q', struct.pack('!d', num))[0]
    return f"{bits:064b}"

def ieee754_to_float_64(binary: str) -> float:
    bits = int(binary, 2)
    return struct.unpack('!d', struct.pack('!Q', bits))[0]
