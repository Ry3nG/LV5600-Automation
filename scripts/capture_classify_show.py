from .capture_and_send_bmp import capture_and_send_bmp
from .recall_preset import recall_preset
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import logging
from time import sleep
from Constants import Constants

async def capture_classify_show(telnet_client, ftp_client):
    try:
        await capture_and_send_bmp(telnet_client, ftp_client)
        logging.info("Captured and sent bmp.")
    except Exception as e:
        logging.error(f"Failed to capture and send bmp: {e}")
        
    # load model to analyze
    model_dir = Constants.MODEL_PATH
    model_name = Constants.WLI_MODEL_NAME
    image_dir = Constants.LOCAL_FILE_PATH_BMP
    buffer_dir = Constants.LOCAL_BUFFER_PATH
    img_width, img_height = Constants.CNN_IMAGE_SIZE
    x_start, x_end, y_start, y_end = Constants.ROI_COORDINATES
    model = load_model(os.path.join(model_dir, model_name))
    os.makedirs(os.path.join(buffer_dir), exist_ok=True)
    img = cv2.imread(image_dir)
    img_roi = img[y_start:y_end, x_start:x_end]
    cv2.imwrite(buffer_dir + "\\buffer.bmp", img_roi)
    img = image.load_img(
        buffer_dir + "\\buffer.bmp", target_size=(img_height, img_width)
    )
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = img / 255
    prediction = model.predict(img)
    class_ = np.argmax(prediction, axis=1)
    if class_ == 0:
        class_name = "Just Saturated"
    elif class_ == 1:
        class_name = "Over Saturated"
    elif class_ == 2:
        class_name = "Under Saturated"
    else:
        class_name = "Unknown"

    # plot the image, the prediction, and relevant information
    plt.imshow(img[0])
    plt.axis("off")
    plt.title(class_name)
    plt.show()

    print("The image is: " + class_name)
