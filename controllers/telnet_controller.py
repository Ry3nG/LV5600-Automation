import asyncio
from typing import Optional
import telnetlib3
from Constants import TelnetConstants
import logging


class TelnetController:
    """
    A class that handles Telnet connections and commands.

    Attributes:
        host (str): The IP address or hostname of the Telnet server.
        port (int): The port number of the Telnet server.
        username (str): The username to use for authentication.
        password (str): The password to use for authentication.
        reader (Optional[telnetlib3.StreamReader]): The Telnet reader object.
        writer (Optional[telnetlib3.StreamWriter]): The Telnet writer object.
        end_string (bytes): The string that marks the end of a Telnet response.
        connection_timeout (float): The maximum time to wait for a Telnet connection.
    """

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.reader = None
        self.writer = None
        self.end_string = TelnetConstants.TELNET_END_STRING
        self.connection_timeout = TelnetConstants.TELNET_CONNECTION_TIMEOUT

    async def login(self):
        """
        Logs in to the Telnet server using the provided username and password.
        If the writer or reader is None, raises a ConnectionError.
        """
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
            raise Exception(f"Error while logging in: {str(e)}")

    async def connect(self):
        """
        Connects to the Telnet server using the provided host and port.
        If the connection times out, raises a ConnectionError.
        """
        try:
            self.reader, self.writer = await asyncio.wait_for(
                telnetlib3.open_connection(self.host, self.port),
                timeout=self.connection_timeout,
            )
        except asyncio.TimeoutError:
            raise ConnectionError("Telnet connection timed out")
        except Exception as e:
            raise Exception(f"Error while connecting to telnet: {str(e)}")

    async def send_command(self, command):
        """
        Sends a command to the Telnet server and returns the response.
        If the writer or reader is None, raises a ConnectionError.
        If the command times out, raises a TimeoutError.
        """
        if self.writer is None or self.reader is None:
            raise ConnectionError("Error sending command: writer or reader is None")

        response = None
        try:
            self.writer.write(command + "\r\n")
            response = await asyncio.wait_for(
                self.reader.readuntil(self.end_string), timeout=self.connection_timeout
            )
        except Exception as e:
            raise Exception(f"Error while sending command: {str(e)}")

        return response

    async def close(self):
        """
        Closes the Telnet connection.
        If the writer is None, raises a ConnectionError.
        """
        try:
            if self.writer is not None:
                self.writer.close()
            else:
                logging.warning("Writer is None")

        except ConnectionError as e:
            raise ConnectionError(f"Error while closing connection: {str(e)}")
        except Exception as e:
            raise Exception(f"Error while closing connection: {str(e)}")
