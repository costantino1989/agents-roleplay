import logging
import sys

# ANSI escape codes for colors
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
WHITE = "\033[37m"

class ColoredFormatter(logging.Formatter):
    """
    Custom formatter to add colors to log levels.
    """
    
    # Format: [Level] [Module:Line] Message
    # We use %(filename)s:%(lineno)d for file and line. 
    # If wrapped in a class, standard logging doesn't easily capture class name automatically 
    # without passing 'extra', but filename is a good proxy.
    FORMAT = "%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s"

    FORMATS = {
        logging.DEBUG: BLUE + FORMAT + RESET,
        logging.INFO: GREEN + FORMAT + RESET,
        logging.WARNING: YELLOW + FORMAT + RESET,
        logging.ERROR: RED + FORMAT + RESET,
        logging.CRITICAL: RED + "\033[1m" + FORMAT + RESET,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMAT)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)

def get_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    """
    Returns a logger with the specified name and level, using the ColoredFormatter.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Check if handler already exists to avoid duplicate logs
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)
        
        # Prevent propagation to root logger if it has its own handlers
        logger.propagate = False

    return logger
