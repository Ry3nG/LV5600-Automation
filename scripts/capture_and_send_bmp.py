import asyncio
import logging
from time import sleep
from Constants import Constants
from commands import capture_command

async def capture_and_send_bmp(telnet_client, ftp_client, file_path = Constants.LOCAL_FILE_PATH_BMP):
    try:
        # send the capture command
        logging.info("Sending capture command...")
        response = await telnet_client.send_command(capture_command.take_snapshot())
        logging.info(f"Capture command response: {response}")
        
        # send the make command
        logging.info("Sending make command...")
        response = await telnet_client.send_command(capture_command.make("CAP_BMP"))
        logging.info(f"Make command response: {response}")
        
        # get the file            
        logging.info("Getting file from FTP server...")
        ftp_client.get_file(Constants.FTP_FILE_NAME_BMP, file_path)

        logging.info("File downloaded successfully.")
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")
