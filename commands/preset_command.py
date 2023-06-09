"""
    r/w limitation: WO
    command: RCLL
    parameter: 1 to 60
"""
def recall_preset(input):
    # check input is valid
    if input < 1 or input > 60:
        print("Invalid input. Input must be between 1 to 60.")
        return None
    
    return "RCLL " + str(input)