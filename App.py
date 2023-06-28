import logging
import asyncio
from utils.telnet_client import TelnetClient
from utils.ftp_client import FTPClient
from utils.debug_console_controller import DebugConsoleController

from Constants import Constants

from scripts.capture_and_send_bmp import capture_and_send_bmp
from scripts.recall_preset import recall_preset
from scripts.send_command_terminal import send_command
from scripts.capture_multiple import capture_multiple

from scripts.tune_to_target_light_level import tune_to_target_level
from scripts.lv5600_initialization import (
    lv5600_initialization,
    LV5600InitializationError,
)
from scripts.display_saturation_result import display_result
from scripts.auto_tuning_use_peak_pixel import (
    auto_adjust,
    white_balance_auto_detect,
    noise_level_auto_adjust,
)

# configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def cleanup(telnet_client, ftp_client=None):
    try:
        if telnet_client:
            await telnet_client.close()
    except Exception as e:
        logging.error(f"Error while closing Telnet connection: {e}")

    try:
        if ftp_client:
            ftp_client.close()
    except Exception as e:
        logging.error(f"Error while closing FTP connection: {e}")


def log_error(error_message, error_severity, error_log_list):
    logging.error(error_message)
    if error_severity == "critical":
        logging.error("Critical error, exiting the application.")
    elif error_severity == "non-critical":
        logging.error("None critical error, continuing...")
    logging.info("Displaying the log list:")
    for log in error_log_list:
        logging.info(log)
    error_log_list.clear()


async def handle_noise_level_auto_adjust(
    telnet_client, ftp_client, debugConsoleController, n1_mv_value
):
    if n1_mv_value != -1:
        return await noise_level_auto_adjust(
            telnet_client, ftp_client, debugConsoleController, n1_mv_value
        )
    else:
        print("Please run option 9 first")


async def main():
    cleanup_flag = False
    logging.info("All modules imported successfully.")
    logging.info("Starting the application.")
    # initialize and connect to telnet
    telnet_client = None
    try:
        telnet_client = TelnetClient(
            Constants.IP_ADDRESS_TELNET,
            Constants.TELNET_PORT,
            Constants.USERNAME_TELNET,
            Constants.PASSWORD_TELNET,
        )
        if not await telnet_client.is_connected():
            await telnet_client.connect()
        logging.info("Connected to Telnet.")
    except Exception as e:
        logging.error(f"Failed to connect to Telnet: {e}")
        await cleanup(telnet_client)
        return

    # initialize and connect to ftp
    try:
        ftp_client = FTPClient(
            Constants.IP_ADDRESS_FTP, Constants.USERNAME_FTP, Constants.PASSWORD_FTP
        )
        if not ftp_client.is_connected():
            ftp_client.connect()
        logging.info("Connected to FTP.")
    except Exception as e:
        logging.error(f"Failed to connect to FTP: {e}")
        await cleanup(telnet_client)
        return

    # initialize and connect to debug console
    try:
        debugConsoleController = DebugConsoleController()
        if not debugConsoleController.activate():
            return
        logging.info("Connected to Debug Console.")
    except Exception as e:
        logging.error(f"Failed to connect to Debug Console: {e}")
        await cleanup(telnet_client, ftp_client)
        return

    # initialize lv5600
    try:
        await lv5600_initialization(telnet_client)
        logging.info("LV5600 initialized.")
    except LV5600InitializationError as e:
        logging.error("LV5600 Initialization error: " + str(e))
        await cleanup(telnet_client, ftp_client)
        return
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        await cleanup(telnet_client, ftp_client)
        return

    menu_options = {
        "1": lambda: capture_and_send_bmp(
            telnet_client, ftp_client
        ),  # does not have return value
        "2": lambda: recall_preset(
            telnet_client, input("Enter preset number: ")
        ),  # does not have return value
        "3": lambda: send_command(telnet_client),  # does not have return value
        "4": lambda: capture_multiple(
            telnet_client, ftp_client
        ),  # does not have return value
        "5": lambda: display_result(
            telnet_client, ftp_client
        ),  # does not have return value
        "6": lambda: auto_adjust(
            telnet_client,
            ftp_client,
            debugConsoleController,
            int(input("Enter current light level: ")),
            mode="SAT",
            target=769.5,
            target_high_threshold=769.5,
            target_low_threshold=766.5,
            use_poly_prediction=True,
            jump_threshold=700,
        ),  # does not have return value
        "7": lambda: handle_noise_level_auto_adjust(
            telnet_client, ftp_client, debugConsoleController, n1_mv_value
        ),  # does not have return value
        "8": lambda: tune_to_target_level(
            debugConsoleController
        ),  # does not have return value
        "9": lambda: white_balance_auto_detect(
            telnet_client, ftp_client
        ),  # return the value of n1_mv
        "10": lambda: lv5600_initialization(
            telnet_client
        ),  # does not have return value
    }

    n1_mv_value = -1
    while True:
        print("Menu:")
        print("1. Capture and send bmp")
        print("2. Recall preset")
        print("3. Command-line")
        print("4. Capture multiple to path")
        print("5. Capture and classify Saturation")
        print("6. Auto adjust lighting based on saturation level")
        print("7. Auto adjust to N1+-20")
        print("8. Adjust Brightness using Debug Console")
        print("9. Auto White Balance")
        print("10. Initialize LV5600")
        print("0. Quit")

        choice = input("Enter your choice: ")
        if choice not in menu_options and choice != "0":
            print("Invalid choice! Please try again.")
            continue
        if choice == "0":
            logging.info("Exiting the application.")
            await cleanup(telnet_client, ftp_client)
            cleanup_flag = True
            break

        try:
            if choice == "9":
                n1_mv_value = await menu_options[choice]()
            else:
                await menu_options[choice]()
        except LV5600InitializationError as e:
            log_error("LV5600 Initialization error: " + str(e), "critical", [])
            await cleanup(telnet_client, ftp_client)
            return
        except Exception as e:
            log_error(f"An unexpected error occurred: {e}", "critical", [])
            await cleanup(telnet_client, ftp_client)
            return
        input(f"\nPress Enter to continue...")

    if not cleanup_flag:
        await cleanup(telnet_client, ftp_client)


if __name__ == "__main__":
    asyncio.run(main())
