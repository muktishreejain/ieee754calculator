# ieee754_core/convert.py
"""
Conversion between decimal values and IEEE-754 representation
"""

import math
from typing import Union, Dict, Any
from fractions import Fraction
from .pack import IEEE754Config, get_config, pack_ieee754, unpack_ieee754, format_bits, round_to_nearest_even

def to_ieee754(value: Union[float, int, str], precision: str = 'single') -> Dict[str, Any]:
    """
    Convert decimal value to IEEE-754 representation
    
    Args:
        value: Input value (float, int, or string like "3.14")
        precision: 'single', 'double', 'half', or 'quad'
    
    Returns:
        Dictionary with fields, bit representations, and metadata
    """
    config = get_config(precision)
    
    # Convert input to float
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return _create_nan_result(config, f"Invalid input: {value}")
    
    # Handle special cases first
    if math.isnan(value):
        return _create_nan_result(config, "NaN")
    
    if math.isinf(value):
        return _create_inf_result(config, value > 0)
    
    if value == 0.0:
        return _create_zero_result(config, math.copysign(1.0, value) > 0)
    
    # Extract sign and work with magnitude
    sign = 0 if value >= 0 else 1
    magnitude = abs(value)
    
    # Convert to binary representation
    return _encode_normal_number(magnitude, sign, config)

def from_ieee754(bits: Union[int, str], precision: str = 'single') -> Dict[str, Any]:
    """
    Convert IEEE-754 bits to decimal value with detailed breakdown
    
    Args:
        bits: IEEE-754 bits as int, binary string, or hex string
        precision: 'single', 'double', 'half', or 'quad'
    
    Returns:
        Dictionary with value, classification, and field breakdown
    """
    config = get_config(precision)
    
    try:
        sign, exponent, mantissa = unpack_ieee754(bits, config)
    except ValueError as e:
        return {'error': str(e), 'value': None}
    
    # Format for display
    bit_format = format_bits(pack_ieee754(sign, exponent, mantissa, config), config)
    
    # Classify and compute value
    classification = _classify_ieee754(exponent, mantissa, config)
    value = _compute_value(sign, exponent, mantissa, config, classification)
    
    # Create detailed breakdown
    result = {
        'value': value,
        'classification': classification,
        'sign': sign,
        'exponent_raw': exponent,
        'mantissa_raw': mantissa,
        'fields': bit_format,
        'breakdown': _create_breakdown(sign, exponent, mantissa, config, classification, value)
    }
    
    return result

def _encode_normal_number(magnitude: float, sign: int, config: IEEE754Config) -> Dict[str, Any]:
    """Encode a normal (non-special) number"""
    
    # Find the binary representation
    if magnitude == 0:
        return _create_zero_result(config, sign == 0)
    
    # Get the binary exponent and mantissa
    # We'll use fractions for exact arithmetic
    frac = Fraction(magnitude).limit_denominator(1 << 60)  # Reasonable precision limit
    
    if frac == 0:
        return _create_zero_result(config, sign == 0)
    
    # Find the position of the most significant bit
    numerator = frac.numerator
    denominator = frac.denominator
    
    # Normalize: find the exponent such that 1 <= significand < 2
    # magnitude = significand * 2^exponent, where 1 <= significand < 2
    
    # Convert to binary scientific notation
    log2_mag = math.log2(float(magnitude))
    binary_exp = int(math.floor(log2_mag))
    
    # Calculate the significand: magnitude / 2^binary_exp
    significand = magnitude / (2 ** binary_exp)
    
    # Check for subnormal numbers
    min_exp = 1 - config.bias
    if binary_exp < min_exp:
        return _encode_subnormal(magnitude, sign, config)
    
    # Normal number encoding
    biased_exp = binary_exp + config.bias
    
    # Check for overflow (infinity)
    if biased_exp >= config.exp_max:
        return _create_inf_result(config, sign == 0)
    
    # Extract mantissa bits (remove implicit leading 1)
    mantissa_value = significand - 1.0  # Remove the implicit 1
    mantissa_scaled = mantissa_value * (1 << config.frac_bits)
    
    # Rounding
    mantissa_int = int(mantissa_scaled)
    fractional_part = mantissa_scaled - mantissa_int
    
    # Implement guard, round, and sticky bits for rounding
    guard_bit = 1 if fractional_part >= 0.5 else 0
    round_bit = 0  # Simplified - would need more precision for exact implementation
    sticky_bit = 1 if fractional_part > 0.5 else 0
    
    rounded_mantissa, overflow = round_to_nearest_even(
        mantissa_scaled, config.frac_bits, guard_bit, round_bit, sticky_bit
    )
    
    if overflow:
        biased_exp += 1
        if biased_exp >= config.exp_max:
            return _create_inf_result(config, sign == 0)
    
    # Pack the result
    bits = pack_ieee754(sign, biased_exp, rounded_mantissa, config)
    bit_format = format_bits(bits, config)
    
    # Verify the encoding by decoding
    decoded_value = _compute_value(sign, biased_exp, rounded_mantissa, config, 'normal')
    
    return {
        'value': float(decoded_value),
        'original_value': magnitude * (-1 if sign else 1),
        'classification': 'normal',
        'sign': sign,
        'exponent_raw': biased_exp,
        'exponent_unbiased': biased_exp - config.bias,
        'mantissa_raw': rounded_mantissa,
        'fields': bit_format,
        'breakdown': _create_breakdown(sign, biased_exp, rounded_mantissa, config, 'normal', decoded_value),
        'encoding_steps': {
            'binary_exponent': binary_exp,
            'significand': significand,
            'biased_exponent': biased_exp,
            'mantissa_before_rounding': mantissa_value,
            'mantissa_scaled': mantissa_scaled,
            'mantissa_rounded': rounded_mantissa,
            'overflow_occurred': overflow
        }
    }

