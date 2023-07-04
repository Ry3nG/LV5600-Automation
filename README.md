# LV5600-Automation
### Introduction
A proof of concept project, to automate the LV5600 waveform monitor. The project establish telnet and ftp connection with the Leader LV5600 waveform monitor, enabling remote control and file retrival.

The project also utilizes Tensorflow.keras to train a CNN model to classify the waveform monitor's capture. 
```
.
├── App.py
├── Constants.py
├── README.md
├── commands
│   ├── __init__.py
│   ├── capture_command.py
│   ├── input_command.py
│   ├── preset_command.py
│   ├── sys_command.py
│   ├── wfm_command.py
├── output
│   ├── CAP_BMP.bmp
├── scripts
│   ├── __init__.py
│   ├── auto_tuning_use_peak_pixel.py
│   ├── capture_and_send_bmp.py
│   ├── capture_multiple.py
│   ├── display_saturation_result.py
│   ├── lv5600_initialization.py
│   ├── recall_preset.py
│   ├── send_command_terminal.py
│   ├── tune_to_target_light_level.py
├── utils
│   ├── __init__.py
│   ├── debug_console_controller.py
│   ├── ftp_client.py
│   ├── generate_directory.py
│   ├── peak_pixel_detection_util.py
│   ├── telnet_client.py
```