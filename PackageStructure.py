# ieee754_core/ package structure

# ieee754_core/__init__.py
"""
IEEE-754 Floating Point Library
Main API for GUI integration
"""

from .convert import to_ieee754, from_ieee754
from .ops import fp_add, fp_mul
from .pack import IEEE754Config

__all__ = ['to_ieee754', 'from_ieee754', 'fp_add', 'fp_mul', 'IEEE754Config']

__version__ = '1.0.0'