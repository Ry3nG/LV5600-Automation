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
    param: CAP_BMP / CAP_BSG/ CAP_DPX_A / CAP_DPX_B / CAP_DPX_C / CAP_DPX_D / CAP_TIF_A / CAP_TIF_B / CAP_TIF_C / CAP_TIF_D / CAP_FRM_A / CAP_FRM_B / CAP_FRM_C / CAP_FRM_D (*1)/LOG / DUMP / LOUDNESS (*2)
        * File make command. Use FTP to retrieve created files.
        *1 If you want to create a frame capture file (DPX, TIF, FRM), a video signal waveform, vector waveform, or picture must be displayed on the screen.
        *2 If you want to create an event log, data dump, or loudness file, the corresponding measurement screen must be displayed on the screen
"""
def make(input):
    # check input is valid
    if input != "CAP_BMP" and input != "CAP_BSG" and input != "CAP_DPX_A" and input != "CAP_DPX_B" and input != "CAP_DPX_C" and input != "CAP_DPX_D" and input != "CAP_TIF_A" and input != "CAP_TIF_B" and input != "CAP_TIF_C" and input != "CAP_TIF_D" and input != "CAP_FRM_A" and input != "CAP_FRM_B" and input != "CAP_FRM_C" and input != "CAP_FRM_D" and input != "LOG" and input != "DUMP" and input != "LOUDNESS":
        print("Invalid input. Input must be CAP_BMP, CAP_BSG, CAP_DPX_A, CAP_DPX_B, CAP_DPX_C, CAP_DPX_D, CAP_TIF_A, CAP_TIF_B, CAP_TIF_C, CAP_TIF_D, CAP_FRM_A, CAP_FRM_B, CAP_FRM_C, CAP_FRM_D, LOG, DUMP or LOUDNESS.")
        return None
    
    return "MAKE " + str(input)

"""
    r/w limitation: WO
    command: CAP:REFRESH
    param: None
"""
def take_snapshot():
    return "CAP:REFRESH"
