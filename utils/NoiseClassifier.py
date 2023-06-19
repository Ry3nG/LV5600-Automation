import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

class noiseClassifier:

    def __init__(self, lower_bound=0.5, upper_bound=1.5):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def get_red_pixels_relative_to_green(self, red_pixels, green_pixels, within_range):
        red_pixels_relative = []
        for green_x, green_y in green_pixels:
            for red_x, red_y in red_pixels:
                if within_range == ((green_x - 3 <= red_x <= green_x + 3) and (green_y - 3 <= red_y <= green_y + 3)):
                    red_pixels_relative.append((red_x, red_y))
        return red_pixels_relative

    def classify_image(self, file_path):
        img = cv2.imread(file_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        roi = img[150:780,400:1520]
        height, width = roi.shape[:2]
        red_pixels = [(x, y) for x in range(width) for y in range(height) if roi[y, x, 0] > roi[y, x, 1] and roi[y, x, 0] > roi[y, x, 2]]
        green_pixels = [(x, y) for x in range(width) for y in range(height) if roi[y, x, 1] > roi[y, x, 0] and roi[y, x, 1] > roi[y, x, 2]]

        red_peak = min(red_pixels, key=lambda coord: coord[1])
        green_corresponding = [coord for coord in green_pixels if coord[0] == red_peak[0]]

        if green_corresponding:
            green_corresponding = min(green_corresponding, key=lambda coord: abs(coord[1] - red_peak[1]))
        else:
            green_corresponding = None

        if green_corresponding is not None:
            green_pixels_around_center = [(x, y) for x, y in green_pixels if abs(x - green_corresponding[0]) <= 25 and abs(y - green_corresponding[1]) <= 25]

            red_pixels_near_green = self.get_red_pixels_relative_to_green(red_pixels, green_pixels_around_center, within_range=True)
            red_pixels_far_green = self.get_red_pixels_relative_to_green(red_pixels, green_pixels_around_center, within_range=False)

            num_red_pixels_above = len([coord for coord in red_pixels_near_green if coord[1] < green_corresponding[1]])
            num_red_pixels_below = len([coord for coord in red_pixels_near_green if coord[1] > green_corresponding[1]])

            ratio = num_red_pixels_above / (num_red_pixels_below + 1e-10)

            red_pixels_above_near, red_pixels_below_near = self.check_red_pixels_relative_to_green(red_pixels_near_green, green_corresponding)
            red_pixels_above_far, red_pixels_below_far = self.check_red_pixels_relative_to_green(red_pixels_far_green, green_corresponding)

        

            if red_pixels_above_near and red_pixels_below_near:
                if self.lower_bound <= ratio <= self.upper_bound:
                    class_ = "The image is just correct"
                elif ratio > self.upper_bound:
                    class_ = "The image is too high"
                elif ratio < self.lower_bound:
                    class_ = "The image is too low"
                else:
                    class_ = "The image does not meet any of the criteria"
            elif (red_pixels_above_near and not red_pixels_below_near) or (not red_pixels_near_green and red_pixels_above_far):
                class_ = "The image is too high"
            elif (not red_pixels_above_near and red_pixels_below_near) or (not red_pixels_near_green and red_pixels_below_far):
                class_ = "The image is too low"
            else:
                class_ = "The image does not meet any of the criteria"
            
            # plot in the same graph
            plt.scatter(*zip(*red_pixels), c='r', s=1)
            plt.scatter(*zip(*green_pixels_around_center), c='g', s=1)
            if red_pixels_near_green:
                plt.scatter(*zip(*red_pixels_near_green), c='b', s=1)
            plt.gca().invert_yaxis()
            plt.gca().set_aspect('equal', adjustable='box')
            plt.title(class_)
            plt.show()

            return class_
        else:
            return "There is no green pixel in the image, check manual settings"



    def check_red_pixels_relative_to_green(self, red_pixels_relative, green_corresponding):
        return any(red_y < green_corresponding[1] for red_x, red_y in red_pixels_relative), any(red_y > green_corresponding[1] for red_x, red_y in red_pixels_relative)
