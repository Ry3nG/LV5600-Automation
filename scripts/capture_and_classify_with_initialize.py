from .capture_and_send_bmp import capture_and_send_bmp
from .lv5600_initialization import lv5600_initialization, LV5600InitializationError
from commands import wfm_command
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import logging
from time import sleep
from Constants import Constants
average_count = 5

async def calculate_middle_cyan_y(image) -> float:
    lower_cyan_range = np.array([0, 200, 200])
    upper_cyan_range = np.array([100, 255, 255])

    # get cyan coordinates
    cyan_mask = cv2.inRange(image, lower_cyan_range, upper_cyan_range)
    cyan_coordinates = np.where(cyan_mask == 255)
    cyan_coordinates = np.array(cyan_coordinates)

    mid_point_x = int(image.shape[1]/2)
    mid_cyan_pixels = np.where(cyan_coordinates[1] == mid_point_x)[0]
    mid_cyan_y = np.nanmin(cyan_coordinates[0][mid_cyan_pixels])
    return mid_cyan_y

async def capture_classify_show_with_initialize(telnet_client, ftp_client):
    try:    
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
            logging.info(f"Peak level: {target_level}")
            response = await telnet_client.send_command(wfm_command.wfm_cursor_height('Y',"DELTA",target_level))
            logging.info("Tuned WFM Cursor to peak level")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return


    finally:
        logging.info("Set WFM Cursor to peak level.")

    cursor_height = target_level
    mv_value = 0.07*cursor_height
    logging.info(f"Current MV value: {mv_value}")
    if(mv_value > 769.5):
        # oversaturated
        class_ = "Oversaturated"
    elif(768<=mv_value <= 769.5):
        # saturated
        class_ = "Saturated"
    elif(0<=mv_value < 768):
        # undersaturated
        class_ = "Undersaturated"
    else:
        logging.error("Unknown saturation level")
        class_ = "Unknown"
    
    # turn back on the WFM SCALE
    try:
        response = await telnet_client.send_command(wfm_command.wfm_scale_inten(0))
        logging.info("Turned on WFM SCALE")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return
    
    return class_, mv_value

async def display_result(telnet_client, ftp_client):
    # show the image, and the classification
    image = cv2.imread(Constants.LOCAL_FILE_PATH_BMP)
    if image is None:
        logging.error("Image is None")
        return
        
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image[Constants.WFM_ROI_COORDINATES_X1:Constants.WFM_ROI_COORDINATES_X2, Constants.WFM_ROI_COORDINATES_Y1:Constants.WFM_ROI_COORDINATES_Y2]
    plt.imshow(image)
    class_,mv_value = await capture_classify_show_with_initialize(telnet_client,ftp_client)
    plt.title(str(class_))
    plt.show()

async def auto_adjust(telnet_client, ftp_client, debugConsoleController, current_brightness):
    class_name = None

    mv_values = []
    light_levels = []
    current_light_level = current_brightness  # Init with current brightness

    target_mv_level = 700

    while class_name != "Saturated":
        class_name, current_mv_value = await capture_classify_show_with_initialize(telnet_client, ftp_client)

        if len(mv_values) < 3 or current_mv_value >= target_mv_level:
            # single step adjustment
            mv_values.append(current_mv_value)
            light_levels.append(current_light_level)

            if class_name == "Oversaturated":
                print("Oversaturated, turning down the brightness")
                debugConsoleController.tune_down_light()
                current_light_level -= 1  
            elif class_name == "Undersaturated":
                print("Undersaturated, turning up the brightness")
                debugConsoleController.tune_up_light()
                current_light_level += 1 
            elif class_name == "Saturated":
                print("Saturated")
            else:
                print("Unknown saturation level")
        else:
            # fit linear model and predict light level to reach target_mv_level
            linear_model = np.polyfit(np.array(mv_values), light_levels, 1)
            predicted_light_level = np.poly1d(linear_model)(target_mv_level)

            print("Adjusting brightness to target level")
            debugConsoleController.tune_to_target_level(int(predicted_light_level), current_light_level)

            # Update current_light_level
            current_light_level = int(predicted_light_level)

            # reset mv_values and light_levels for the next prediction if necessary
            mv_values = []
            light_levels = []

            if current_mv_value >= target_mv_level:
                break  # exit the while loop if the target_mv_level is reached