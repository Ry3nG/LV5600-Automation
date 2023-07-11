import logging
class LogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self,record):
        msg = self.format(record)
        self.text_widget.append(msg)