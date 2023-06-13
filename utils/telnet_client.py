import asyncio
import logging
import telnetlib3

from Constants import Constants

class TelnetClient:
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

    async def login(self):
        try:
            self.writer.write(self.username + '\r\n')
            await self.reader.readuntil(b'Password:')
            self.writer.write(self.password + '\r\n')
            await self.reader.readuntil(self.end_string)
        except Exception as e:
            logging.error(f"Error while Login: {e}")


    async def send_command(self, command):
        self.writer.write(command + '\r\n')
        try:
            response = await self.reader.readuntil(self.end_string)
            
        except asyncio.IncompleteReadError:
            logging.error("Error while reading response: IncompleteReadError")
            # read some bytes 
            response = await self.reader.read(20)
            logging.info(f"The response is: {response}")
        
        except Exception as e:
            logging.error(f"Error while reading response: {e}")
            response = None
            
        return response

    async def close(self):
        try:
            self.writer.close()
        
        except Exception as e:
            logging.error(f"Error while closing connection: {e}")

    async def run_in_terminal(telnet_client):
        client = telnet_client
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
