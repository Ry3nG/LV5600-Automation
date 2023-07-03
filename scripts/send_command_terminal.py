"""
    This module contains a function that sends a command to a telnet client and logs the response.
"""
import logging

async def send_command(telnet_client):
    """
    Sends a command to a telnet client and logs the response.

    Args:
        telnet_client: A telnet client object.

    Returns:
        A list of responses from the telnet client.
    """
    response_log_list = []
    while True:
        command = input("Enter command: (type \"exit\" to exit) ")
        if command == "exit":
            return response_log_list
        try:
            response = await telnet_client.send_command(command)
            logging.info(f'Command "{command}" sent.')
            response_log_list.append(response)
        except Exception as error:
            logging.error(f'Failed to send command "{command}": {error}')
            logging.error("None critical error, continuing...")
            continue
