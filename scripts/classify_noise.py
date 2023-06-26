import logging
from .recall_preset import recall_preset
from .capture_and_send_bmp import capture_and_send_bmp
from time import sleep
from utils.noise_classifier import NoiseClassifier

async def classify_noise(telnet_client, ftp_client, preset_number, file_path):
    try:
        await capture_and_send_bmp(telnet_client, ftp_client)
        logging.info("Captured and sent bmp.")
    except Exception as e:
        logging.error(f"Failed to capture and send bmp: {e}")

    NoiseClassifier_client = NoiseClassifier()
    result = NoiseClassifier_client.classify_image(file_path)

    return result
