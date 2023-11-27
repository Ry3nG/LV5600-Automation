import os
from Constants import CalculationConstants
import Constants
import cv2



image_path = "C:\\LV5600-OCB_Automation\\snapshot.bmp"
img = cv2.imread(image_path)
roi_x1 = CalculationConstants.ROI_COORDINATES_X1
roi_x2 = CalculationConstants.ROI_COORDINATES_X2
roi_y1 = CalculationConstants.ROI_COORDINATES_Y1
roi_y2 = CalculationConstants.ROI_COORDINATES_Y2

# display the image of ROi
cv2.rectangle(img, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)

cv2.imshow("Image", img)
cv2.waitKey(0)