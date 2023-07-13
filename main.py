import asyncio
import logging
import os
from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop
from gui.my_gui import MyGUI

async def main():
    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Ensure 'logs' directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Clear existing handlers from the root logger
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Clear the log file
    open("logs/myapp.log", "w").close()

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create a stream handler for the console output (Info and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(console_handler)

    # create a file handler for the log file (Debug and above)
    file_handler = logging.FileHandler("logs/myapp.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)
    


    window = MyGUI()
    window.show()

    with loop:
        loop.run_forever()

if __name__ == '__main__':
    asyncio.run(main())

