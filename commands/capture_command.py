"""
    r/w limitation: -
    command: CAP:TRIGGER
    param: MANUAL/ERROR/?
"""
def set_trigger_mode(input):
    # check input is valid
    if input != "MANUAL" and input != "ERROR" and input != "?":
        print("Invalid input. Input must be MANUAL, ERROR or ?.")
        return None
    
    return "CAP:TRIGGER " + str(input)

"""
    r/w limitation: WO
    command: MAKE
    param: CAP_BMP
"""
def make(input):
    # check input is valid
    if input != "CAP_BMP":
        print("Invalid input. Input must be CAP_BMP.")
        return None
    
    return "MAKE " + str(input)

"""
    r/w limitation: WO
    command: CAP:REFRESH
    param: None
"""
def take_snapshot():
    return "CAP:REFRESH"
