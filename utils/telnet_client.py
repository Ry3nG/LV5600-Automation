"""
This module provides a TelnetClient class that can connect to a remote host and execute commands using Telnet protocol.
"""
import asyncio
import logging
from typing import Optional
import telnetlib3

from Constants import Constants

class TelnetClient:
    """
    A class representing a Telnet client that can connect to a remote host and execute commands.
    """

    reader: Optional[telnetlib3.TelnetReader] = None
    writer: Optional[telnetlib3.TelnetWriter] = None

    def __init__(self, host, port, username, password):
        """
        Initializes a new instance of the TelnetClient class.

        Args:
            host (str): The hostname or IP address of the remote host.
            port (int): The port number to connect to on the remote host.
            username (str): The username to use for authentication.
            password (str): The password to use for authentication.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.reader = None
        self.writer = None
        self.end_string = Constants.TELNET_END_STRING

    async def connect(self):
        """
        Connects to the remote host using Telnet protocol.
        """
        try:
            self.reader, self.writer = await telnetlib3.open_connection(self.host, self.port)
            await self.login()
        except Exception as e:
            logging.error(f"Error while connecting: {e}")

    async def is_connected(self):
        """
        Checks if the Telnet client is currently connected to a remote host.

        Returns:
            bool: True if the client is connected, False otherwise.
        """
        return self.writer is not None and not self.reader is not None

    async def login(self):
        """
        Logs in to the remote host using the provided username and password.
        """
        try:
            if self.writer is not None and self.reader is not None:
                self.writer.write(self.username + '\r\n')
                await self.reader.readuntil(b'Password:')
                self.writer.write(self.password + '\r\n')
                await self.reader.readuntil(self.end_string)
            else:
                logging.error("Error while Login: writer or reader is None")
        except Exception as e:
            logging.error(f"Error while Login: {e}")

    async def send_command(self, command):
        """
        Sends a command to the remote host and returns the response.

        Args:
            command (str): The command to send to the remote host.

        Returns:
            str: The response from the remote host.
        """
        response = None
        if self.writer is not None and self.reader is not None:
            self.writer.write(command + '\r\n')
        else:
            logging.error("Error while sending command: writer or reader is None")
        try:
            if self.writer is not None and self.reader is not None:
                response = await self.reader.readuntil(self.end_string)
            else:
                logging.error("Error while sending command: writer or reader is None")
            
        except asyncio.IncompleteReadError:
            logging.error("Error while reading response: IncompleteReadError")
            # read some bytes 
            if self.writer is not None and self.reader is not None:
                response = await self.reader.read(20)
                logging.info(f"The response is: {response}")
            else:
                logging.error("Error while reading response: writer or reader is None")
        
        except Exception as e:
            logging.error(f"Error while reading response: {e}")
            response = None
            
        return response

    async def close(self):
        """
        Closes the connection to the remote host.
        """
        try:
            if self.writer is not None and self.reader is not None:
                self.writer.close()
            else:
                logging.error("Error while closing connection: writer or reader is None")
        
        except Exception as e:
            logging.error(f"Error while closing connection: {e}")

    async def run_in_terminal(self):
        """
        Runs the Telnet client in the terminal, allowing the user to enter commands and see the responses.
        """
        client = self
        try:
            await client.connect()
            while True:
                command = input("Enter a command (or 'quit' to quit): ")
                if command.lower() == 'quit':
                    break
                response = await client.send_command(command)
                if response:
                    print(response)
                else:
                    print("Error occurred while sending command.")
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            await client.close()
            print("Session terminated.")
