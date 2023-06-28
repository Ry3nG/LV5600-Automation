from commands import preset_command
import logging

async def recall_preset(telnet_client, preset_number):
    # convert preset_number to int if not already
    preset_number = int(preset_number)
    client = telnet_client
    # execute the command
    try:
        response = await client.send_command(preset_command.recall_preset(preset_number))
        logging.info("Recalled preset: " + str(preset_number))
    except Exception as e:
        logging.error(f"Failed to change preset: {e}")