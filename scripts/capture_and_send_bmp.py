import asyncio
import logging
from time import sleep
from Constants import Constants
from commands import capture_command

# does not handle the error here, propagate it to the caller
async def capture_and_send_bmp(telnet_client, ftp_client, file_path = Constants.LOCAL_FILE_PATH_BMP):
    response_log_list = []
    # send the capture command
    #logging.info("Sending capture command...")
    response = await telnet_client.send_command(capture_command.take_snapshot())
    response_log_list.append(response)
    
    # send the make command
    #logging.info("Sending make command...")
    response = await telnet_client.send_command(capture_command.make("CAP_BMP"))
    response_log_list.append(response)
    
    # get the file            
    #logging.info("Getting file from FTP server...")
    ftp_client.get_file(Constants.FTP_FILE_NAME_BMP, file_path)
    logging.info("File downloaded successfully.")

    return response_log_list

