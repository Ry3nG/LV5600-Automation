import logging
from time import sleep
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
        print("Menu:")
        print("1. Capture and send bmp")
        print("2. Recall preset")
        print("3. Command-line")
        print("4. Capture multiple to path")
        print("5. Quit")

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
