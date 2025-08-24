"""
Main driver script to demonstrate IEEE-754 conversion and operations.
"""

from convert import float_to_ieee754, ieee754_to_float
from ops import add_floats, multiply_floats, add_ieee754, multiply_ieee754

def main():
    print("IEEE 754 Calculator (32-bit)")
    a = float(input("Enter first number: "))
    b = float(input("Enter second number: "))

    a_bin = float_to_ieee754(a)
    b_bin = float_to_ieee754(b)

    print(f"Binary of {a}: {a_bin}")
    print(f"Binary of {b}: {b_bin}")

    sum_result = add_ieee754(a_bin, b_bin)
    mul_result = multiply_ieee754(a_bin, b_bin)

    print(f"Addition Result (binary): {sum_result}")
    print(f"Addition Result (float): {ieee754_to_float(sum_result)}")

    print(f"Multiplication Result (binary): {mul_result}")
    print(f"Multiplication Result (float): {ieee754_to_float(mul_result)}")

if __name__ == "__main__":
    main()