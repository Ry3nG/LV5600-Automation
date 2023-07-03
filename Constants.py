import os


class Constants:
    """
    A class that contains all the constants used in the LV5600 Automation project.
    """

    BASE_DIR = "E:\\"
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
    LOCAL_FILE_PATH_BMP = os.path.join(
        BASE_DIR, "M15", "Leader LV5600 PoC","LV5600 Automation", "output", "CAP_BMP.bmp"
    )
    LOCAL_BUFFER_PATH = os.path.join(BASE_DIR, "M15", "Leader LV5600 PoC","LV5600 Automation", "output", "buffer")

    # for peak pixel detection
    AVERAGE_COUNT = 5
    JUMP_THRESHOLD = 700
    MAX_CURSOR_POSITION = 11000
    MAX_MV_VALUE = 770
    TARGET_THRESHOLD_OFFSET = 3

    # model
    MODEL_PATH = os.path.join(BASE_DIR, "M15", "Leader LV5600 PoC", "Models")
    WLI_MODEL_NAME = "model_20_20230615-134651.h5"
    RDI_MODEl_NAME = "RDI-Model-20K.h5"

    # CNN Testing
    CNN_IMAGE_SIZE = (670, 240)
    ROI_COORDINATES = (920, 1590, 60, 300)
    CATEGORY_DICT = {0: "JustSaturated", 1: "OverSaturated", 2: "UnderSaturated"}
    TEST_CATEGORIES = ["OverSaturated", "UnderSaturated", "JustSaturated"]

    # dataset directory
    # WLI
    PATH_WLI_DATASET_RAW = os.path.join(
        BASE_DIR, "M15", "Leader LV5600 PoC", "Dataset", "WLI Dataset", "RAW"
    )
    PATH_WLI_TESTSET = os.path.join(
        BASE_DIR, "M15", "Leader LV5600 PoC", "Dataset", "WLI Dataset", "TestSet"
    )
    PATH_WLI_FAILED = os.path.join(
        BASE_DIR, "M15", "Leader LV5600 PoC", "Dataset", "WLI Dataset", "Failed Testset"
    )
    PATH_WLI_BUFFER = os.path.join(
        BASE_DIR,
        "M15",
        "Leader LV5600 PoC",
        "Dataset",
        "WLI Dataset",
        "PreprocessingBuffer",
    )
    # Noise
    PATH_NOISE_DATASET_RAW = os.path.join(
        BASE_DIR, "M15", "Leader LV5600 PoC", "Dataset", "Noise Dataset", "RAW"
    )
    # RDI
    PATH_RDI_DATASET_RAW = os.path.join(
        BASE_DIR, "M15", "Leader LV5600 PoC", "Dataset", "RDI Dataset", "RAW"
    )
    PATH_RDI_DATASET_PREPROCESSED = os.path.join(
        BASE_DIR, "M15", "Leader LV5600 PoC", "Dataset", "RDI Dataset", "Preprocessed"
    )
    PATH_RDI_TESTSET = os.path.join(
        BASE_DIR,
        "M15",
        "Leader LV5600 PoC",
        "Dataset",
        "RDI Dataset",
        "PreProcessed",
        "test",
    )
    PATH_RDI_FAILED = os.path.join(
        BASE_DIR,
        "M15",
        "Leader LV5600 PoC",
        "Dataset",
        "RDI Dataset",
        "PreProcessed",
        "failed",
    )
    PATH_RDI_BUFFER = os.path.join(
        BASE_DIR,
        "M15",
        "Leader LV5600 PoC",
        "Dataset",
        "RDI Dataset",
        "PreProcessed",
        "buffer",
    )
