"""
    r/w limitation: -
    command: SYS:LCD:BACKLIGHT
    parameter: 1 to 32
"""
def set_backlight_level(input):
    # check input is valid
    if input < 1 or input > 32:
        print("Invalid input. Input must be between 1 to 32.")
        return None
    
    return "SYS:LCD:BACKLIGHT " + str(input)
