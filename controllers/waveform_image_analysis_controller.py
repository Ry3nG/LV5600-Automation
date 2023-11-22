from ctypes import c_char_p, c_int, c_float, cdll
import logging

from Constants import CalculationConstants


class WaveformImageAnalysisController:
    DLL_error_code = {
        -100: "Unknown error",
        -101: "Image could not be loaded",
        -102: "No cyan pixel found",
        -103: "Invalid parameter",
    }

    def __init__(self):
        self.myDLL = cdll.LoadLibrary("lib\\WaveformImageAnalysisLib.dll")
        self.oldDLL = cdll.LoadLibrary("lib\\WaveformImageAnalysisLib_old.dll")
        if not self.myDLL or not self.oldDLL:
            raise Exception("Could not load DLL")
        else:
            logging.info("Waveform Image Analysis DLL loaded successfully")

        self.get_current_mv_dll = self.myDLL.GetCurrentMV
        self.get_current_mv_dll.argtypes = [c_char_p, c_int, c_int, c_int, c_int, c_int]
        self.get_current_mv_dll.restype = c_float

        self.get_current_mid_mv_dll = self.myDLL.GetCurrentMidMV
        self.get_current_mid_mv_dll.argtypes = [c_char_p, c_int, c_int, c_int, c_int, c_int]
        self.get_current_mv_dll.restype = c_float

        self.get_current_cursor_level_dll = self.myDLL.GetCurrentCursorLevel
        self.get_current_cursor_level_dll.argtypes = [
            c_char_p,
            c_int,
            c_int,
            c_int,
            c_int,
            c_int,
        ]
        self.get_current_cursor_level_dll.restype = c_float

        self.classify_waveform_dll = self.myDLL.ClassifyWaveform
        self.classify_waveform_dll.argtypes = [
            c_float,
            c_float,
            c_float,
            c_float,
            c_float,
            c_int,
        ]
        self.classify_waveform_dll.restype = c_int

        self.get_current_stdev_dll = self.myDLL.GetCurrentStdev
        self.get_current_stdev_dll.argtypes = [c_char_p,c_float, c_int, c_int, c_int, c_int, c_int]
        self.get_current_stdev_dll.restype = c_float

        # -------------------------------------------
        self.get_current_mv_old_dll = self.oldDLL.GetCurrentMV
        self.get_current_mv_old_dll.argtypes = [c_char_p, c_int, c_int, c_int, c_int, c_int]
        self.get_current_mv_old_dll.restype = c_float

        self.get_current_cursor_level_old_dll = self.oldDLL.GetCurrentCursorLevel
        self.get_current_cursor_level_old_dll.argtypes = [
            c_char_p,
            c_int,
            c_int,
            c_int,
            c_int,
            c_int,
        ]
        self.get_current_cursor_level_old_dll.restype = c_float

        self.classify_waveform_old_dll = self.oldDLL.ClassifyWaveform
        self.classify_waveform_old_dll.argtypes = [
            c_float,
            c_float,
            c_float,
            c_float,
            c_float,
            c_int,
        ]
        self.classify_waveform_old_dll.restype = c_int

        self.get_current_stdev_old_dll = self.oldDLL.GetCurrentStdev
        self.get_current_stdev_old_dll.argtypes = [c_char_p,c_float, c_int, c_int, c_int, c_int, c_int]
        self.get_current_stdev_old_dll.restype = c_float




    def _check_error(self, result):
        if result in self.DLL_error_code:
            logging.error(self.DLL_error_code[result])
            raise Exception(self.DLL_error_code[result])

    def get_current_mv(
        self, image_path, calculation_type, roi_x1, roi_x2, roi_y1, roi_y2
    ):
        if calculation_type == CalculationConstants.NOISE_MODE:
            result = self.get_current_mid_mv_dll(
                image_path.encode("utf-8"),
                roi_x1,
                roi_x2,
                roi_y1,
                roi_y2,
                calculation_type,
            )
            self._check_error(result)

        else:

            result = self.get_current_mv_dll(
                image_path.encode("utf-8"),
                roi_x1,
                roi_x2,
                roi_y1,
                roi_y2,
                calculation_type,
            )
            self._check_error(result)
        # make sure the result is round to 1 decimal place
        result = round(result, 1)
        return result


    def get_current_mv_old(
        self, image_path, calculation_type, roi_x1, roi_x2, roi_y1, roi_y2
    ):
        result = self.get_current_mv_old_dll(
            image_path.encode("utf-8"),
            roi_x1,
            roi_x2,
            roi_y1,
            roi_y2,
            calculation_type,
        )
        self._check_error(result)
        # make sure the result is round to 1 decimal place
        result = round(result, 1)
        return result

    def get_current_cursor_level(
        self, image_path, calculation_type, roi_x1, roi_x2, roi_y1, roi_y2
    ):
        result = self.get_current_cursor_level_dll(
            image_path.encode("utf-8"),
            roi_x1,
            roi_x2,
            roi_y1,
            roi_y2,
            calculation_type,
        )
        self._check_error(result)
        # make sure the result is round to integer
        result = round(result)
        return result

    def classify_waveform(
        self,
        current_mv,
        current_sd,
        target,
        target_tolerance,
        flat_sd_threshold,
        calculation_type,
    ):
        result = self.classify_waveform_dll(
            current_mv,
            current_sd,
            target,
            target_tolerance,
            flat_sd_threshold,
            calculation_type
        )
        self._check_error(result)
        return result

    def compute_mv_cursor(self, image_path, mode):
        
        mv = self.get_current_mv(
                image_path,
                mode,
                CalculationConstants.ROI_COORDINATES_X1,
                CalculationConstants.ROI_COORDINATES_X2,
                CalculationConstants.ROI_COORDINATES_Y1,
                CalculationConstants.ROI_COORDINATES_Y2,
            )
        cursor = mv / CalculationConstants.CURSOR_TO_MV_FACTOR

        return mv, cursor

    def get_current_stdev(
            self,
            image_path,
            flat_pixel_count,
            roi_x1,
            roi_x2,
            roi_y1,
            roi_y2,
            calculation_type
    ):
        if calculation_type == CalculationConstants.WHITE_BALANCE_MODE:
            result = self.get_current_stdev_old_dll(
                image_path.encode("utf-8"),
                flat_pixel_count,
                roi_x1,
                roi_x2,
                roi_y1,
                roi_y2,
                CalculationConstants.NOISE_MODE
            )
        else:
            result = self.get_current_stdev_dll(
                image_path.encode("utf-8"),
                flat_pixel_count,
                roi_x1,
                roi_x2,
                roi_y1,
                roi_y2,
                calculation_type
            )
        self._check_error(result)
        # make sure the result is round to 1 decimal place
        return result