import logging
import sys


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[36m",      # Cyan
        logging.INFO: "",       # Green
        logging.WARNING: "\033[33m",    # Yellow
        logging.ERROR: "\033[31m",      # Red
        logging.CRITICAL: "\033[41m",   # Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


def initialize_logging():
    logging.root.setLevel(logging.INFO)

    stream_formatter = ColorFormatter(
        '(%(filename)s:%(lineno)d): %(message)s'
    )

    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - (%(filename)s:%(lineno)d) - %(levelname)s\n%(message)s'
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(stream_formatter)

    file_handler = logging.FileHandler('error.log', mode='a')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(file_formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)