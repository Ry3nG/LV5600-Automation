import logging
from typing import List
from .lv5600_initialization import lv5600_initialization, LV5600InitializationError
from .capture_and_send_bmp import capture_and_send_bmp
from commands import wfm_command
from Constants import Constants
import cv2
import numpy as np

average_count = 10

async def calculate_middle_cyan_y(image) -> float:
    lower_cyan_range = np.array([0, 200, 200])
    upper_cyan_range = np.array([100, 255, 255])

    # get cyan coordinates
    cyan_mask = cv2.inRange(image, lower_cyan_range, upper_cyan_range)
    cyan_coordinates = np.where(cyan_mask == 255)
    cyan_coordinates = np.array(cyan_coordinates)

    mid_point_x = int(image.shape[1]/2)
    mid_cyan_pixels = np.where(cyan_coordinates[1] == mid_point_x)[0]
    mid_cyan_y = np.nanmean(cyan_coordinates[0][mid_cyan_pixels])
    return mid_cyan_y


async def auto_white_balance(telnet_client, ftp_client):
    try:
        # initialize LV5600
        try:
            await lv5600_initialization(telnet_client)
            logging.info("LV5600 initialized.")
        except LV5600InitializationError as e:
            logging.error("LV5600 Initialization error: "+str(e))
            return
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return

        # turn off the WFM SCALE
        try:
            response = await telnet_client.send_command(wfm_command.wfm_scale_inten(-8))
            logging.info("Turned off WFM SCALE")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return

        cyan_y_values = []
        for i in range(average_count): # replace N with number of screenshots
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
                return
        
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = image[Constants.WFM_ROI_COORDINATES_X1:Constants.WFM_ROI_COORDINATES_X2, Constants.WFM_ROI_COORDINATES_Y1:Constants.WFM_ROI_COORDINATES_Y2]


            mid_cyan_y = await calculate_middle_cyan_y(image)
            if np.isnan(mid_cyan_y):
                logging.warning(f"No cyan pixel in the middle for image {i+1}")
                continue

            cyan_y_values.append(mid_cyan_y)
            logging.info(f"Middle cyan pixel's y value for image {i+1}: {mid_cyan_y}")

        # calculate average y value
        average_y = np.mean(cyan_y_values)
        logging.info(f"Average y value: {average_y}")

        # calculate target level
        target_level = (1-average_y/float(image.shape[0]))* 11000 
        target_level = int(target_level)

        # tune WFM Cursor to target level
        try:
            logging.info(f"Target level: {target_level}")
            response = await telnet_client.send_command(wfm_command.wfm_cursor_height('Y',"DELTA",target_level))
            logging.info("Tuned WFM Cursor to target level")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return

        # turn back the WFM SCALE
        try:
            response = await telnet_client.send_command(wfm_command.wfm_scale_inten(7))
            logging.info("Turned on WFM SCALE")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return
    finally:
        logging.info("Auto white balance finished.")
    
    """
    y = 0.07x
    x is the cursor height, and y is the mv value

    between y value and cursor height, there is also a linear relationship
    the formula is level = (1-y/roi_height)*11000
    """
    # calculate the value of n1
    n1_cursor_height = target_level
    n1_mv_value = 0.07 * n1_cursor_height
    logging.info(f"n1 mv value: {n1_mv_value}")

    n1_plus_20_value = n1_mv_value + 20
    n1_plus_20_cursor_height = int(n1_plus_20_value/0.07)

    n1_minus_20_value = n1_mv_value - 20
    n1_minus_20_cursor_height = int(n1_minus_20_value/0.07)
