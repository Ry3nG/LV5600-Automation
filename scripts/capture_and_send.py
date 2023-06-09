from utils.telnet_client import TelnetClient
from utils.credential import Credential
from commands import capture_command, wfm_command
from utils.ftp_client import FTPClient
from time import sleep
import logging
from Constants import Constants

# configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def run(ip_address_telnet, username_telnet, password_telnet, ip_address_ftp, username_ftp, password_ftp):
    logging.info("Starting script: capture_and_send.py ...")

    # create a credential object
    telnet_credential = Credential(ip_address_telnet, username_telnet, password_telnet)
    ftp_credential = Credential(ip_address_ftp, username_ftp, password_ftp)
    logging.info("1. Credential object created ---")

    # create a telnet client object
    client = TelnetClient(telnet_credential)
    logging.info("2. Telnet client object created ---")

    # make sure to go to Waveform Monitor page
    await client.send_command(wfm_command.goto_wfm_page())
    sleep(0.2)

    # execute the command
    await client.send_command(capture_command.take_snapshot())
    logging.info("3. Take snapshot command executed ---")
    await client.send_command(capture_command.make("CAP_BMP"))
    sleep(0.4)
    logging.info("4. Make command executed ---")

    # create a ftp client object
    ftp_client = FTPClient(ftp_credential.ip_address, ftp_credential.username, ftp_credential.password)
    logging.info("5. FTP client object created ---")

    # get the file
    ftp_client.get_file(Constants.FTP_FILE_NAME_BMP, Constants.LOCAL_FILE_PATH_BMP)
    logging.info("6. File downloaded, check the file at %s", Constants.LOCAL_FILE_PATH_BMP)

    # close the ftp connection
    ftp_client.close()
    logging.info("7. FTP connection closed ---")

    logging.info("Script: capture_and_send.py completed -------------")