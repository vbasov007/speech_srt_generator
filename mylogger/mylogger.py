import logging
import os
import datetime

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED,
    'RED': RED,
    'GREEN': GREEN,
    'YELLOW': YELLOW,
    'BLUE': BLUE,
    'MAGENTA': MAGENTA,
    'CYAN': CYAN,
    'WHITE': WHITE,
}

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


class ColorFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        # can't do super(...) here because Formatter is an old school class
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname
        color = COLOR_SEQ % (30 + COLORS[levelname])
        message = logging.Formatter.format(self, record)
        message = message.replace("$RESET", RESET_SEQ) \
            .replace("$BOLD", BOLD_SEQ) \
            .replace("$COLOR", color)
        for k, v in COLORS.items():
            message = message.replace("$" + k, COLOR_SEQ % (v + 30)) \
                .replace("$BG" + k, COLOR_SEQ % (v + 40)) \
                .replace("$BG-" + k, COLOR_SEQ % (v + 40))
        return message + RESET_SEQ


def init_mylogger(*, debug_level=r'DEBUG',
                  # log_file_name='', log_folder_name='',
                  string_format=r'%(levelname)s %(asctime)s %(funcName)s: %(message)s',
                  color_string_format=r'$COLOR%(levelname)s $RESET %(relativeCreated)d %(funcName)s: %(message)s'):

    # if len(log_file_name) == 0:
    #     log_file_name = datetime.datetime.now().strftime("-%Y%m%d-%H%M%S") + ".log"
    #
    # if not os.path.exists(log_folder_name):
    #     os.mkdir(log_folder_name)

    # my_logger_path = os.path.join(log_folder_name, log_file_name)

    # my_logger = logging.getLogger(my_logger_path)
    my_logger = logging.getLogger('my_logger')

    if not my_logger.hasHandlers():
        level = debug_level

        my_logger.setLevel(level)

        my_logger.propagate = False

        # logger_file_handler = logging.FileHandler(my_logger_path)

        # logger_file_handler.setLevel(level)

        logger_console_handler = logging.StreamHandler()
        logger_console_handler.setLevel(level)

        logger_console_handler.setFormatter(ColorFormatter(color_string_format))
        # logger_file_handler.setFormatter(ColorFormatter(string_format))

        my_logger.addHandler(logger_console_handler)
        # my_logger.addHandler(logger_file_handler)

    return my_logger


mylog: logging.Logger = init_mylogger(
    # log_folder_name='logs'
)

