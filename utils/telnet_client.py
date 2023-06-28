import asyncio
import logging
from typing import Optional
import telnetlib3

from Constants import Constants

class TelnetClient:
    reader: Optional[telnetlib3.TelnetReader] = None
    writer: Optional[telnetlib3.TelnetWriter] = None
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.reader = None
        self.writer = None
        self.end_string = Constants.TELNET_END_STRING

    async def connect(self):
        try:
            self.reader, self.writer = await telnetlib3.open_connection(self.host, self.port)
            await self.login()
        except Exception as e:
            logging.error(f"Error while connecting: {e}")

    async def is_connected(self):
        return self.writer is not None and not self.reader is not None

    async def login(self):
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
        try:
            if self.writer is not None and self.reader is not None:
                self.writer.close()
            else:
                logging.error("Error while closing connection: writer or reader is None")
        
        except Exception as e:
            logging.error(f"Error while closing connection: {e}")

    async def run_in_terminal(self):
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

'''
async def run():
    client = TelnetClient(Constants.IP_ADDRESS_TELNET, Constants.TELNET_PORT, Constants.USERNAME_TELNET, Constants.PASSWORD_TELNET)
    await client.connect()

    while True:
        command = input("Enter a command (or 'quit' to quit): ")
        if command.lower() == 'quit':
            break
        response = await client.send_command(command)
        print(response)

    print("Session terminated.")
    await client.close()

asyncio.run(run())
'''
