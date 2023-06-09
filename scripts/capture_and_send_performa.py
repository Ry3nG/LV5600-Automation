# main script: capture_and_send.py
from time import sleep
from utils.telnet_client_performa import TelnetClientPerforma
from utils.ftp_client import FTPClient
from utils.credential import Credential
from commands import capture_command, wfm_command
import logging
from Constants import Constants

# configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def run(ip_address_telnet, username_telnet, password_telnet, ip_address_ftp, username_ftp, password_ftp):
    logging.info("Starting script: capture_and_send_performa.py ...")

    # create a credential object
    telnet_credential = Credential(ip_address_telnet, username_telnet, password_telnet)
    ftp_credential = Credential(ip_address_ftp, username_ftp, password_ftp)
    logging.info("Credential object created ---")

    # create a telnet client object and connect
    client = TelnetClientPerforma(telnet_credential)
    await client.connect()
    logging.info("Telnet client object created and connected ---")

    # execute the command
    response = await client.send_command(capture_command.take_snapshot())
    logging.info("Response after taking snapshot: %s", response)

    response = await client.send_command(capture_command.make("CAP_BMP"))
    sleep(0.35)
    logging.info("Response after making CAP_BMP: %s", response)

    # create a ftp client object and download the file
    ftp_client = FTPClient(ftp_credential.ip_address, ftp_credential.username, ftp_credential.password)
    logging.info("FTP client object created ---")

    ftp_client.get_file(Constants.FTP_FILE_NAME_BMP, Constants.LOCAL_FILE_PATH_BMP)
    logging.info("File downloaded, check the file at %s", Constants.LOCAL_FILE_PATH_BMP)

    # close the telnet and ftp connection
    client.writer.close()
    client.reader.close()
    ftp_client.close()
    logging.info("Telnet and FTP connections closed ---")

    logging.info("Script: capture_and_send_performa.py completed -------------")
