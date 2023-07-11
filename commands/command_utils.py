class WFMCommand:
    @staticmethod
    def wfm_line_select(input):
        """
        turn on/off wfm line select
        WFM:LINE_SELECT ON / OFF / CINELITE / ?
        """
        # check input is valid
        if input != "ON" and input != "OFF" and input != "CINELITE" and input != "?":
            raise ValueError("Invalid input. Input must be ON, OFF, CINELITE or ?.")

        return "WFM:LINE_SELECT " + input

    @staticmethod
    def wfm_line_number(input):
        # check input is valid
        if input < 0 or input > 32767:
            raise ValueError("Invalid input. Input must be between 0 to 32767.")
        return "WFM:LINE_NUMBER " + str(input)

    @staticmethod
    def wfm_matrix_ycbcr(input):
        # check input is valid
        if (
            input != "YCBCR"
            and input != "GBR"
            and input != "RGB"
            and input != "COMPOSITE"
        ):
            raise ValueError(
                "Invalid input. Input must be YCBCR, GBR, RGB or COMPOSITE."
            )

        return "WFM:MATRIX:YCBCR " + input

    @staticmethod
    def wfm_mode_rgb(channel, input):
        # check if channel is R or G or B
        if channel != "R" and channel != "G" and channel != "B":
            raise ValueError("Invalid channel. Channel must be R, G or B.")
        # check if input is valid
        if input != "ON" and input != "OFF" and input != "?":
            raise ValueError("Invalid input. Input must be ON, OFF or ?.")

        return "WFM:MODE:RGB:" + channel + " " + input

    @staticmethod
    def wfm_cursor(input):
        # check input is valid
        if input != "SINGLE" and input != "BOTH" and input != "OFF":
            raise ValueError("Invalid input. Input must be SINGLE, BOTH or OFF.")

        return "WFM:CURSOR " + input

    @staticmethod
    def wfm_cursor_height(axis, channel, val):
        # check if axis is X or Y
        if axis != "X" and axis != "Y":
            raise ValueError("Invalid axis. Axis must be X or Y.")
        # check if channel is REF or DELTA
        if channel != "REF" and channel != "DELTA":
            raise ValueError("Invalid channel. Channel must be REF or DELTA.")
        # check if val is valid
        if axis == "X":
            if val < 0 or val > 927:
                raise ValueError("Invalid val. Val must be between 0 to 927.")
        else:
            if val < -5000 or val > 15000:
                raise ValueError("Invalid val. Val must be between -5000 to 15000.")

        return "WFM:CURSOR:" + channel + " " + str(val)

    @staticmethod
    def wfm_scale_inten(val):
        # check if val is valid
        if val < -8 or val > 7:
            raise ValueError("Invalid val. Val must be between -8 to 7.")

        return "WFM:SCALE:INTEN " + str(val)

    @staticmethod
    def wfm_cursor_unit(ch, input):
        # check if channel is X or Y
        if ch != "X" and ch != "Y":
            raise ValueError("Invalid channel. Channel must be X or Y.")
        # check if input is valid
        if ch == "X":
            if input != "SEC" and input != "HZ":
                raise ValueError("Invalid input. Input must be SEC or HZ.")
        else:
            if (
                input != "MV"
                and input != "P"
                and input != "RP"
                and input != "DEC"
                and input != "HEX"
                and input != "HDR"
            ):
                raise ValueError(
                    "Invalid input. Input must be MV, P, RP, DEC, HEX or HDR."
                )

        return "WFM:CURSOR:UNIT:" + ch + " " + input

class CaptureCommand:
    @staticmethod
    def make(input):
        # check input is valid
        if (
            input != "CAP_BMP"
            and input != "CAP_BSG"
            and input != "CAP_DPX_A"
            and input != "CAP_DPX_B"
            and input != "CAP_DPX_C"
            and input != "CAP_DPX_D"
            and input != "CAP_TIF_A"
            and input != "CAP_TIF_B"
            and input != "CAP_TIF_C"
            and input != "CAP_TIF_D"
            and input != "CAP_FRM_A"
            and input != "CAP_FRM_B"
            and input != "CAP_FRM_C"
            and input != "CAP_FRM_D"
            and input != "LOG"
            and input != "DUMP"
            and input != "LOUDNESS"
        ):
            raise ValueError(
                "Invalid input. Input must be CAP_BMP, CAP_BSG, CAP_DPX_A, CAP_DPX_B, CAP_DPX_C, CAP_DPX_D, CAP_TIF_A, CAP_TIF_B, CAP_TIF_C, CAP_TIF_D, CAP_FRM_A, CAP_FRM_B, CAP_FRM_C, CAP_FRM_D, LOG, DUMP or LOUDNESS."
            )

        return "MAKE " + str(input)

    @staticmethod
    def take_snapshot():
        return "CAP:REFRESH"


class InputCommand:
    @staticmethod
    def change_input_to(input):
        # Determine the input number based on the input letter
        if input == "A":
            num = 1
        elif input == "B":
            num = 2
        elif input == "C":
            num = 3
        elif input == "D":
            num = 4
        else:
            raise ValueError("Invalid input. Input must be A, B, C or D.")

        # Return the command to change the input to the corresponding input number
        return "INPUT_CHANGE " + str(num)


class PresetCommand:
    @staticmethod
    def recall_preset(input):
        # check input is valid
        if input < 1 or input > 60:
            raise ValueError("Invalid input. Input must be between 1 to 60.")

        return "RCLL " + str(input)
class SYSCommand:
    @staticmethod
    def set_backlight_level(input):
        # check input is valid
        if input < 1 or input > 32:
            raise ValueError("Invalid input. Input must be between 1 to 32.")
        
        return "SYS:LCD:BACKLIGHT " + str(input)
   
    @staticmethod
    def system_initialize():
        return "SYS:INITIALIZE:ALL"