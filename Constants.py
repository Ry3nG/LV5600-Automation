class TelnetConstants:
    TELNET_END_STRING = b"$"

class LV5600Constants:
    LINE_NUMBER = 580
    MAX_CURSOR_VALUE = 11000

class FTPConstants:
    FTP_FILE_NAME_BMP = 'cap_bmp.bmp'
    LOCAL_FILE_NAME_BMP = 'snapshot.bmp'

class CalculationConstants:
    AVERAGE_COUNT = 4
    TOLERANCE = 0.001 # 1 percent
    CURSOR_TO_MV_FACTOR = 0.07
    TARGET_SATURATION_MV_VALUE = 769
    MAX_SATURATION_MV_VALUE = 770
    

class PreprocessingConstants:
    ROI_COORDINATES_Y1 = 93
    ROI_COORDINATES_Y2 = 775
    ROI_COORDINATES_X1 = 755
    ROI_COORDINATES_X2 = 1745
