# LV5600-Automation
### Introduction
The LV5600 Automation project is a Proof-of-Concept project, aims to provice a set of tools and a graphical user interface for automated control and interaction with Leader LV5600 Waveform Monitor.

### Project structure
The project is structured as follows:
```
LV5600-Automation
|
├── .gitignore                    # Specifies files to be ignored by Git
├── README.md                     # This file
├── commands                      # Contains the command utilities for the system
│   ├── command_utils.py
│   └── __init__.py
|
├── config                        # Configuration related files and classes
│   ├── application_config.py     # Application configuration management
│   ├── config.ini                # Configuration values
│   └── __init__.py
|
├── constants.py                  # Stores constant values used throughout the project
|
├── controllers                   # Classes that control the interaction with the LV5600
│   ├── debug_console_controller.py
│   ├── ftp_controller.py
│   ├── ftp_session_controller.py
│   ├── telnet_controller.py
│   └── __init__.py
|
├── gui                           # Contains the code for the graphical user interface
│   ├── ftp_settings_dialog.py    # GUI for the FTP settings dialog
│   ├── log_handler.py            # Handles the logging in the GUI
│   ├── my_gui.py                 # Main GUI class
│   ├── resources                 # Resources used by the GUI
│   │   ├── LV5600-Automation-GUI.ui  # QtDesigner file for GUI layout
│   │   └── icon.svg                  # Icon for the GUI
│   ├── telnet_settings_dialog.py # GUI for the Telnet settings dialog
│   └── __init__.py
|
├── logs                          # Log related files
│   ├── myapp.log                 # Log file
│   ├── snapshot.bmp              # Sample snapshot image
│   └── __init__.py
|
├── main.py                       # Entry point for the application
|
└── tasks                         # Task classes for LV5600 automation
    ├── auto_tuning.py
    ├── capture_and_send_bmp.py
    ├── display_saturation_result.py
    ├── lv5600_tasks.py
    ├── task_util.py
    └── __init__.py
```
### Installation and Running
1. Make sure to have Python 3.7+ installed
2. Clone the repository
3. Navigate to the project directory
4. Start a virtual environment using `python -m venv venv`, then activate it using `venv\Scripts\activate.bat` or `source venv/bin/activate` on Linux
5. Install the required packages using `pip install -r requirements.txt`
6. Run the application using `python main.py`

### Configuration
The application configuration is stored in `config/config.ini`, it includes default settings for Telnet and FTP Servers, as well as the default path for the snapshot image.


