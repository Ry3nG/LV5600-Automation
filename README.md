# LV5600-Automation
[![Python application build](https://github.com/Ry3nG/LV5600-Automation/actions/workflows/main.yml/badge.svg)](https://github.com/Ry3nG/LV5600-Automation/actions/workflows/main.yml)
### Introduction
The LV5600 Automation project is a Proof-of-Concept project, aims to provice a set of tools and a graphical user interface for automated control and interaction with Leader LV5600 Waveform Monitor.

### Project structure
The project is structured as follows:
```
|---LV5600-Automation
|   |---.gitignore
|   |---.vscode
|   |   |---settings.json
|   |---README.md
|   |---__init__.py
|   |---commands
|   |   |---__init__.py
|   |   |---command_utils.py
|   |---config
|   |   |---__init__.py
|   |   |---application_config.py       
|   |   |---config.ini
|   |---constants.py
|   |---controllers
|   |   |---__init__.py
|   |   |---debug_console_controller.py 
|   |   |---ftp_controller.py
|   |   |---ftp_session_controller.py   
|   |   |---telnet_controller.py        
|   |---gui
|   |   |---__init__.py
|   |   |---ftp_settings_dialog.py      
|   |   |---log_handler.py
|   |   |---my_gui.py
|   |   |---resources
|   |   |   |---LV5600-Automation-GUI.ui
|   |   |   |---icon.svg
|   |   |---telnet_settings_dialog.py   
|   |---logs
|   |   |---__init__.py
|   |   |---myapp.log
|   |   |---snapshot.bmp
|   |---main.py
|   |---tasks
|   |   |---__init__.py
|   |   |---calculation_tasks.py
|   |   |---lv5600_tasks.py
```
### Important files
Some of the most important files to understand include:

* ``main.py``: This is the entry point to the application. It initializes and launches the GUI.

* ``my_gui.py`` located in the **gui** folder: This is where the GUI logic is handled, including button actions and the behavior of other UI elements. This file also includes the core logic of the application, and each of the actions are linked with corresponding tasks or functions in the controller classes.

* ``telnet_controller.py``, ``ftp_controller.py`` and `debug_console_controller.py`` located in the **controllers** folder: These files manage the interactions between the application and external services like Telnet, FTP, and the Debug Console. Changes to how the application interacts with these services would be made here.

* ``lv5600_tasks.py`` and ``calculation_tasks.py`` located in the **tasks** folder: These files define the tasks or actions that the application can perform. If you want to add new functionality to the application, you would likely need to add new tasks here.

* ``application_config.py`` located in the **config** folder: This file handles the reading and writing of the configuration file (config.ini). Any changes to how the application saves or retrieves its settings would be made here.
### Installation and Running
1. Make sure to have Python 3.7+ installed
2. Clone the repository
3. Navigate to the project directory
4. Start a virtual environment using `python -m venv venv`, then activate it using `venv\Scripts\activate.bat` or `source venv/bin/activate` on Linux
5. Install the required packages using `pip install -r requirements.txt`
6. Run the application using `python main.py`

### Configuration
The application configuration is stored in `config/config.ini`, it includes default settings for Telnet and FTP Servers, as well as the default path for the snapshot image.


