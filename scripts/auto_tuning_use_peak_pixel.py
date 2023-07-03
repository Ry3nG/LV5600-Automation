import logging
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from .lv5600_initialization import lv5600_initialization, LV5600InitializationError
from .capture_and_send_bmp import capture_and_send_bmp
from utils.peak_pixel_detection_util import (
    classify_mv_level,
    prompt_manual_adjustment,
    calculate_middle_cyan_y,
    get_cursor_and_mv,
)
from commands import wfm_command
from Constants import Constants
import collections
from Constants import Constants

average_count = 5


async def auto_adjust(
    telnet_client,
    ftp_client,
    debugConsoleController,
    current_brightness,
    mode,
    target,
    target_high_threshold,
    target_low_threshold,
    use_poly_prediction=True,
    jump_threshold=Constants.AVERAGE_COUNT,
):
    current_class_ = None
    # convert target mv to target cursor height
    target_cursor_height = (
        Constants.MAX_CURSOR_POSITION / Constants.MAX_MV_VALUE
    ) * target
    mv_values = []
    light_levels = []
    current_light_level = current_brightness  # Init with current brightness
    light_history = collections.deque(maxlen=3)

    while current_class_ != "Just right":
        current_mv_value = await get_cursor_and_mv(
            telnet_client, ftp_client, mode, target_cursor_height
        )
        current_class_ = classify_mv_level(
            current_mv_value, target_high_threshold, target_low_threshold
        )

        # check if the response is none
        if current_class_ is None or current_mv_value is None:
            logging.error("Response is None")
            return

        # add the current light level to the history
        light_history.append(current_light_level)

        # check if the last 3 light level values are oscillating
        if len(light_history) == 3 and len(set(light_history)) == 2:
            print("Possible oscillation detected, breaking the loop")
            # tune WFM Cursor to target for indication
            try:
                logging.info(f"Tuning WFM Cursor to {target:.1f} mV")
                response = await telnet_client.send_command(
                    wfm_command.wfm_cursor_height(
                        "Y", "DELTA", int(target_cursor_height)
                    )
                )
                logging.info(f"Tuned WFM Cursor to {target:.1f} mV")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
            await prompt_manual_adjustment()
            # pop all from the deque
            light_history.clear()
            continue

        if (
            len(mv_values) < 2
            or current_mv_value >= jump_threshold
            or not use_poly_prediction
        ):
            # single step adjustment
            mv_values.append(current_mv_value)
            light_levels.append(current_light_level)

            if current_class_ == "Too high":
                print("Turning down the brightness")
                debugConsoleController.tune_down_light()
                current_light_level -= 1
            elif current_class_ == "Too low":
                print("Turning up the brightness")
                debugConsoleController.tune_up_light()
                current_light_level += 1
            elif current_class_ == "Just right":
                break
            else:
                print("Unknown status")
        else:
            # fit polynomial regression model and predict light level to reach target_mv_level
            poly = PolynomialFeatures(degree=2)
            X = poly.fit_transform(np.array(mv_values).reshape(-1, 1))
            model = LinearRegression().fit(X, light_levels)
            predicted_light_level = model.predict(
                poly.fit_transform(np.array(jump_threshold).reshape(-1, 1))
            )[0]

            if predicted_light_level < 0:
                predicted_light_level = current_light_level + 1
            if abs(predicted_light_level - current_light_level) > 10:
                predicted_light_level = current_light_level + 10
            if predicted_light_level > 255:
                predicted_light_level = 255

            print(
                "Adjusting brightness closer to target level "
                + str(predicted_light_level)
            )
            debugConsoleController.tune_to_target_level(
                int(predicted_light_level), current_light_level
            )

            # Update current_light_level
            current_light_level = int(predicted_light_level)

            # reset mv_values and light_levels for the next prediction if necessary
            mv_values = []
            light_levels = []

            if current_mv_value >= jump_threshold:
                break  # exit the while loop if the target_mv_level is reached

    print(current_class_)
    try:
        logging.info(f"Tuning WFM Cursor to {target:.1f} mV")
        response = await telnet_client.send_command(
            wfm_command.wfm_cursor_height("Y", "DELTA", int(target_cursor_height))
        )
        logging.info(f"Tuned WFM Cursor to {target:.1f} mV")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


async def white_balance_auto_detect(telnet_client, ftp_client):
    n1_mv_values = await get_cursor_and_mv(telnet_client, ftp_client, "WB")
    logging.info("N1 mv values: " + str(n1_mv_values))
    return n1_mv_values


async def noise_level_auto_adjust(
    telnet_client, ftp_client, debugConsoleController, n1_value
):
    n1_plus20 = n1_value + 20
    n1_minus20 = n1_value - 20

    # convert mv value to cursor height
    # when cursor is 0, mv = 0, when cursor is 11000, mv = 770,
    # so the slope is 770/11000 = 0.07
    # so cursor = (770/11000) * mv

    cursor_plus20 = int(
        (Constants.MAX_CURSOR_POSITION / Constants.MAX_MV_VALUE) * n1_plus20
    )
    cursor_minus20 = int(
        (Constants.MAX_CURSOR_POSITION / Constants.MAX_MV_VALUE) * n1_minus20
    )

    # calculate threshold
    n1_plus20_high_threshold = n1_plus20 + Constants.TARGET_THRESHOLD_OFFSET
    n1_plus20_low_threshold = n1_plus20 - Constants.TARGET_THRESHOLD_OFFSET

    n1_minus20_high_threshold = n1_minus20 + Constants.TARGET_THRESHOLD_OFFSET
    n1_minus20_low_threshold = n1_minus20 - Constants.TARGET_THRESHOLD_OFFSET

    logging.info("N1 + 20: " + str(n1_plus20))
    logging.info("Auto adjusting to N1 + 20")
    await auto_adjust(
        telnet_client,
        ftp_client,
        debugConsoleController,
        int(input("Enter current brightness level: ")),
        "NOISE",
        n1_plus20,
        n1_plus20_high_threshold,
        n1_plus20_low_threshold,
        use_poly_prediction=False,
        jump_threshold=0,
    )

    logging.info("N1 - 20: " + str(n1_minus20))
    logging.info("Auto adjusting to N1 - 20")
    # prompt user to press enter
    input("Press Enter to continue...")

    await auto_adjust(
        telnet_client,
        ftp_client,
        debugConsoleController,
        int(input("Enter current brightness level: ")),
        "NOISE",
        n1_minus20,
        n1_minus20_high_threshold,
        n1_minus20_low_threshold,
        use_poly_prediction=False,
        jump_threshold=0,
    )
