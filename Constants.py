# the place for all the constants


class Constants:
    # Credentials for FTP
    IP_ADDRESS_FTP = "192.168.0.1"
    USERNAME_FTP = "LV5600"
    PASSWORD_FTP = "LV5600"

    # Telnet Parameters
    TELNET_PORT = 23
    TELNET_END_STRING = b"$"

    # Credentials for Telnet
    IP_ADDRESS_TELNET = "192.168.0.1"
    USERNAME_TELNET = "LV5600"
    PASSWORD_TELNET = "LV5600"

    # for Capture and storage
    FTP_FILE_NAME_BMP = "cap_bmp.bmp"
    LOCAL_FILE_PATH_BMP = "E:\\Leader LV5600\\LV5600 Automation\\output\\CAP_BMP.bmp"

    # for waveform analysis
    TEST_DATASET_PATH = "E:\\Data\\TestSet\\"
    TEST_CATEGORIES = ['OverSaturated', 'UnderSaturated', 'JustSaturated']

    MODEL_PATH = 'E:\\Model\\'
    CNN_PREPROCESSING_BUFFER_PATH = 'E:\\Data\\PreprocessingBuffer\\'
    FAILED_TESTCASES_PATH = "E:\\Data\\Failed Testset\\"
    CROPPED_DATASET_PATH = 'E:\\Data\\LargeSet\\Cropped\\'

    OVERSATURATED_DATASET_PATH = 'E:\\Data\\LargeSet\\OverSaturated'
    UNDERSATURATED_DATASET_PATH = 'E:\\Data\\LargeSet\\UnderSaturated'
    JUSTSATURATED_DATASET_PATH = 'E:\\Data\\LargeSet\\JustSaturated'

    OVERSATURATED_CROPPED_DATASET_PATH = 'E:\\Data\\LargeSet\\Cropped\\OverSaturated'
    UNDERSATURATED_CROPPED_DATASET_PATH = 'E:\\Data\\LargeSet\\Cropped\\UnderSaturated'
    JUSTSATURATED_CROPPED_DATASET_PATH = 'E:\\Data\\LargeSet\\Cropped\\JustSaturated'