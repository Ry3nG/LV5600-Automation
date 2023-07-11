from commands import command_utils
import logging
import constants

class LV5600Tasks:

    @staticmethod
    async def initialize_lv5600(telnet_client):
        response = None
        try:
            response = await telnet_client.send_command(command_utils.SYSCommand.system_initialize())
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error initializing LV5600: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error initializing LV5600: " + str(e))
    
        try:
            response = await telnet_client.send_command(command_utils.WFMCommand.wfm_line_select("ON"))
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error enabling waveform line: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error enabling waveform line: " + str(e))

        try:
            response = await telnet_client.send_command(command_utils.WFMCommand.wfm_line_number(constants.LV5600Constants.LINE_NUMBER))
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error setting waveform line number: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error setting waveform line number: " + str(e))
    
        try:
            response = await telnet_client.send_command(command_utils.WFMCommand.wfm_matrix_ycbcr("RGB"))
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error setting waveform matrix: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error setting waveform matrix: " + str(e))
        
        try:
            response = await telnet_client.send_command(command_utils.WFMCommand.wfm_mode_rgb("R","OFF"))
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error setting waveform mode: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error setting waveform mode: " + str(e))
        
        try:
            response = await telnet_client.send_command(command_utils.WFMCommand.wfm_mode_rgb("G","ON"))
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error setting waveform mode: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error setting waveform mode: " + str(e))

        try:
            response = await telnet_client.send_command(command_utils.WFMCommand.wfm_mode_rgb("B","OFF"))
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error setting waveform mode: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error setting waveform mode: " + str(e))
        
        try:
            response = await telnet_client.send_command(command_utils.WFMCommand.wfm_cursor("SINGLE"))
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error setting waveform cursor: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error setting waveform cursor: " + str(e))
        
        try:
            response = await telnet_client.send_command(command_utils.WFMCommand.wfm_cursor_height("Y","DELTA",0))
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error setting waveform cursor height: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error setting waveform cursor height: " + str(e))
        
        try:
            response = await telnet_client.send_command(command_utils.WFMCommand.wfm_cursor_height("Y","REF",0))
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error setting waveform cursor height: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error setting waveform cursor height: " + str(e))
        
        try:
            response = await telnet_client.send_command(command_utils.WFMCommand.wfm_cursor_unit("Y","MV"))
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error setting waveform cursor unit: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error setting waveform cursor unit: " + str(e))
        
    @staticmethod
    async def capture_n_send_bmp(telnet_client,ftp_client,file_path):
        response = None
        # capture
        try:
            response = await telnet_client.send_command(command_utils.CaptureCommand.take_snapshot())
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error capturing waveform: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error capturing waveform: " + str(e))
        
        # make
        try:
            response = await telnet_client.send_command(command_utils.CaptureCommand.make("CAP_BMP"))
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error making waveform: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error making waveform: " + str(e))

        # send
        try:
            ftp_client.get_file(constants.FTPConstants.FTP_FILE_NAME_BMP,file_path)
            logging.debug("File downloaded from FTP")
        except Exception as e:
            logging.error("Error downloading file from FTP: " + str(e))
            raise Exception("Error downloading file from FTP: " + str(e))

    @staticmethod
    async def recall_preset(telnet_client, preset_number):
        preset_number = int(preset_number)
        response = None
        try:
            response = await telnet_client.send_command(command_utils.PresetCommand.recall_preset(preset_number))
            logging.debug("The response is " + str(response))
        except Exception as e:
            logging.error("Error recalling preset: " + str(e))
            logging.debug("The response is " + str(response))
            raise Exception("Error recalling preset: " + str(e))

        
        
        