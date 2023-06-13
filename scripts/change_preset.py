from commands import preset_command
import logging

# configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def run(telnet_client, preset_number):
    # convert preset_number to int if not already
    preset_number = int(preset_number)
    client = telnet_client
    # execute the command
    response = await client.send_command(preset_command.recall_preset(preset_number))
