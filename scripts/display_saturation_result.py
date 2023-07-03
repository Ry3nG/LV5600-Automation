from utils.peak_pixel_detection_util import get_cursor_and_mv

import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import logging
import collections
from time import sleep
from Constants import Constants
from utils.peak_pixel_detection_util import get_cursor_and_mv, classify_mv_level

average_count = 3


async def display_result(telnet_client, ftp_client):
    # show the image, and the classification
    image = cv2.imread(Constants.LOCAL_FILE_PATH_BMP)
    if image is None:
        logging.error("Image is None")
        return

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image[
        Constants.WFM_ROI_COORDINATES_X1 : Constants.WFM_ROI_COORDINATES_X2,
        Constants.WFM_ROI_COORDINATES_Y1 : Constants.WFM_ROI_COORDINATES_Y2,
    ]
    plt.imshow(image)

    current_mv_value = await get_cursor_and_mv(telnet_client, ftp_client, "SAT")
    saturation_class = classify_mv_level(current_mv_value, 769.5, 766.5)
    if saturation_class == "Too high":
        saturation_class = "Oversatuated"
    elif saturation_class == "Too low":
        saturation_class = "Undersaturated"
    elif saturation_class == "Just right":
        saturation_class = "Just Saturated"
    print("Saturation class: ", saturation_class)
    plt.title(str(saturation_class) + " " + str(current_mv_value))
    plt.show()
