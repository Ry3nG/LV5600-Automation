from scripts import capture_and_send
import asyncio

# Global variables
IP_ADDRESS = "192.168.0.1"
USERNAME = "LV5600"
PASSWORD = "LV5600"

def main():
    asyncio.run(capture_and_send.run(IP_ADDRESS, USERNAME, PASSWORD))

if __name__ == '__main__':
    main()