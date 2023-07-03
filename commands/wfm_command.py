def goto_wfm_page():
    return "WFM"

"""
    turn on/off wfm line select
    WFM:LINE_SELECT ON / OFF / CINELITE / ?
"""
def wfm_line_select(input):
    # check input is valid
    if input != "ON" and input != "OFF" and input != "CINELITE" and input != "?":
        print("Invalid input. Input must be ON, OFF, CINELITE or ?.")
        return None
    
    return "WFM:LINE_SELECT " + input

"""
    WFM:LINE_NUMBER 0 to 32767 / ?
"""
def wfm_line_number(input):
    # check input is valid
    if input < 0 or input > 32767:
        print("Invalid input. Input must be between 0 to 32767.")
        return None
    
    return "WFM:LINE_NUMBER " + str(input)

"""
    WFM:MATRIX:YCBCR YCBCR / GBR / RGB / COMPOSITE
"""
def wfm_matrix_ycbcr(input):
    # check input is valid
    if input != "YCBCR" and input != "GBR" and input != "RGB" and input != "COMPOSITE":
        print("Invalid input. Input must be YCBCR, GBR, RGB or COMPOSITE.")
        return None
    
    return "WFM:MATRIX:YCBCR " + input

"""
- WFM:MODE:RGB:R ON / OFF / ?
- WFM:MODE:RGB:G ON / OFF / ?
- WFM:MODE:RGB:B ON / OFF / ?
"""
def wfm_mode_rgb(channel, input):
    # check if channel is R or G or B
    if channel != "R" and channel != "G" and channel != "B":
        print("Invalid channel. Channel must be R, G or B.")
        return None
    # check if input is valid
    if input != "ON" and input != "OFF" and input != "?":
        print("Invalid input. Input must be ON, OFF or ?.")
        return None
    
    return "WFM:MODE:RGB:" + channel + " " + input

"""
    WFM:CURSOR SINGLE / BOTH / OFF
"""
def wfm_cursor(input):
    # check input is valid
    if input != "SINGLE" and input != "BOTH" and input != "OFF":
        print("Invalid input. Input must be SINGLE, BOTH or OFF.")
        return None
    
    return "WFM:CURSOR " + input

"""
- WFM:CURSOR:REF 0 to 927 (when X is selected) 
- 5000 to 15000 (when Y is selected)
- WFM:CURSOR:DELTA 0 to 927 (when X is selected) 
- 5000 to 15000 (when Y is selected
"""
def wfm_cursor_height(axis,channel, val):
    # check if axis is X or Y
    if axis != "X" and axis != "Y":
        print("Invalid axis. Axis must be X or Y.")
        return None
    # check if channel is REF or DELTA
    if channel != "REF" and channel != "DELTA":
        print("Invalid channel. Channel must be REF or DELTA.")
        return None
    # check if val is valid
    if axis == 'X':
        if val < 0 or val > 927:
            print("Invalid val. Val must be between 0 to 927.")
            return None
    else:
        if val < -5000 or val > 15000:
            print("Invalid val. Val must be between 5000 to 15000.")
            return None
    
    return "WFM:CURSOR:" + channel + " " + str(val)

"""
WFM:SCALE:INTEN -8 to 7
"""
def wfm_scale_inten(val):
    # check if val is valid
    if val < -8 or val > 7:
        print("Invalid val. Val must be between -8 to 7.")
        return None
    
    return "WFM:SCALE:INTEN " + str(val)

"""
WFM:CURSOR:UNIT:Y MV / P / RP / DEC / HEX / HDR
WFM:CURSOR:UNIT:X SEC / HZ /
"""
def wfm_cursor_unit(ch,input):
    # check if channel is X or Y
    if ch != "X" and ch != "Y":
        print("Invalid channel. Channel must be X or Y.")
        return None
    # check if input is valid
    if ch == 'X':
        if input != "SEC" and input != "HZ":
            print("Invalid input. Input must be SEC or HZ.")
            return None
    else:
        if input != "MV" and input != "P" and input != "RP" and input != "DEC" and input != "HEX" and input != "HDR":
            print("Invalid input. Input must be MV, P, RP, DEC, HEX or HDR.")
            return None
    
    return "WFM:CURSOR:UNIT:" + ch + " " + input