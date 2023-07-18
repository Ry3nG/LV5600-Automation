import asyncio
from typing import Optional
import telnetlib3
from constants import TelnetConstants
import logging

class TelnetController:

    def __init__(self,host,port,username,password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.reader = None
        self.writer = None
        self.end_string = TelnetConstants.TELNET_END_STRING
        self.connection_timeout = TelnetConstants.TELNET_CONNECTION_TIMEOUT
        
    async def login(self):
        try:
            if self.writer is not None and self.reader is not None:
                await self.reader.readuntil(b"login: ")
                self.writer.write(self.username + "\r\n")
                await self.reader.readuntil(b"Password: ")
                self.writer.write(self.password + "\r\n")
                await self.reader.readuntil(self.end_string)
            else:
                raise ConnectionError("Error logging in: writer or reader is None")
        except Exception as e:
            logging.error(f"Error while logging in: {str(e)}")
            raise Exception(f"Error while logging in: {str(e)}")

    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.wait_for(
                telnetlib3.open_connection(self.host, self.port),
                timeout=self.connection_timeout
            )
        except asyncio.TimeoutError:
            logging.error("Telnet connection timed out")
            raise ConnectionError("Telnet connection timed out")
        except Exception as e:
            raise Exception(f"Error while connecting to telnet: {str(e)}")

    async def send_command(self, command):
        if self.writer is None or self.reader is None:
            logging.error("Error sending command: writer or reader is None")
            raise ConnectionError("Error sending command: writer or reader is None")

        response = None
        try:
            self.writer.write(command + "\r\n")
            response = await asyncio.wait_for(self.reader.readuntil(self.end_string), timeout=self.connection_timeout)
        except Exception as e:
            logging.error(f"Error while sending command: {str(e)}")
            raise Exception(f"Error while sending command: {str(e)}")

        return response

    async def close(self):
        try:
            if self.writer is not None:
                self.writer.close()
            else:
                logging.warning("Writer is None")
                
        except ConnectionError as e:
            logging.error(f"Error while closing connection: {str(e)}")
            raise ConnectionError(f"Error while closing connection: {str(e)}")
        except Exception as e:
            logging.error(f"Error while closing connection: {str(e)}")
            raise Exception(f"Error while closing connection: {str(e)}")