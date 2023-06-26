import logging
from commands import sys_command, wfm_command
from Constants import Constants
"""
    initialization sequence:
    1. SYS:INITIALIZE ALL
    2. WFM:LINE_SELECT ON
    3. WFM:LINE_NUMBER 580
    4. WFM:MATRIX:YCBCR RGB
    5. WFM:MODE:RGB:R OFF
    6. WFM:MODE:RGB:G ON
    7. WFM:MODE:RGB:B OFF
    8. WFM:CURSOR SINGLE
    9. WFM:CURSOR:DELTA 0
    10. WFM:CURSOR:REF 0
"""

async def lv5600_initialization(telnet_client):
    client = telnet_client
    # 1. SYS:INITIALIZE ALL
    try:
        response = await client.send_command(sys_command.system_initialize())
        logging.info("Initialized system")
    except Exception as e:
        raise LV5600InitializationError("Failed to initialize system")
    
    # 2. WFM:LINE_SELECT ON
    try:
        response = await client.send_command(wfm_command.wfm_line_select("ON"))
        logging.info("Turned on line select")
    except Exception as e:
        raise LV5600InitializationError("Failed to turn on line select")
    
    # 3. WFM:LINE_NUMBER 580
    try:
        response = await client.send_command(wfm_command.wfm_line_number(Constants.LINE_NUMBER))
        logging.info("Set line number to" + str(Constants.LINE_NUMBER))
    except Exception as e:
        raise LV5600InitializationError(f"Failed to set line number to {Constants.LINE_NUMBER}")
    
    # 4. WFM:MATRIX:YCBCR RGB
    try:
        response = await client.send_command(wfm_command.wfm_matrix_ycbcr("RGB"))
        logging.info("Set matrix to RGB")
    except Exception as e:
        raise LV5600InitializationError("Failed to set matrix to RGB")
    
    # 5. WFM:MODE:RGB:R OFF
    try:
        response = await client.send_command(wfm_command.wfm_mode_rgb("R", "OFF"))
        logging.info("Turned off R channel")
    except Exception as e:
        raise LV5600InitializationError("Failed to turn off R channel")
    
    # 6. WFM:MODE:RGB:G ON
    try:
        response = await client.send_command(wfm_command.wfm_mode_rgb("G", "ON"))
        logging.info("Turned on G channel")
    except Exception as e:
        raise LV5600InitializationError("Failed to turn on G channel")

    # 7. WFM:MODE:RGB:B OFF
    try:
        response = await client.send_command(wfm_command.wfm_mode_rgb("B", "OFF"))
        logging.info("Turned off B channel")
    except Exception as e:
        raise LV5600InitializationError("Failed to turn off B channel")
    
    # 8. WFM:CURSOR SINGLE
    try:
        response = await client.send_command(wfm_command.wfm_cursor("SINGLE"))
        logging.info("Set cursor to single")
    except Exception as e:
        raise LV5600InitializationError("Failed to set cursor to single")
    
    # 9. WFM:CURSOR:DELTA 0
    try:
        response = await client.send_command(wfm_command.wfm_cursor_height("Y","DELTA" , 0))
        logging.info("Set cursor delta to 0")
    except Exception as e:
        raise LV5600InitializationError("Failed to set cursor delta to 0")
    
    # 10. WFM:CURSOR:REF 0
    try:
        response = await client.send_command(wfm_command.wfm_cursor_height('Y', "REF" , 0))
        logging.info("Set cursor ref to 0")
    except Exception as e:
        raise LV5600InitializationError("Failed to set cursor ref to 0")

    # 11. WFM:CURSOR:UNIT:Y MV
    try:
        response = await client.send_command(wfm_command.wfm_cursor_unit("Y", "MV"))
        logging.info("Set cursor unit to MV")
    except Exception as e:
        raise LV5600InitializationError("Failed to set cursor unit to MV")

class LV5600InitializationError(Exception):
    pass