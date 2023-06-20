import logging

async def send_command(telnet_client):
    while True:
        command = input("Enter command: (type \"exit\" to exit) ")
        if command == "exit":
            break
        try:
            await telnet_client.send_command(command)
            logging.info(f'Command "{command}" sent.')
        except Exception as e:
            logging.error(f"Failed to send command: {e}")
