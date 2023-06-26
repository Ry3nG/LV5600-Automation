import logging
import asyncio

from time import sleep
from utils.telnet_client import TelnetClient
from utils.ftp_client import FTPClient
from utils.debug_console_controller import DebugConsoleController

from Constants import Constants

from scripts.capture_and_send_bmp import capture_and_send_bmp
from scripts.recall_preset import recall_preset
from scripts.send_command_terminal import send_command
from scripts.capture_multiple import capture_multiple
#from scripts.capture_classify_show import capture_classify_show
#from scripts.auto_adjust_lighting import adjust_lighting
from scripts.classify_noise import classify_noise
from scripts.tune_to_target_light_level import tune_to_target_level
from scripts.lv5600_initialization import lv5600_initialization, LV5600InitializationError
from scripts.auto_white_balance import auto_white_balance
from scripts.capture_and_classify_with_initialize import auto_adjust, display_result
# configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def main():
    logging.info("All modules imported successfully.")
    logging.info("Starting the application.")
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
    
    # initialize lv5600
    try:
        await lv5600_initialization(telnet_client)
        logging.info("LV5600 initialized.")
    except LV5600InitializationError as e:
        logging.error("LV5600 Initialization error: "+str(e))
        await telnet_client.close()
        return
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
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
        print("7. Capture and classify Noise")
        print("8. Adjust Brightness using Debug Console")
        print("9. Auto White Balance")
        print("10. Initialize LV5600")
        print("0. Quit")
        

        choice = input("Enter your choice: ")

        if choice == "1":
            await capture_and_send_bmp(telnet_client, ftp_client)

        elif choice == "2":
            preset_number = input("Enter preset number: ")
            await recall_preset(telnet_client, preset_number)

        elif choice == "3":
            await send_command(telnet_client)

        elif choice == "4":
            await capture_multiple(telnet_client, ftp_client)

        elif choice == "5":
            await display_result(telnet_client, ftp_client)
        elif choice == "6":
            current_brightness = int(input("Enter current brightness: "))
            await auto_adjust(telnet_client, ftp_client,debugConsoleController,current_brightness)

        elif choice == "7":
            preset_number = 5
            file_path = Constants.LOCAL_FILE_PATH_BMP
            result = await classify_noise(
                telnet_client, ftp_client, preset_number, file_path
            )
            print(result)

        elif choice == "8":
            tune_to_target_level(debugConsoleController)
        
        elif choice == "9":
            try:
                await auto_white_balance(telnet_client,ftp_client)
            except Exception as e:
                logging.error(f"An unexpected error occurred during auto white balance: {e}")
                await telnet_client.close()

                return

        elif choice == "0":
            logging.info("Exiting the applicaion.")
            try:
                ftp_client.close()
                await telnet_client.close()
                logging.info("Closed connections.")
            except Exception as e:
                logging.error(f"Failed to close connections: {e}")
            break
            
        elif choice == "10":
            try:
                await lv5600_initialization(telnet_client)
                logging.info("LV5600 initialized.")
            except LV5600InitializationError as e:
                logging.error("LV5600 Initialization error: "+str(e))
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                await telnet_client.close()
                return
        else:
            logging.info("Invalid choice.")


if __name__ == "__main__":
    asyncio.run(main())
