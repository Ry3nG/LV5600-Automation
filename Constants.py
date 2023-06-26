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

    # for initialization
    BACKLIGHT_LEVEL = 32
    LINE_NUMBER = 580
    WFM_ROI_COORDINATES_X1 = 93
    WFM_ROI_COORDINATES_X2 = 775
    WFM_ROI_COORDINATES_Y1 = 755
    WFM_ROI_COORDINATES_Y2 = 1745

    # for Capture and storage
    FTP_FILE_NAME_BMP = "cap_bmp.bmp"
    LOCAL_FILE_PATH_BMP = "E:\\M15\\Leader LV5600 PoC\\LV5600 Automation\\output\\CAP_BMP.bmp"
    LOCAL_BUFFER_PATH = "E:\\M15\\Leader LV5600 PoC\\LV5600 Automation\\output\\buffer\\"

    # model
    MODEL_PATH = "E:\\M15\\Leader LV5600 PoC\\Models\\"
    WLI_MODEL_NAME = "model_20_20230615-134651.h5"
    RDI_MODEl_NAME = "RDI-Model-20K.h5"

    # CNN Testing
    CNN_IMAGE_SIZE = (670, 240)
    ROI_COORDINATES = (920, 1590, 60, 300)
    CATEGORY_DICT = {0: "JustSaturated", 1: "OverSaturated", 2: "UnderSaturated"}
    TEST_CATEGORIES = ["OverSaturated", "UnderSaturated", "JustSaturated"]

    # dataset directory
    # WLI
    PATH_WLI_DATASET_RAW = "E:\\M15\\Leader LV5600 PoC\\Dataset\\WLI Dataset\\RAW\\"
    PATH_WLI_TESTSET = "E:\\M15\\Leader LV5600 PoC\\Dataset\\WLI Dataset\\TestSet\\"
    PATH_WLI_FAILED = "E:\\M15\\Leader LV5600 PoC\\Dataset\\WLI Dataset\\Failed Testset\\"
    PATH_WLI_BUFFER = "E:\\M15\\Leader LV5600 PoC\\Dataset\\WLI Dataset\\PreprocessingBuffer\\"
    # Noise
    PATH_NOISE_DATASET_RAW = "E:\\M15\\Leader LV5600 PoC\\Dataset\\Noise Dataset\\RAW\\"
    # RDI
    PATH_RDI_DATASET_RAW = "E:\\M15\\Leader LV5600 PoC\\Dataset\\RDI Dataset\\RAW\\"
    PATH_RDI_DATASET_PREPROCESSED = "E:\\M15\\Leader LV5600 PoC\\Dataset\\RDI Dataset\\Preprocessed\\"
    PATH_RDI_TESTSET = "E:\\M15\\Leader LV5600 PoC\\Dataset\\RDI Dataset\\PreProcessed\\test"   
    PATH_RDI_FAILED = "E:\\M15\\Leader LV5600 PoC\\Dataset\\RDI Dataset\\PreProcessed\\failed"
    PATH_RDI_BUFFER = "E:\\M15\\Leader LV5600 PoC\\Dataset\\RDI Dataset\\PreProcessed\\buffer"