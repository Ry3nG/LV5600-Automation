import logging
from utils.telnet_client import TelnetClient
from utils.ftp_client import FTPClient
import asyncio
from Constants import Constants
import scripts.capture_and_send as capture_and_send
import scripts.change_preset as change_preset

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
        logging.info("Menu:")
        logging.info("1. Capture and send bmp")
        logging.info("2. Recall preset")
        logging.info("3. Quit")

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
                logging.info("Preset changed.")
            except Exception as e:
                logging.error(f"Failed to change preset: {e}")
        elif choice == "3":
            logging.info("Exiting.")
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