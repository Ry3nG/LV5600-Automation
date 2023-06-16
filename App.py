import logging
from time import sleep
from utils.telnet_client import TelnetClient
from utils.ftp_client import FTPClient
import asyncio
from Constants import Constants
import scripts.capture_and_send as capture_and_send
import scripts.change_preset as change_preset

import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def main():
    # initialize and connect to telnet
    try:
        telnet_client = TelnetClient(
            Constants.IP_ADDRESS_TELNET,
            Constants.TELNET_PORT,
            Constants.USERNAME_TELNET,
            Constants.PASSWORD_TELNET,
        )
        await telnet_client.connect()
        logging.info("Connected to Telnet.")
    except Exception as e:
        logging.error(f"Failed to connect to Telnet: {e}")
        return

    # initialize and connect to ftp
    try:
        ftp_client = FTPClient(
            Constants.IP_ADDRESS_FTP, Constants.USERNAME_FTP, Constants.PASSWORD_FTP
        )
        logging.info("Connected to FTP.")
    except Exception as e:
        logging.error(f"Failed to connect to FTP: {e}")
        await telnet_client.close()
        return

    while True:
        print("Menu:")
        print("1. Capture and send bmp")
        print("2. Recall preset")
        print("3. Command-line")
        print("4. Capture multiple to path")
        print("5. Capture and analyze")
        print("6. Quit")

        choice = input("Enter your choice: ")

        if choice == "1":
            try:
                await capture_and_send.capture_and_send_bmp(telnet_client, ftp_client)
                logging.info("Captured and sent bmp.")
            except Exception as e:
                logging.error(f"Failed to capture and send bmp: {e}")
        elif choice == "2":
            preset_number = input("Enter preset number: ")
            try:
                await change_preset.run(telnet_client, preset_number)
                logging.info("Recalled preset: "+preset_number)
            except Exception as e:
                logging.error(f"Failed to change preset: {e}")
        elif choice == "3":
            while True:
                command = input("Enter command: ")
                if command == "exit":
                    break
                try:
                    await telnet_client.send_command(command)
                    logging.info("Command \""+command+"\" sent.")
                except Exception as e:
                    logging.error(f"Failed to send command: {e}")
        elif choice == "4":
            while True:
                number_of_captures = input("Enter number of captures: ")
                if number_of_captures == "exit":
                    break
                
                # loop through the number of captures
                # each time, append the number to the file name
                # and send the command
                for i in range(int(number_of_captures)):
                    file_name = "UnderSaturatedFar"+str(i)+".bmp"
                    file_path = "E:\\Data\\TestSet\\UnderSaturated" + "\\" + file_name
                    try:
                        await capture_and_send.capture_and_send_bmp_to_name_path(telnet_client, ftp_client, file_path)
                        logging.info("Sending number "+str(i+1)+" of "+number_of_captures+" bmps.")
                    except Exception as e:
                        logging.error(f"Failed to capture and send bmp: {e}")
        elif choice == "5":
            # step 1 first capture an image
            try:
                await capture_and_send.capture_and_send_bmp(telnet_client, ftp_client)
                logging.info("Captured and sent bmp.")
            except Exception as e:
                logging.error(f"Failed to capture and send bmp: {e}")
            # load model to analyze
            model_dir = "E:\\Model\\"
            model_name = 'model_20_20230615-134651.h5'
            image_dir = "E:\\Leader LV5600\\LV5600 Automation\\output\\CAP_BMP.bmp"
            buffer_dir = "E:\\Leader LV5600\\LV5600 Automation\\output\\buffer"
            img_width,img_height = 240,670
            x_start,x_end,y_start,y_end = 600,1270,60,300
            model = load_model(os.path.join(model_dir,model_name))
            os.makedirs(os.path.join(buffer_dir),exist_ok=True)
            img = cv2.imread(image_dir)
            img_roi = img[y_start:y_end,x_start:x_end]
            cv2.imwrite(buffer_dir+"\\buffer.bmp",img_roi)
            img = image.load_img(buffer_dir+"\\buffer.bmp",target_size=(img_width,img_height))
            img = image.img_to_array(img)
            img = np.expand_dims(img,axis=0)
            img = img/255
            prediction = model.predict(img)
            class_ = np.argmax(prediction,axis=1)
            if class_ == 0:
                class_name = "Just Saturated"
            elif class_ == 1:
                class_name = "Over Saturated"
            elif class_ == 2:
                class_name = "Under Saturated"
            else:
                class_name = "Unknown"
            print("The image is: "+class_name)

        elif choice == "6":
            logging.info("Exiting the applicaion.")
            try:
                ftp_client.close() 
                await telnet_client.close()
                logging.info("Closed connections.")
            except Exception as e:
                logging.error(f"Failed to close connections: {e}")
            break
        else:
            logging.info("Invalid choice.")


if __name__ == "__main__":
    asyncio.run(main())
