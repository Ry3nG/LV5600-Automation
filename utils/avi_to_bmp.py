import cv2
import os

def convert_video_to_bmp():
    # The path to your videos
    video_path = "E:\\RDI Dataset\\"

    for i in range(1, 101):
        # Create folder name
        folder_name = f"Light Level {str(i).zfill(2)}"
        folder_path = os.path.join(video_path, folder_name)

        # Create folder if not exists
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Create video file path
        video_file = os.path.join(video_path, f"Untitled {str(i).zfill(2)}.mov")
        print(video_file)
        # Open video file
        vidcap = cv2.VideoCapture(video_file)
        success, image = vidcap.read()
        print("Success: ", success)
        print(f"Converting {folder_name}...")
        count = 0
        while success:
            # Save frame as BMP file with new naming convention
            cv2.imwrite(os.path.join(folder_path, f"light_level_{str(i).zfill(2)}_{str(count + 1)}.bmp"), image)
            
            success, image = vidcap.read()
            print(f"Frame {count + 1} saved")
            count += 1