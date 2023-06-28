from time import sleep
from typing import Tuple
import numpy as np
import logging
import cv2
from commands import wfm_command
from scripts.capture_and_send_bmp import capture_and_send_bmp
from scripts.lv5600_initialization import (
    lv5600_initialization,
    LV5600InitializationError,
)
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

import logging
from Constants import Constants

average_count = 3


def calculate_middle_cyan_y(image, calculation_type="min") -> float:
    """
    Calculates the y-coordinate of the middle cyan pixel in the given image.

    Args:
        image (numpy.ndarray): The image to process.
        calculation_type (str, optional): The type of calculation to perform. Can be 'min' or 'mean'. Defaults to 'min'.

    Returns:
        float: The y-coordinate of the middle cyan pixel, or NaN if no cyan pixel is found.

    Raises:
        ValueError: If the calculation_type argument is not 'min' or 'mean'.
    """
    lower_cyan_range = np.array([0, 200, 200])
    upper_cyan_range = np.array([100, 255, 255])

    # get cyan coordinates
    cyan_mask = cv2.inRange(image, lower_cyan_range, upper_cyan_range)
    cyan_coordinates = np.where(cyan_mask == 255)
    cyan_coordinates = np.array(cyan_coordinates)

    mid_point_x = int(image.shape[1] / 2)
    mid_cyan_pixels = np.where(cyan_coordinates[1] == mid_point_x)[0]
    if calculation_type == "min":
        mid_cyan_y = np.nanmin(cyan_coordinates[0][mid_cyan_pixels])
    elif calculation_type == "mean":
        mid_cyan_y = np.nanmean(cyan_coordinates[0][mid_cyan_pixels])
    else:
        logging.error(f"Invalid calculation type: {calculation_type}")
        mid_cyan_y = np.nan
    return mid_cyan_y


def classify_mv_level(mv_value: float, target_high, target_low) -> str:
    if mv_value > target_high:
        mv_level = "Too bright"
    elif target_low <= mv_value <= target_high:
        mv_level = "Just right"
    elif 0 <= mv_value <= target_low:
        mv_level = "Too dark"
    else:
        logging.error(f"Invalid mv value: {mv_value}")
        mv_level = "Invalid"
    return mv_level


async def prompt_manual_adjustment():
    while True:
        user_input = input("Please manually adjust, press 'y' to continue")
        if user_input == "y":
            break
        else:
            logging.info("Invalid input, please try again")


async def get_cursor_and_mv(
    telnet_client, ftp_client, mode, target_cursor_value=0
):  # mode can be "SAT" or "WB" or "NOISE"
    error_tuple = (None, None)
    try:
        # turn off the WFM SCALE and Cursor
        try:
            response = await telnet_client.send_command(wfm_command.wfm_scale_inten(-8))
            response = await telnet_client.send_command(
                wfm_command.wfm_cursor_height("Y", "DELTA", 0)
            )
            logging.info("Turned off WFM SCALE and Cursor")
            sleep(0.2)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return error_tuple

        cyan_y_values = []
        for i in range(average_count):
            # capture the image
            try:
                await capture_and_send_bmp(telnet_client, ftp_client)
                logging.info(f"Captured and sent bmp {i+1}.")
            except Exception as e:
                logging.error(f"Failed to capture and send bmp: {e}")
                continue
            image = cv2.imread(Constants.LOCAL_FILE_PATH_BMP)
            if image is None:
                logging.error("Image is None")
                return error_tuple

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = image[
                Constants.WFM_ROI_COORDINATES_X1 : Constants.WFM_ROI_COORDINATES_X2,
                Constants.WFM_ROI_COORDINATES_Y1 : Constants.WFM_ROI_COORDINATES_Y2,
            ]
            if mode == "SAT":
                mid_cyan_y = calculate_middle_cyan_y(image)
            elif mode == "WB":
                mid_cyan_y = calculate_middle_cyan_y(image, calculation_type="mean")
            elif mode == "NOISE":
                mid_cyan_y = calculate_middle_cyan_y(image, calculation_type="mean")
            if np.isnan(mid_cyan_y):
                logging.warning(f"No cyan pixel in the middle for image {i+1}")
                continue

            cyan_y_values.append(mid_cyan_y)
            logging.info(f"Middle cyan pixel's y value for image {i+1}: {mid_cyan_y}")

        # calculate average y value
        average_y = np.mean(cyan_y_values)
        logging.info(f"Average y value: {average_y}")

        cursor_level = (
            1
            - average_y
            / float(Constants.WFM_ROI_COORDINATES_X2 - Constants.WFM_ROI_COORDINATES_X1)
        ) * 11000
        cursor_level = int(cursor_level)

        if mode == "WB":
            # calculate cursor level

            target_cursor_value = cursor_level
            # tune WFM Cursor to target level
            try:
                logging.info(f"Peak level: {cursor_level}")
                response = await telnet_client.send_command(
                    wfm_command.wfm_cursor_height("Y", "DELTA", cursor_level)
                )
                logging.info("Tuned WFM Cursor to peak level")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                return error_tuple

    finally:
        if mode == "WB":
            logging.info("Set WFM Cursor to peak level.")

    current_mv_value = 0.07 * cursor_level
    logging.info(f"Current MV value: {current_mv_value}")

    # turn back on the WFM SCALE and Cursor
    try:
        response = await telnet_client.send_command(wfm_command.wfm_scale_inten(0))
        response = await telnet_client.send_command(
            wfm_command.wfm_cursor_height("Y", "DELTA", int(target_cursor_value))
        )
        logging.info("Turned on WFM SCALE and Cursor")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return error_tuple

    return current_mv_value
