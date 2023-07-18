import unittest
import numpy as np
from unittest import mock

from tasks.calculation_tasks import CalculationTasks
from constants import PreprocessingConstants, LV5600Constants

class TestCalculationTasks(unittest.TestCase):
    def setUp(self):
        self.image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.image[50, 50] = [50, 255, 255]  # cyan pixel in the middle

    @mock.patch('tasks.calculation_tasks.logging')  
    def test_calculate_middle_cyan_y(self, mock_logging):
        mid_cyan_y = CalculationTasks.calculate_middle_cyan_y(self.image, "min")
        self.assertEqual(mid_cyan_y, 50)
        mid_cyan_y = CalculationTasks.calculate_middle_cyan_y(self.image, "mean")
        self.assertEqual(mid_cyan_y, 50)

    @mock.patch('tasks.calculation_tasks.logging') 
    def test_classify_mv_level(self, mock_logging):
        self.assertEqual(CalculationTasks.classify_mv_level(100, 100, 0.1), "pass")
        self.assertEqual(CalculationTasks.classify_mv_level(112, 100, 0.1), "high")
        self.assertEqual(CalculationTasks.classify_mv_level(88, 100, 0.1), "low")

    @mock.patch('tasks.calculation_tasks.cv2') 
    @mock.patch('tasks.calculation_tasks.AppConfig') 
    @mock.patch('tasks.calculation_tasks.os')  
    async def test_preprocess_and_get_mid_cyan(self, mock_os, mock_app_config, mock_cv2):
        mock_app_config().get_local_file_path.return_value = "/path/to/local/files"
        mock_os.path.join.return_value = "/path/to/local/files/file.bmp"
        mock_cv2.imread.return_value = self.image
        mid_cyan_y = await CalculationTasks.preprocess_and_get_mid_cyan("SAT")
        self.assertEqual(mid_cyan_y, 50)

    @mock.patch('tasks.calculation_tasks.logging') 
    def test_get_cursor_and_mv(self, mock_logging):
        cyan_y = 25
        total_y = PreprocessingConstants.ROI_COORDINATES_Y2 - PreprocessingConstants.ROI_COORDINATES_Y1
        max_cursor_value = LV5600Constants.MAX_CURSOR_VALUE
        cursor_level = (1 - cyan_y / float(total_y)) * max_cursor_value
        cursor_level = round(cursor_level, 0)

        cursor, mv = CalculationTasks.get_cursor_and_mv(cyan_y)
        self.assertEqual(cursor, cursor_level)


if __name__ == "__main__":
    unittest.main()
