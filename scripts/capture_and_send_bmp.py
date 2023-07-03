"""
This module contains a function to capture a snapshot from a telnet client and send it to an FTP server as a BMP file.
"""

import logging
from Constants import Constants
from commands import capture_command

async def capture_and_send_bmp(telnet_client, ftp_client, file_path = Constants.LOCAL_FILE_PATH_BMP):
    """
    Capture a snapshot from a telnet client and send it to an FTP server as a BMP file.

    Args:
        telnet_client (TelnetClient): The telnet client to capture the snapshot from.
        ftp_client (FTPClient): The FTP client to send the BMP file to.
        file_path (str): The local file path to save the BMP file to. Defaults to Constants.LOCAL_FILE_PATH_BMP.

    Returns:
        list: A list of responses from the telnet client for each command sent.
    """
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
