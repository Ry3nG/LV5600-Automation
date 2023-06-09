# utils/telnet_client.py
import asyncio
import logging
import telnetlib3

class TelnetClientPerforma:
    def __init__(self, credential):
        self.credential = credential
        self.wait_time = 0.1
        self.end_string = "$"
        self.timeout = 10 # seconds
        self.reader = None
        self.writer = None

    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.wait_for(telnetlib3.open_connection(self.credential.ip_address, 23), timeout=self.timeout)
            await self.login(self.reader, self.writer)
        except Exception as e:
            logging.error("Failed to connect. Error: %s", str(e))

    async def login(self, reader, writer):
        await reader.readuntil(b"login: ")
        writer.write(self.credential.username + "\r\n")
        await reader.readuntil(b"Password: ")
        writer.write(self.credential.password + "\r\n")
        await asyncio.sleep(self.wait_time)

    async def send_command(self, command):
        if self.writer is None:
            raise Exception("No connection established")
        self.writer.write(command + "\r\n")
        await self.writer.drain()  # Ensure the command is sent
        response = await self.reader.readuntil(self.end_string.encode('ascii'))  # Wait for response
        return response