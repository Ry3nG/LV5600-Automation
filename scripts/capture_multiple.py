"""
This module provides a function to capture multiple BMP images and send them over FTP.

Functions:
- capture_multiple: captures multiple BMP images and sends them over FTP.
"""
import logging
import os
from .capture_and_send_bmp import capture_and_send_bmp

async def capture_multiple(telnet_client, ftp_client):
    """
    Captures multiple BMP images and sends them over FTP.

    Args:
    - telnet_client: a Telnet client object.
    - ftp_client: an FTP client object.

    Returns:
    - None
    """
    while True:
        number_of_captures = input("Enter number of captures: (type \"exit\" to exit)")
        if number_of_captures == "exit":
            break

        if not number_of_captures.isdigit() or int(number_of_captures) <= 0:
            print("Invalid input. Please enter a positive integer.")
            continue

        # Ask user for base file name and directory path
        base_file_name = input("Enter base file name: ")
        directory_path = input("Enter directory path: ")

        # Validate the directory path
        if not os.path.isdir(directory_path):
            print("The provided directory path does not exist.")
            continue

        # loop through the number of captures
        # each time, append the number to the base file name
        # and send the command
        for i in range(int(number_of_captures)):
            file_name = f"{base_file_name}{str(i)}.bmp"
            file_path = os.path.join(directory_path, file_name)

            try:
                await capture_and_send_bmp(telnet_client, ftp_client, file_path)
                logging.info(f"Sending number {i + 1} of {number_of_captures} bmps.")
            except Exception as error:  # Replace Exception with the types of exceptions you want to handle
                logging.error(f"Failed to capture and send bmp: {error}")
                # Add error handling code here, if necessary
