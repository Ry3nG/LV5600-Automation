from .capture_and_send_bmp import capture_and_send_bmp
from .recall_preset import recall_preset
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import cv2
import os
import logging
from time import sleep
from Constants import Constants

async def adjust_lighting(telnet_client, ftp_client, debugConsoleController, current_level):
    # recall preset 1
    try:
        await recall_preset(telnet_client, "1")
        logging.info("Recalled preset: 1")
    except Exception as e:
        logging.error(f"Failed to change preset: {e}")

    #print("Set brightness to 10 first")
    #target_level = 10
    #debugConsoleController.tune_to_target_level(target_level,int(current_level))

    sleep(1)

    # Load model
    model_dir =  Constants.MODEL_PATH
    model_name = Constants.WLI_MODEL_NAME
    image_dir = Constants.LOCAL_FILE_PATH_BMP
    buffer_dir = Constants.LOCAL_BUFFER_PATH
    img_width, img_height = 240, 670
    x_start, x_end, y_start, y_end = 600, 1270, 60, 300
    model = load_model(os.path.join(model_dir, model_name))
    os.makedirs(os.path.join(buffer_dir), exist_ok=True)

    class_name = None
    while class_name != "Just Saturated":
        # step 1 first capture an image
        try:
            await capture_and_send_bmp(telnet_client, ftp_client)
            logging.info("Captured and sent bmp.")
        except Exception as e:
            logging.error(f"Failed to capture and send bmp: {e}")

        img = cv2.imread(image_dir)
        img_roi = img[y_start:y_end, x_start:x_end]
        cv2.imwrite(buffer_dir + "\\buffer.bmp", img_roi)
        img = image.load_img(
            buffer_dir + "\\buffer.bmp", target_size=(img_width, img_height)
        )
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = img / 255
        prediction = model.predict(img)
        class_ = np.argmax(prediction, axis=1)

        if class_ == 0:
            class_name = "Just Saturated"
            print("The image is: " + class_name)
        elif class_ == 1:
            class_name = "Over Saturated"
            print("Turning down the light.")
            # use debugConsole to turn down the light
            debugConsoleController.tune_down_light()
        elif class_ == 2:
            class_name = "Under Saturated"
            print("Turning up the light.")
            # use debugConsole to turn up the light
            debugConsoleController.tune_up_light()
        else:
            class_name = "Unknown"
            logging.error("Unknown class.")