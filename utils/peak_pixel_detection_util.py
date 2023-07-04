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
from PyQt5.QtWidgets import QMessageBox

average_count = Constants.AVERAGE_COUNT


def calculate_middle_cyan_y(image, calculation_type) -> float:
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
    """
    Classifies the given mv_value as 'Too high', 'Just right', 'Too low', or 'Invalid' based on the given target_high and target_low values.

    Args:
        mv_value (float): The mv value to classify.
        target_high (float): The upper threshold for the mv value.
        target_low (float): The lower threshold for the mv value.

    Returns:
        str: The classification of the mv value.

    Raises:
        None.
    """
    if mv_value > target_high:
        return "Too high"
    elif target_low <= mv_value <= target_high:
        return "Just right"
    elif 0 <= mv_value < target_low:
        return "Too low"

    logging.error(f"Invalid mv value: {mv_value}")
    return "Invalid"

async def prompt_manual_adjustment():
    """
    Prompts the user to manually adjust and waits for confirmation to continue.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.
    """
    while True:
        user_input = input("Please manually adjust, press 'y' to continue")
        if user_input == "y":
            break
        else:
            logging.info("Invalid input, please try again")

async def prompt_manual_adjustment_qt():
    while True:
        message_box = QMessageBox()
        message_box.setText("Please manually adjust")
        message_box.setInformativeText("Press 'OK' to continue")
        message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        result = message_box.exec_()

        if result == QMessageBox.Ok:
            break
        else:
            logging.info("Invalid input, please try again")


async def get_cursor_and_mv(
    telnet_client, ftp_client, mode, target_cursor_value=Constants.MAX_CURSOR_POSITION
) -> float:
    """
    Captures an image from the LV5600 and calculates the middle cyan pixel's y value.
    Calculates the average y value of multiple images and returns the current MV value.

    Args:
        telnet_client (TelnetClient): The telnet client to use for sending commands.
        ftp_client (FTPClient): The ftp client to use for sending commands.
        mode (str): The mode to use for calculating the middle cyan pixel's y value. Can be "SAT", "WB", or "NOISE".
        target_cursor_value (int): The target cursor value to use for tuning the WFM Cursor. Defaults to Constants.MAX_CURSOR_POSITION.

    Returns:
        float: The current MV value.
        or -1.0 if there was an error.

    Raises:
        None.
    """
    error_code = -1.0
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
            return error_code

        cyan_y_values = []
        for i in range(average_count):
            # capture the image
            try:
                await capture_and_send_bmp(telnet_client, ftp_client)
            except Exception as e:
                logging.error(f"Failed to capture and send bmp: {e}")
                continue
            image = cv2.imread(Constants.LOCAL_FILE_PATH_BMP)
            if image is None:
                logging.error("Image is None")
                return error_code

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = image[
                Constants.WFM_ROI_COORDINATES_X1 : Constants.WFM_ROI_COORDINATES_X2,
                Constants.WFM_ROI_COORDINATES_Y1 : Constants.WFM_ROI_COORDINATES_Y2,
            ]
            if mode == "SAT":
                mid_cyan_y = calculate_middle_cyan_y(image, calculation_type="min")
            elif mode == "WB":
                mid_cyan_y = calculate_middle_cyan_y(image, calculation_type="mean")
            elif mode == "NOISE":
                mid_cyan_y = calculate_middle_cyan_y(image, calculation_type="mean")
            else:
                logging.error(f"Invalid mode: {mode}")
                return error_code
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
                return error_code

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
        return error_code

    return current_mv_value