def _encode_subnormal(magnitude: float, sign: int, config: IEEE754Config) -> Dict[str, Any]:
    """Encode a subnormal (denormalized) number"""
    min_normal = 2 ** (1 - config.bias)
    scaling_factor = 2 ** (config.frac_bits + config.bias - 1)
    
    mantissa_scaled = magnitude * scaling_factor
    mantissa_int = int(mantissa_scaled + 0.5)  # Simple rounding
    
    # Clamp to valid range
    mantissa_int = min(mantissa_int, config.frac_mask)
    
    if mantissa_int == 0:
        return _create_zero_result(config, sign == 0)
    
    bits = pack_ieee754(sign, 0, mantissa_int, config)
    bit_format = format_bits(bits, config)
    
    decoded_value = _compute_value(sign, 0, mantissa_int, config, 'subnormal')
    
    return {
        'value': float(decoded_value),
        'original_value': magnitude * (-1 if sign else 1),
        'classification': 'subnormal',
        'sign': sign,
        'exponent_raw': 0,
        'exponent_unbiased': 1 - config.bias,
        'mantissa_raw': mantissa_int,
        'fields': bit_format,
        'breakdown': _create_breakdown(sign, 0, mantissa_int, config, 'subnormal', decoded_value)
    }

def _classify_ieee754(exponent: int, mantissa: int, config: IEEE754Config) -> str:
    """Classify IEEE-754 number based on exponent and mantissa"""
    if exponent == config.exp_max:
        if mantissa == 0:
            return 'infinity'
        else:
            return 'nan'
    elif exponent == 0:
        if mantissa == 0:
            return 'zero'
        else:
            return 'subnormal'
    else:
        return 'normal'

def _compute_value(sign: int, exponent: int, mantissa: int, config: IEEE754Config, classification: str) -> float:
    """Compute the actual floating-point value"""
    if classification == 'zero':
        return -0.0 if sign else 0.0
    elif classification == 'infinity':
        return -math.inf if sign else math.inf
    elif classification == 'nan':
        return math.nan
    elif classification == 'subnormal':
        # Value = (-1)^sign * (mantissa / 2^frac_bits) * 2^(1-bias)
        significand = mantissa / (1 << config.frac_bits)
        value = significand * (2 ** (1 - config.bias))
        return -value if sign else value
    elif classification == 'normal':
        # Value = (-1)^sign * (1 + mantissa/2^frac_bits) * 2^(exponent-bias)
        significand = 1.0 + mantissa / (1 << config.frac_bits)
        value = significand * (2 ** (exponent - config.bias))
        return -value if sign else value
    else:
        raise ValueError(f"Unknown classification: {classification}")

