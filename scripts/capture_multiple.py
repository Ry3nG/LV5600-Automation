from .capture_and_send_bmp import capture_and_send_bmp
import logging
import os
import shutil

async def capture_multiple(telnet_client, ftp_client):
    while True:
        number_of_captures = input("Enter number of captures: (type \"exit\" to exit)")
        if number_of_captures == "exit":
            break

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
            except Exception as e:
                logging.error(f"Failed to capture and send bmp: {e}")
