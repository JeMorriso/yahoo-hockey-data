import re

def height_to_int(height_str):
    h = [int(s) for s in re.findall(r'\d+', height_str)]

    return 12*h[0] + h[1]

def int_to_height(height_inches):
    feet = height_inches/12
    inches = height_inches%12

    return f"{feet}\'{inches}\""
