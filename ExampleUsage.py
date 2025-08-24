# example_usage.py
"""
Example usage of the IEEE-754 library
This demonstrates the main API functions for GUI integration
"""

from ieee754_core import to_ieee754, from_ieee754, fp_add, fp_mul

def demo_conversion():
    """Demonstrate decimal to IEEE-754 conversion"""
    print("=== IEEE-754 Conversion Demo ===")
    
    # Convert decimal to IEEE-754
    values = [1.0, -1.5, 0.1, float('inf'), float('-inf'), float('nan')]
    
    for value in values:
        result = to_ieee754(value, 'single')
        print(f"\nValue: {value}")
        print(f"Classification: {result['classification']}")
        print(f"Hex: {result['fields']['hex']}")
        print(f"Binary: {result['fields']['binary']}")
        print(f"Sign|Exponent|Mantissa: {result['fields']['sign_bit']}|{result['fields']['exponent_bits']}|{result['fields']['fraction_bits']}")
        
        if 'breakdown' in result:
            print(f"Formula: {result['breakdown']['formula']}")

def demo_decoding():
    """Demonstrate IEEE-754 to decimal conversion"""
    print("\n=== IEEE-754 Decoding Demo ===")
    
    # Some known IEEE-754 bit patterns
    test_cases = [
        (0x3F800000, 'single', '1.0'),
        (0x40000000, 'single', '2.0'),
        (0xC0000000, 'single', '-2.0'),
        (0x7F800000, 'single', '+infinity'),
        (0xFF800000, 'single', '-infinity'),
        (0x7FC00000, 'single', 'NaN'),
    ]
    
    for bits, precision, description in test_cases:
        result = from_ieee754(bits, precision)
        print(f"\nBits: 0x{bits:08X} ({description})")
        print(f"Value: {result['value']}")
        print(f"Classification: {result['classification']}")
        if 'breakdown' in result:
            print(f"Explanation: {result['breakdown']['formula']}")

def demo_arithmetic():
    """Demonstrate IEEE-754 arithmetic operations"""
    print("\n=== IEEE-754 Arithmetic Demo ===")
    
    # Convert some values to IEEE-754 format first
    a_val = 1.5
    b_val = 2.5
    
    a_ieee = to_ieee754(a_val, 'single')
    b_ieee = to_ieee754(b_val, 'single')
    
    a_bits = a_ieee['fields']['bits']
    b_bits = b_ieee['fields']['bits']
    
    print(f"A = {a_val} → 0x{a_bits:08X}")
    print(f"B = {b_val} → 0x{b_bits:08X}")
    
    # Addition
    add_result = fp_add(a_bits, b_bits, 'single')
    print(f"\nAddition: {a_val} + {b_val}")
    print(f"Expected: {a_val + b_val}")
    print(f"IEEE-754 Result: {add_result['result']['value']}")
    print(f"Result Hex: {add_result['result']['fields']['hex']}")
    print(f"Exact Match: {add_result['verification']['exact_match']}")
    
    # Multiplication  
    mul_result = fp_mul(a_bits, b_bits, 'single')
    print(f"\nMultiplication: {a_val} × {b_val}")
    print(f"Expected: {a_val * b_val}")
    print(f"IEEE-754 Result: {mul_result['result']['value']}")
    print(f"Result Hex: {mul_result['result']['fields']['hex']}")
    print(f"Exact Match: {mul_result['verification']['exact_match']}")

def demo_precision_comparison():
    """Compare single vs double precision"""
    print("\n=== Precision Comparison Demo ===")
    
    value = 0.1  # This has interesting representation in IEEE-754
    
    single_result = to_ieee754(value, 'single')
    double_result = to_ieee754(value, 'double')
    
    print(f"Value: {value}")
    print(f"Single precision: {single_result['value']}")
    print(f"Single hex: {single_result['fields']['hex']}")
    print(f"Double precision: {double_result['value']}")
    print(f"Double hex: {double_result['fields']['hex']}")
    
    print(f"\nDifference from original:")
    print(f"Single error: {abs(single_result['value'] - value)}")
    print(f"Double error: {abs(double_result['value'] - value)}")

def demo_educational_breakdown():
    """Show detailed educational breakdown"""
    print("\n=== Educational Breakdown Demo ===")
    
    value = 6.5
    result = to_ieee754(value, 'single')
    
    print(f"Converting {value} to IEEE-754 single precision:")
    print(f"Result: {result['fields']['hex']}")
    print(f"Binary: {result['fields']['binary']}")
    print()
    
    breakdown = result['breakdown']
    print("Step-by-step breakdown:")
    print(f"1. {breakdown['sign_explanation']}")
    print(f"2. {breakdown['exponent_explanation']}")
    print(f"3. {breakdown['mantissa_explanation']}")
    print(f"4. Formula: {breakdown['formula']}")
    print(f"5. Calculation: {breakdown['calculation']}")
    
    if 'encoding_steps' in result:
        steps = result['encoding_steps']
        print(f"\nEncoding details:")
        print(f"Binary exponent: {steps['binary_exponent']}")
        print(f"Significand: {steps['significand']}")
        print(f"Biased exponent: {steps['biased_exponent']}")

if __name__ == "__main__":
    demo_conversion()
    demo_decoding()
    demo_arithmetic()
    demo_precision_comparison()
    demo_educational_breakdown()
    
    print("\n=== API Summary ===")
    print("Main functions for GUI integration:")
    print("• to_ieee754(value, precision) - Convert decimal to IEEE-754")
    print("• from_ieee754(bits, precision) - Convert IEEE-754 to decimal") 
    print("• fp_add(a_bits, b_bits, precision, rounding) - Add two IEEE-754 numbers")
    print("• fp_mul(a_bits, b_bits, precision, rounding) - Multiply two IEEE-754 numbers")
    print("\nSupported precisions: 'single' (32-bit), 'double' (64-bit)")
    print("Each function returns detailed breakdown for educational visualization")