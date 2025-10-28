"""
Main driver script to demonstrate IEEE-754 conversion and operations.
"""

from convert import float_to_ieee754, ieee754_to_float, float_to_ieee754_64, ieee754_to_float_64
from ops import add_floats, multiply_floats, add_ieee754, multiply_ieee754, add_floats_64, multiply_floats_64, add_ieee754_64, multiply_ieee754_64

def main():
    precision = input("Enter precision (32 or 64): ")
    a = float(input("Enter first number: "))
    b = float(input("Enter second number: "))
    if precision == "32":
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
    else:
        a_bin = float_to_ieee754_64(a)
        b_bin = float_to_ieee754_64(b)
        print(f"Binary of {a}: {a_bin}")
        print(f"Binary of {b}: {b_bin}")
        sum_result = add_ieee754_64(a_bin, b_bin)
        mul_result = multiply_ieee754_64(a_bin, b_bin)
        print(f"Addition Result (binary): {sum_result}")
        print(f"Addition Result (float): {ieee754_to_float_64(sum_result)}")
        print(f"Multiplication Result (binary): {mul_result}")
        print(f"Multiplication Result (float): {ieee754_to_float_64(mul_result)}")

if __name__ == "__main__":
    main()
