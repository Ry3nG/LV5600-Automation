import asyncio
import logging
import telnetlib3

class TelnetClient:
    def __init__(self, credential, command=None):
        self.credential = credential
        self.command = command
        self.wait_time = 0.1
        self.end_string = "$"
        self.timeout = 10 # seconds

    async def login(self, reader, writer):
        await reader.readuntil(b"login: ")
        writer.write(self.credential.username + "\r\n")
        await reader.readuntil(b"Password: ")
        writer.write(self.credential.password + "\r\n")
        await asyncio.sleep(self.wait_time)

    async def send_command(self, command=None):
        if command is not None:
            self.command = command

        try:
            reader, writer = await asyncio.wait_for(telnetlib3.open_connection(self.credential.ip_address, 23), timeout=self.timeout)
            await self.login(reader, writer)
            #logging.info("Sending command: %s", self.command)
            writer.write(self.command + "\r\n")
            #output = await asyncio.wait_for(reader.readuntil(self.end_string.encode('ascii')), timeout=self.timeout)
            #logging.info('Server output: %s', output.decode('ascii'))
        except asyncio.TimeoutError:
            logging.error("Timeout while connecting or executing the command")
        except Exception as e:
            logging.error("Failed to connect or execute the command. Error: %s", str(e))
