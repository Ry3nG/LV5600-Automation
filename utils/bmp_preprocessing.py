import os
import cv2
import matplotlib.pyplot as plt
import sys
from Constants import Constants

# Define the path to the main directory
main_dir = ""

# Region of Interest (ROI) coordinates
x_start, x_end, y_start, y_end = Constants.ROI_COORDINATES

# Function to handle cropping
def handle_cropping(image_dir, cropped_dir):
    # Check if the cropped directory exists, if not, create it
    if not os.path.exists(cropped_dir):
        os.makedirs(cropped_dir)
        
    # Process each image file in the image directory
    for file in os.listdir(image_dir):
        # Check if the file is an image
        if file.endswith(".bmp") or file.endswith(".jpg") or file.endswith(".png"):
            # Read the image
            img = cv2.imread(os.path.join(image_dir, file))
            
            # Crop the image to the ROI
            img_cropped = img[y_start:y_end, x_start:x_end]
            
            # Save the cropped image in the cropped directory
            cv2.imwrite(os.path.join(cropped_dir, file), img_cropped)

def main():
    # Loop through each subdirectory in the main directory
    for subdir in os.listdir(main_dir):
        subdir_path = os.path.join(main_dir, subdir)

        # Check if the path is a directory
        if os.path.isdir(subdir_path):
            # Define the paths to the image directory and the cropped directory
            image_dir = subdir_path
            cropped_dir = os.path.join(subdir_path, "cropped")

            # Handle the cropping for this directory
            handle_cropping(image_dir, cropped_dir)

if __name__ == "__main__":
    main()
