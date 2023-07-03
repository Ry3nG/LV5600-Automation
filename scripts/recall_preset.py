"""
This module contains the function to recall a preset on a Leader LV5600 device.

Functions:
- recall_preset: recalls a preset on a Leader LV5600 device.
"""
import logging
from commands import preset_command

async def recall_preset(telnet_client, preset_number):
    """
    Recalls a preset on a Leader LV5600 device.

    Args:
    - telnet_client: a TelnetClient instance connected to the Leader LV5600 device.
    - preset_number: the number of the preset to recall.

    Returns:
    - The response from the device after recalling the preset.
    """
    # convert preset_number to int if not already
    preset_number = int(preset_number)
    client = telnet_client
    response = await client.send_command(preset_command.recall_preset(preset_number))
    logging.info("Recalled preset: " + str(preset_number))
    return response
