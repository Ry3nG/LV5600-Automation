import logging

async def send_command(telnet_client):
    response_log_list = []
    while True:
        command = input("Enter command: (type \"exit\" to exit) ")
        if command == "exit":
            return response_log_list
        try:
            response = await telnet_client.send_command(command)
            logging.info(f'Command "{command}" sent.')
            response_log_list.append(response)
        except Exception as e:
            logging.error(f'Failed to send command "{command}": {e}')
            logging.error("None critical error, continuing...")
            continue

