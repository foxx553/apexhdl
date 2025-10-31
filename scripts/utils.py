# Clamp to nearest discrete value
def clamp_nearest(value, window_min, window_step, window_bit_width):
    float_quotient = (value - window_min) / window_step
    float_remainder = float_quotient % 1
    nearest_int = int(float_quotient) if float_remainder < 0.5 else int(float_quotient) + 1
    return max(0, min(nearest_int, 2 ** window_bit_width - 1))

# Least significant bits extraction
def int_to_lsb(n, data_width):
    masked = n & ((2 ** data_width) - 1)
    return format(masked, f'0{data_width}b')