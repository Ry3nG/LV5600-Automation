class TelnetConstants:
    TELNET_END_STRING = b"$"
    TELNET_CONNECTION_TIMEOUT = 7


class LV5600Constants:
    LINE_NUMBER = 580
    MAX_CURSOR_VALUE = 11000


class FTPConstants:
    FTP_FILE_NAME_BMP = "cap_bmp.bmp"
    LOCAL_FILE_NAME_BMP = "snapshot.bmp"


class CalculationConstants:
    AVERAGE_COUNT = 4
    JUMP_THRESHOLD = 0.97  # 97% of the target value
    CURSOR_TO_MV_FACTOR = 0.07
    SAT_MODE = 0
    NOISE_MODE = 1
    WHITE_BALANCE_MODE = 2
    ROI_COORDINATES_Y1 = 87
    ROI_COORDINATES_Y2 = 775
    ROI_COORDINATES_X1 = 755
    ROI_COORDINATES_X2 = 1745
