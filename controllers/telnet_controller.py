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
        self.connection_timeout = 7
        
    async def login(self):
        try:
            if self.writer is not None and self.reader is not None:
                await self.reader.readuntil(b"login: ")
                self.writer.write(self.username + "\r\n")
                await self.reader.readuntil(b"Password: ")
                self.writer.write(self.password + "\r\n")
                await self.reader.readuntil(self.end_string)
            else:
                logging.error("Error logging in: writer or reader is None")
                return False
        except Exception as e:
            logging.error(f"Error logging in: {e}")
            return False
        return True

    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.wait_for(
                telnetlib3.open_connection(self.host, self.port),
                timeout=self.connection_timeout
            )
            return True
        except asyncio.TimeoutError:
            logging.error("Telnet connection timed out")
            return False
        except Exception as e:
            logging.error(f"Telnet connection failed: {e}")
            return False

    async def send_command(self, command):
        if self.writer is None or self.reader is None:
            logging.error("Error sending command: writer or reader is None")
            return None

        response = None
        try:
            self.writer.write(command + "\r\n")
            response = await self.reader.readuntil(self.end_string)
        except Exception as e:
            logging.error(f"Error sending command {command}: {e}")

        return response

    async def close(self):
        try:
            if self.writer is not None:
                self.writer.close()
            else:
                logging.error("Error closing connection: writer is None")
        except Exception as e:
            logging.error(f"Error closing connection: {e}")
