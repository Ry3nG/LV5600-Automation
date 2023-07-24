import os
import cv2
import numpy as np
import logging
from Constants import (
    CalculationConstants,
    FTPConstants,
    PreprocessingConstants,
    LV5600Constants,
)
import cv2
from config.application_config import AppConfig


class CalculationTasks:
    @staticmethod
    def calculate_middle_cyan_y(image, calculation_type) -> float:
        try:
            if image is None:
                raise ValueError("Image is None")
            if calculation_type not in ["min", "mean"]:
                raise ValueError(f"Invalid calculation type: {calculation_type}")

            lower_cyan_range = np.array([0, 200, 200])
            upper_cyan_range = np.array([100, 255, 255])

            cyan_mask = cv2.inRange(image, lower_cyan_range, upper_cyan_range)
            cyan_coordinates = np.where(cyan_mask == 255)
            cyan_coordinates = np.array(cyan_coordinates)

            mid_point_x = int(image.shape[1] / 2)
            #mid_cyan_pixels = np.where(cyan_coordinates[1] == mid_point_x)[0]
            mid_cyan_pixels = np.where((cyan_coordinates[1] >= mid_point_x - 5) & (cyan_coordinates[1] < mid_point_x + 5))[0]

            if calculation_type == "min":
                mid_cyan_y = np.nanmin(cyan_coordinates[0][mid_cyan_pixels])
            elif calculation_type == "mean":
                mid_cyan_y = np.nanmean(cyan_coordinates[0][mid_cyan_pixels])
            else:
                raise ValueError(f"Invalid calculation type: {calculation_type}")

            logging.debug(f"mid_cyan_y: {mid_cyan_y}")
            return mid_cyan_y

        except ValueError as ve:
            logging.error(f"ValueError: {ve}")
            return np.nan

        except Exception as e:
            logging.error(f"Exception: {e}")
            return np.nan

    @staticmethod
    def classify_mv_level(mv_value, target,tolerance) -> str:
        try:
            if mv_value is None:
                raise ValueError("mv_value is None")
            if target is None:
                raise ValueError("target is None")
            if not isinstance(mv_value, (int, float)):
                raise TypeError("mv_value must be a number")
            if not isinstance(target, (int, float)):
                raise TypeError("target must be a number")
            if target <= 0:
                raise ValueError("target must be greater than 0")


            #target_high = min(target * (1 + tolerance),CalculationConstants.MAX_SATURATION_MV_VALUE)
            target_high = target * (1 + tolerance)
            logging.debug(f"target_high: {target_high}")
            target_low = max(target * (1 - tolerance),0)
            logging.debug(f"target_low: {target_low}")

            if mv_value >= target_high:
                return "high"
            elif mv_value <= target_low:
                return "low"
            else:
                return "pass"

        except ValueError as ve:
            logging.error(f"ValueError: {ve}")
            return "error"

        except TypeError as te:
            logging.error(f"TypeError: {te}")
            return "error"

        except Exception as e:
            logging.error(f"Exception: {e}")
            return "error"

    @staticmethod
    async def preprocess_and_get_mid_cyan(mode) -> float:
        # get local file path from config file
        app_config = AppConfig()
        local_file_path = os.path.join(
            app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP
        )

        image = cv2.imread(local_file_path)
        if image is None:
            raise Exception("Error reading image")

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image[
            PreprocessingConstants.ROI_COORDINATES_Y1 : PreprocessingConstants.ROI_COORDINATES_Y2,
            PreprocessingConstants.ROI_COORDINATES_X1 : PreprocessingConstants.ROI_COORDINATES_X2,
        ]

        if mode == "SAT":
            mode = "min"
        elif mode == "WB" or mode == "NOISE":
            mode = "mean"
        else:
            raise ValueError("Invalid mode: " + str(mode))
        mid_cyan_y = CalculationTasks.calculate_middle_cyan_y(image, mode)

        return mid_cyan_y

    @staticmethod
    def get_cursor_and_mv(cyan_y):
        cursor_level = (
            1
            - cyan_y
            / float(
                PreprocessingConstants.ROI_COORDINATES_Y2
                - PreprocessingConstants.ROI_COORDINATES_Y1
            )
        ) * LV5600Constants.MAX_CURSOR_VALUE

        current_mv = round(cursor_level * CalculationConstants.CURSOR_TO_MV_FACTOR, 1)
        cursor_level = round(cursor_level, 0)

        logging.debug(f"cursor_level: {cursor_level}")
        logging.debug(f"current_mv: {current_mv}")
        return cursor_level, current_mv
