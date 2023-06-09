from utils.telnet_client import TelnetClient
from utils.credential import Credential
from commands import capture_command
from utils.ftp_client import FTPClient
from time import sleep
import logging


# configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def run(ip_address, username, password):
    logging.info("Starting script: capture_and_send.py ...")

    # create a credential object
    uut_credential = Credential(ip_address, username, password)
    logging.info("1. Credential object created ---")

    # create a telnet client object
    client = TelnetClient(uut_credential)
    logging.info("2. Telnet client object created ---")

    # execute the command
    await client.send_command(capture_command.take_snapshot())
    logging.info("3. Take snapshot command executed ---")
    await client.send_command(capture_command.make("CAP_BMP"))
    sleep(0.5)
    logging.info("4. Make command executed ---")

    # create a ftp client object
    ftp_client = FTPClient(uut_credential.ip_address, uut_credential.username, uut_credential.password)
    logging.info("5. FTP client object created ---")

    # get the file
    ftp_file_name = "cap_bmp.bmp"
    local_file_path = "E:\\Leader LV5600\\LV5600 Automation with Telnet\\output\\CAP_BMP.bmp"
    ftp_client.get_file(ftp_file_name, local_file_path)
    logging.info("6. File downloaded, check the file at %s", local_file_path)

    # close the ftp connection
    ftp_client.close()
    logging.info("7. FTP connection closed ---")

    logging.info("Script: capture_and_send.py completed -------------")