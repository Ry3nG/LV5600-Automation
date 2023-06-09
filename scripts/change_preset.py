from utils.telnet_client_performa import TelnetClientPerforma
from utils.credential import Credential
from commands import preset_command
import logging
from time import sleep

# configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def run(ip_address, username, password, preset_number):
    logging.info("Starting script: change_preset.py ...")

    # convert preset_number to int if not already
    preset_number = int(preset_number)

    # create a credential object
    uut_credential = Credential(ip_address, username, password)
    logging.info("1. Credential object created ---")

    # create a telnet client object
    client = TelnetClientPerforma(uut_credential)
    logging.info("2. Telnet client object created ---")

    # connect to the device
    await client.connect()

    # execute the command
    response = await client.send_command(preset_command.recall_preset(preset_number))
    logging.info("3. Preset %s recalled ---", preset_number)
    #log response
    logging.info("Response after recalling preset: %s", response)
    logging.info("Script: change_preset.py completed -------------")
