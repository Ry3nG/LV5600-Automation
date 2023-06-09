from scripts import capture_and_send, change_preset, capture_and_send_performa
import asyncio
from Constants import Constants

# Global variables
IP_ADDRESS = "192.168.0.1"
USERNAME = "LV5600"
PASSWORD = "LV5600"

def main():
    asyncio.run(capture_and_send_performa.run(Constants.IP_ADDRESS_TELNET, Constants.USERNAME_TELNET, Constants.PASSWORD_TELNET, Constants.IP_ADDRESS_FTP, Constants.USERNAME_FTP, Constants.PASSWORD_FTP))
    
    # change preset, first prompt user
    #preset_number = input("Enter preset number: ")
    #asyncio.run(change_preset.run(IP_ADDRESS, USERNAME, PASSWORD, preset_number))

if __name__ == '__main__':
    main()