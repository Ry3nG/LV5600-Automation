import logging

class LogHandler(logging.Handler):
    def __init__(self, text_widget, log_level=logging.DEBUG):
        super().__init__()
        self.text_widget = text_widget
        self.setLevel(log_level)
        self.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.append(msg)

    def setup_application_logging(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(self)