def _create_breakdown(sign: int, exponent: int, mantissa: int, config: IEEE754Config, 
                     classification: str, value: float) -> Dict[str, Any]:
    """Create detailed breakdown for educational purposes"""
    breakdown = {
        'sign_explanation': f"Sign bit = {sign} → {'negative' if sign else 'positive'}",
        'classification': classification,
        'exponent_explanation': '',
        'mantissa_explanation': '',
        'formula': '',
        'calculation': ''
    }
    
    if classification == 'zero':
        breakdown.update({
            'exponent_explanation': f"Exponent = {exponent} (all zeros) → zero",
            'mantissa_explanation': f"Mantissa = {mantissa} (all zeros) → zero",
            'formula': f"(-1)^{sign} × 0 = {value}",
            'calculation': f"Value is {'negative' if sign else 'positive'} zero"
        })
    elif classification == 'infinity':
        breakdown.update({
            'exponent_explanation': f"Exponent = {exponent} (all ones) → special",
            'mantissa_explanation': f"Mantissa = {mantissa} (zero) → infinity",
            'formula': f"(-1)^{sign} × ∞ = {value}",
            'calculation': f"Value is {'negative' if sign else 'positive'} infinity"
        })
    elif classification == 'nan':
        breakdown.update({
            'exponent_explanation': f"Exponent = {exponent} (all ones) → special",
            'mantissa_explanation': f"Mantissa = {mantissa} (non-zero) → NaN",
            'formula': "NaN (Not a Number)",
            'calculation': "Value is undefined"
        })
    elif classification == 'subnormal':
        unbiased_exp = 1 - config.bias
        significand = mantissa / (1 << config.frac_bits)
        breakdown.update({
            'exponent_explanation': f"Exponent = {exponent} (zero) → subnormal, use {unbiased_exp}",
            'mantissa_explanation': f"Mantissa = {mantissa} → significand = {mantissa}/{1 << config.frac_bits} = {significand}",
            'formula': f"(-1)^{sign} × {significand} × 2^{unbiased_exp}",
            'calculation': f"= {'-' if sign else '+'}{significand} × {2**unbiased_exp} = {abs(value)}"
        })
    elif classification == 'normal':
        unbiased_exp = exponent - config.bias
        frac_value = mantissa / (1 << config.frac_bits)
        significand = 1.0 + frac_value
        breakdown.update({
            'exponent_explanation': f"Exponent = {exponent} → unbiased = {exponent} - {config.bias} = {unbiased_exp}",
            'mantissa_explanation': f"Mantissa = {mantissa} → fraction = {mantissa}/{1 << config.frac_bits} = {frac_value}",
            'formula': f"(-1)^{sign} × (1 + {frac_value}) × 2^{unbiased_exp}",
            'calculation': f"= {'-' if sign else '+'}{significand} × {2**unbiased_exp} = {abs(value)}"
        })
    
    return breakdown

def _create_zero_result(config: IEEE754Config, positive: bool = True) -> Dict[str, Any]:
    """Create result for zero value"""
    sign = 0 if positive else 1
    bits = pack_ieee754(sign, 0, 0, config)
    bit_format = format_bits(bits, config)
    
    return {
        'value': 0.0 if positive else -0.0,
        'classification': 'zero',
        'sign': sign,
        'exponent_raw': 0,
        'mantissa_raw': 0,
        'fields': bit_format,
        'breakdown': _create_breakdown(sign, 0, 0, config, 'zero', 0.0 if positive else -0.0)
    }

def _create_inf_result(config: IEEE754Config, positive: bool = True) -> Dict[str, Any]:
    """Create result for infinity value"""
    sign = 0 if positive else 1
    bits = pack_ieee754(sign, config.exp_max, 0, config)
    bit_format = format_bits(bits, config)
    value = math.inf if positive else -math.inf
    
    return {
        'value': value,
        'classification': 'infinity',
        'sign': sign,
        'exponent_raw': config.exp_max,
        'mantissa_raw': 0,
        'fields': bit_format,
        'breakdown': _create_breakdown(sign, config.exp_max, 0, config, 'infinity', value)
    }

def _create_nan_result(config: IEEE754Config, reason: str = "NaN") -> Dict[str, Any]:
    """Create result for NaN value"""
    # Use quiet NaN with sign=0 and mantissa MSB=1
    mantissa = 1 << (config.frac_bits - 1)
    bits = pack_ieee754(0, config.exp_max, mantissa, config)
    bit_format = format_bits(bits, config)
    
    return {
        'value': math.nan,
        'classification': 'nan',
        'sign': 0,
        'exponent_raw': config.exp_max,
        'mantissa_raw': mantissa,
        'fields': bit_format,
        'breakdown': _create_breakdown(0, config.exp_max, mantissa, config, 'nan', math.nan),
        'reason': reason
    }