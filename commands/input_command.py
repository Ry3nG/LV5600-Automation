"""
    r/w limitation: -
    command: INPUT_CHANGE
    parameter: 1 to 4
"""
def change_input_to(input):
    # Determine the input number based on the input letter
    if input == 'A':
        num = 1
    elif input == 'B':
        num = 2
    elif input == 'C':
        num = 3
    elif input == 'D':
        num = 4

    # Return the command to change the input to the corresponding input number
    return "INPUT_CHANGE " + str(num)
