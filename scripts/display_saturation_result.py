from utils.peak_pixel_detection_util import get_cursor_and_mv

import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import logging
import collections
from time import sleep
from Constants import Constants
average_count = 3

async def display_result(telnet_client, ftp_client):
    # show the image, and the classification
    image = cv2.imread(Constants.LOCAL_FILE_PATH_BMP)
    if image is None:
        logging.error("Image is None")
        return
        
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image[Constants.WFM_ROI_COORDINATES_X1:Constants.WFM_ROI_COORDINATES_X2, Constants.WFM_ROI_COORDINATES_Y1:Constants.WFM_ROI_COORDINATES_Y2]
    plt.imshow(image)

    saturation_level, mv_value = await get_cursor_and_mv(telnet_client, ftp_client)
    plt.title(str(saturation_level) + " " + str(mv_value))
    plt.show()
