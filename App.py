import logging
from time import sleep
from utils.telnet_client import TelnetClient
from utils.ftp_client import FTPClient
from utils.DebugConsoleController import DebugConsoleController
from utils.NoiseClassifier import noiseClassifier
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

    # initialize and connect to debug console
    try:
        debugConsoleController = DebugConsoleController()
        if not debugConsoleController.activate():
            return
        logging.info("Connected to Debug Console.")
    except Exception as e:
        logging.error(f"Failed to connect to Debug Console: {e}")
        await telnet_client.close()
        return

    while True:
        print("Menu:")
        print("1. Capture and send bmp")
        print("2. Recall preset")
        print("3. Command-line")
        print("4. Capture multiple to path")
        print("5. Capture and classify Saturation")
        print("6. Auto adjust")
        print("7. Auto collect dataset")
        print("8. Capture and classify Noise")
        print("9. Adjust Brightness using Debug Console")
        print("0. Quit")

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
                logging.info("Recalled preset: " + preset_number)
            except Exception as e:
                logging.error(f"Failed to change preset: {e}")
        elif choice == "3":
            while True:
                command = input("Enter command: ")
                if command == "exit":
                    break
                try:
                    await telnet_client.send_command(command)
                    logging.info('Command "' + command + '" sent.')
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
                    file_name = "UnderSaturatedFar" + str(i) + ".bmp"
                    file_path = "E:\\" + "\\" + file_name
                    try:
                        await capture_and_send.capture_and_send_bmp_to_name_path(
                            telnet_client, ftp_client, file_path
                        )
                        logging.info(
                            "Sending number "
                            + str(i + 1)
                            + " of "
                            + number_of_captures
                            + " bmps."
                        )
                    except Exception as e:
                        logging.error(f"Failed to capture and send bmp: {e}")
        elif choice == "5":
            # recall preset 1
            try:
                await change_preset.run(telnet_client, "1")
                logging.info("Recalled preset: 1")
            except Exception as e:
                logging.error(f"Failed to change preset: {e}")

            sleep(1)
            try:
                await capture_and_send.capture_and_send_bmp(telnet_client, ftp_client)
                logging.info("Captured and sent bmp.")
            except Exception as e:
                logging.error(f"Failed to capture and send bmp: {e}")
            # load model to analyze
            model_dir = "E:\\Model\\"
            model_name = "model_20_20230615-134651.h5"
            image_dir = "E:\\Leader LV5600\\LV5600 Automation\\output\\CAP_BMP.bmp"
            buffer_dir = "E:\\Leader LV5600\\LV5600 Automation\\output\\buffer"
            img_width, img_height = 240, 670
            x_start, x_end, y_start, y_end = 600, 1270, 60, 300
            model = load_model(os.path.join(model_dir, model_name))
            os.makedirs(os.path.join(buffer_dir), exist_ok=True)
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
            # create a txt file to save the result
            with open(
                "E:\\Leader LV5600\\LV5600 Automation\\output\\result.txt", "w"
            ) as f:
                f.write(class_name)
        elif choice == "6":
            # recall preset 1
            try:
                await change_preset.run(telnet_client, "1")
                logging.info("Recalled preset: 1")
            except Exception as e:
                logging.error(f"Failed to change preset: {e}")

            print("Set brightness to 10 first")
            current_level = input("Enter current brightness level: ")
            target_level = 10
            debugConsoleController.tune_to_target_level(target_level,int(current_level))

            sleep(1)

            # Load model
            model_dir = "E:\\Model\\"
            model_name = "model_20_20230615-134651.h5"
            image_dir = "E:\\Leader LV5600\\LV5600 Automation\\output\\CAP_BMP.bmp"
            buffer_dir = "E:\\Leader LV5600\\LV5600 Automation\\output\\buffer"
            img_width, img_height = 240, 670
            x_start, x_end, y_start, y_end = 600, 1270, 60, 300
            model = load_model(os.path.join(model_dir, model_name))
            os.makedirs(os.path.join(buffer_dir), exist_ok=True)

            class_name = None
            while class_name != "Just Saturated":
                # step 1 first capture an image
                try:
                    await capture_and_send.capture_and_send_bmp(
                        telnet_client, ftp_client
                    )
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
        elif choice == "7":
            print("Please set to just saturated manually, press enter to continue.")
            input()
            num_each_class = int(input("Enter capture number of each class: "))
            # make a directory
            os.makedirs(os.path.join("E:\\RDI Dataset"), exist_ok=True)
            dataset_dir = "E:\\RDI Dataset"
            # create 3 folders for each class
            os.makedirs(os.path.join(dataset_dir, "just_saturated"), exist_ok=True)
            os.makedirs(os.path.join(dataset_dir, "over_saturated"), exist_ok=True)
            os.makedirs(os.path.join(dataset_dir, "under_saturated"), exist_ok=True)
            just_saturated_dataset_dir = os.path.join(dataset_dir, "just_saturated")
            over_saturated_dataset_dir = os.path.join(dataset_dir, "over_saturated")
            under_saturated_dataset_dir = os.path.join(dataset_dir, "under_saturated")

            current_level = int(input("Enter current brightness level: "))
            just_saturate_level_lower_bound = int(input("Enter lower bound of just saturate level: "))
            just_saturate_level_upper_bound = int(input("Enter upper bound of just saturate level: "))

            light_level_offset = int(input("Enter light level offset: "))

            undersaturated_lower_bound = current_level - light_level_offset
            undersaturated_upper_bound = just_saturate_level_lower_bound - 1

            oversaturated_lower_bound = just_saturate_level_upper_bound + 1
            oversaturated_upper_bound = current_level + light_level_offset

            # capture just saturated images
            print("Capturing just saturated images...")
            print("Current level: " + str(current_level))
            print("Incrementing from lower bound to upper bound...")
            debugConsoleController.tune_to_target_level(just_saturate_level_lower_bound, current_level)
            current_level = just_saturate_level_lower_bound # always remember to update current level
            while(current_level <= just_saturate_level_upper_bound):
                for i in range(num_each_class):
                    try:
                        await capture_and_send.capture_and_send_bmp_to_name_path(
                            telnet_client, ftp_client, just_saturated_dataset_dir + "\\just_saturated_" + "light_level_" + str(current_level) + "_" + str(i) + ".bmp"
                        )
                    except Exception as e:
                        logging.error(f"Failed to capture and send bmp: {e}")
                    
                    
                debugConsoleController.tune_up_light()
                current_level += 1
            print("Done capturing just saturated images.")
            print("current level: " + str(current_level))

            # capture over saturated images
            print("Capturing over saturated images...")
            print("Current level: " + str(current_level))
            print("Incrementing from lower bound to upper bound...")
            debugConsoleController.tune_to_target_level(oversaturated_lower_bound, current_level)
            current_level = oversaturated_lower_bound # always remember to update current level
            while(current_level <= oversaturated_upper_bound):
                for i in range(num_each_class):
                    try:
                        await capture_and_send.capture_and_send_bmp_to_name_path(
                            telnet_client, ftp_client, over_saturated_dataset_dir + "\\over_saturated_" + "light_level_" + str(current_level) + "_" + str(i) + ".bmp"
                        )
                    except Exception as e:
                        logging.error(f"Failed to capture and send bmp: {e}")
                    
                    
                debugConsoleController.tune_up_light()
                current_level += 1
            print("Done capturing over saturated images.")
            print("current level: " + str(current_level))

            # capture under saturated images
            print("Capturing under saturated images...")
            print("Current level: " + str(current_level))
            print("Incrementing from lower bound to upper bound...")
            debugConsoleController.tune_to_target_level(undersaturated_lower_bound, current_level)
            current_level = undersaturated_lower_bound # always remember to update current level
            while(current_level <= undersaturated_upper_bound):
                for i in range(num_each_class):
                    try:
                        await capture_and_send.capture_and_send_bmp_to_name_path(
                            telnet_client, ftp_client, under_saturated_dataset_dir + "\\under_saturated_" + "light_level_" + str(current_level) + "_" + str(i) + ".bmp"
                        )
                    except Exception as e:
                        logging.error(f"Failed to capture and send bmp: {e}")
                    
                    
                debugConsoleController.tune_up_light()
                current_level += 1
            print("Done capturing under saturated images.")
            print("current level: " + str(current_level))

            print("Done capturing images.")

            
        elif choice == "8":
            '''
            # recall preset 5
            try:
                await change_preset.run(telnet_client, 5)
                logging.info("Recalled preset 5.")
            except Exception as e:
                logging.error(f"Failed to recall preset 5: {e}")
            sleep(1)
            '''

            try:
                await capture_and_send.capture_and_send_bmp(telnet_client, ftp_client)
                logging.info("Captured and sent bmp.")
            except Exception as e:
                logging.error(f"Failed to capture and send bmp: {e}")
            NoiseClassifier = noiseClassifier()
            file_path = "E:\\Leader LV5600\\LV5600 Automation\\output\\CAP_BMP.bmp"
            result = NoiseClassifier.classify_image(file_path)
            print(result)

        elif choice == "9":
            target_level = input("Enter target level: ")
            current_level = input("Enter current level: ")

            debugConsoleController.tune_to_target_level(int(target_level), int(current_level))

        elif choice == "0":
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
