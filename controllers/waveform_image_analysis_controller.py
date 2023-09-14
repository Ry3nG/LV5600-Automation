from ctypes import c_char_p, c_int, c_float, cdll
import logging


class WaveformImageAnalysisController:
    DLL_error_code = {
        -100: "Unknown error",
        -101: "Image could not be loaded",
        -102: "No cyan pixel found",
        -103: "Invalid parameter",
    }

    def __init__(self):
        self.myDLL = cdll.LoadLibrary("lib\\WaveformImageAnalysisLib.dll")
        if not self.myDLL:
            raise Exception("Could not load DLL")
        else:
            logging.info("Waveform Image Analysis DLL loaded successfully")

        self.get_current_mv_dll = self.myDLL.GetCurrentMV
        self.get_current_mv_dll.argtypes = [c_char_p, c_int, c_int, c_int, c_int, c_int]
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
            c_char_p,
            c_float,
            c_float,
            c_float,
            c_float,
            c_int,
            c_int,
            c_int,
            c_int,
            c_int,
        ]
        self.classify_waveform_dll.restype = c_int

    def _check_error(self, result):
        if result in self.DLL_error_code:
            logging.error(self.DLL_error_code[result])
            raise Exception(self.DLL_error_code[result])

    def get_current_mv(
        self, image_path, calculation_type, roi_x1, roi_x2, roi_y1, roi_y2
    ):
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
        image_path,
        target,
        target_tolerance,
        flat_pixel_count,
        flat_sd_threshold,
        roi_x1,
        roi_x2,
        roi_y1,
        roi_y2,
        calculation_type,
    ):
        result = self.classify_waveform_dll(
            image_path.encode("utf-8"),
            target,
            target_tolerance,
            flat_pixel_count,
            flat_sd_threshold,
            roi_x1,
            roi_x2,
            roi_y1,
            roi_y2,
            calculation_type,
        )
        self._check_error(result)
        return result
