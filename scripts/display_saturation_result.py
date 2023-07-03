"""
This module contains a function to display the saturation result of an image.

Functions:
----------
display_result: Displays the saturation result of an image.
"""
import logging
import cv2
import matplotlib.pyplot as plt
from Constants import Constants
from utils.peak_pixel_detection_util import get_cursor_and_mv, classify_mv_level


AVERAGE_COUNT = Constants.AVERAGE_COUNT


async def display_result(telnet_client, ftp_client):
    """
    Displays the saturation result of an image.

    Parameters:
    -----------
    telnet_client: TelnetClient
        The telnet client object.
    ftp_client: FTPClient
        The FTP client object.
    """
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
