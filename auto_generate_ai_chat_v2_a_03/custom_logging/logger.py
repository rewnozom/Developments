import os
import re
import sys
import traceback
from datetime import datetime
from functools import wraps
from typing import Literal, Mapping
import logging as python_logging
from flask import request  # Importing request from Flask

# Assuming the configuration is now handled within this module or another appropriate way
class Config:
    def __init__(self):
        self.disable_color = False
        self.debug = True
        self.log_dir = os.path.join(os.getcwd(), 'logs')

    def get_logs_dir(self):
        return self.log_dir

    def get_logging_rest_api(self):
        return True

config = Config()

DISABLE_COLOR_PRINTING = config.disable_color

ColorType = Literal[
    'red', 'green', 'yellow', 'blue', 'magenta', 'cyan',
    'light_grey', 'dark_grey', 'light_red', 'light_green',
    'light_yellow', 'light_blue', 'light_magenta', 'light_cyan', 'white',
]

LOG_COLORS: Mapping[str, ColorType] = {
    'BACKGROUND LOG': 'blue',
    'ACTION': 'green',
    'OBSERVATION': 'yellow',
    'DETAIL': 'cyan',
    'ERROR': 'red',
    'PLAN': 'light_magenta',
}

class ColoredFormatter(python_logging.Formatter):
    def format(self, record):
        msg_type = record.__dict__.get('msg_type', None)
        if msg_type in LOG_COLORS and not DISABLE_COLOR_PRINTING:
            msg_type_color = f"\033[{LOG_COLORS[msg_type]}m{msg_type}\033[0m"
            msg = f"\033[{LOG_COLORS[msg_type]}m{record.msg}\033[0m"
            time_str = f"\033[{LOG_COLORS[msg_type]}m{self.formatTime(record, self.datefmt)}\033[0m"
            name_str = f"\033[{LOG_COLORS[msg_type]}m{record.name}\033[0m"
            level_str = f"\033[{LOG_COLORS[msg_type]}m{record.levelname}\033[0m"
            if msg_type in ['ERROR']:
                return f'{time_str} - {name_str}:{level_str}: {record.filename}:{record.lineno}\n{msg_type_color}\n{msg}'
            return f'{time_str} - {msg_type_color}\n{msg}'
        elif msg_type == 'STEP':
            msg = '\n\n==============\n' + record.msg + '\n'
            return f'{msg}'
        return super().format(record)

console_formatter = ColoredFormatter(
    '\033[92m%(asctime)s - %(name)s:%(levelname)s\033[0m: %(filename)s:%(lineno)s - %(message)s',
    datefmt='%H:%M:%S',
)

file_formatter = python_logging.Formatter(
    '%(asctime)s - %(name)s:%(levelname)s: %(filename)s:%(lineno)s - %(message)s',
    datefmt='%H:%M:%S',
)

llm_formatter = python_logging.Formatter('%(message)s')

class SensitiveDataFilter(python_logging.Filter):
    def filter(self, record):
        sensitive_patterns = [
            'api_key', 'jwt_secret', 'ssh_password',
        ]

        env_vars = [attr.upper() for attr in sensitive_patterns]
        sensitive_patterns.extend(env_vars)

        sensitive_patterns.append('JWT_SECRET')
        sensitive_patterns.append('LLM_API_KEY')

        msg = record.getMessage()
        record.args = ()

        for attr in sensitive_patterns:
            pattern = rf"{attr}='?([\w-]+)'?"
            msg = re.sub(pattern, f"{attr}='******'", msg)

        record.msg = msg
        return True

def get_console_handler():
    console_handler = python_logging.StreamHandler()
    console_handler.setLevel(python_logging.INFO)
    console_handler.setFormatter(console_formatter)
    return console_handler

def get_file_handler(log_dir=None):
    log_dir = config.get_logs_dir() if log_dir is None else log_dir
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d')
    file_name = f'log_{timestamp}.log'
    file_handler = python_logging.FileHandler(os.path.join(log_dir, file_name))
    if config.debug:
        file_handler.setLevel(python_logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    return file_handler

python_logging.basicConfig(level=python_logging.ERROR)

def log_uncaught_exceptions(ex_cls, ex, tb):
    python_logging.error(''.join(traceback.format_tb(tb)))
    python_logging.error('{0}: {1}'.format(ex_cls, ex))

sys.excepthook = log_uncaught_exceptions

logger = python_logging.getLogger('logger')
logger.setLevel(python_logging.INFO)
logger.addHandler(get_file_handler())
logger.addHandler(get_console_handler())
logger.addFilter(SensitiveDataFilter(logger.name))
logger.propagate = False
logger.debug('Logging initialized')
logger.debug('Logging to %s', os.path.join(os.getcwd(), 'logs', 'log.log'))

class LlmFileHandler(python_logging.FileHandler):
    def __init__(self, filename, mode='a', encoding='utf-8', delay=False):
        self.filename = filename
        self.message_counter = 1
        if config.debug:
            self.session = datetime.now().strftime('%y-%m-%d_%H-%M')
        else:
            self.session = 'default'
        self.log_directory = os.path.join(os.getcwd(), 'logs', 'llm', self.session)
        os.makedirs(self.log_directory, exist_ok=True)
        if not config.debug:
            for file in os.listdir(self.log_directory):
                file_path = os.path.join(self.log_directory, file)
                try:
                    os.unlink(file_path)
                except Exception as e:
                    logger.error('Failed to delete %s. Reason: %s', file_path, e)
        filename = f'{self.filename}_{self.message_counter:03}.log'
        self.baseFilename = os.path.join(self.log_directory, filename)
        super().__init__(self.baseFilename, mode, encoding, delay)

    def emit(self, record):
        filename = f'{self.filename}_{self.message_counter:03}.log'
        self.baseFilename = os.path.join(self.log_directory, filename)
        self.stream = self._open()
        super().emit(record)
        self.stream.close()
        logger.debug('Logging to %s', self.baseFilename)
        self.message_counter += 1

def _get_llm_file_handler(name, debug_level=python_logging.DEBUG):
    llm_file_handler = LlmFileHandler(name, delay=True)
    llm_file_handler.setFormatter(llm_formatter)
    llm_file_handler.setLevel(debug_level)
    return llm_file_handler

def _setup_llm_logger(name, debug_level=python_logging.DEBUG):
    llm_logger = python_logging.getLogger(name)
    llm_logger.propagate = False
    llm_logger.setLevel(debug_level)
    llm_logger.addHandler(_get_llm_file_handler(name, debug_level))
    return llm_logger

llm_prompt_logger = _setup_llm_logger('prompt', python_logging.DEBUG)
llm_response_logger = _setup_llm_logger('response', python_logging.DEBUG)

class Logger:
    def __init__(self, filename="devika_agent.log"):
        logs_dir = config.get_logs_dir()
        self.logger = python_logging.getLogger("app_logger")
        handler = python_logging.FileHandler(filename=os.path.join(logs_dir, filename))
        handler.setFormatter(file_formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(python_logging.DEBUG)

    def read_log_file(self) -> str:
        with open(self.logger.handlers[0].baseFilename, "r") as file:
            return file.read()

    def info(self, message: str):
        self.logger.info(message)
        self.logger.flush()

    def error(self, message: str):
        self.logger.error(message)
        self.logger.flush()

    def warning(self, message: str):
        self.logger.warning(message)
        self.logger.flush()

    def debug(self, message: str):
        self.logger.debug(message)
        self.logger.flush()

    def exception(self, message: str):
        self.logger.exception(message)
        self.logger.flush()

def route_logger(app_logger: Logger):
    log_enabled = config.get_logging_rest_api()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if log_enabled:
                app_logger.info(f"{request.path} {request.method}")
            response = func(*args, **kwargs)
            from werkzeug.wrappers import Response
            try:
                if log_enabled:
                    if isinstance(response, Response) and response.direct_passthrough:
                        app_logger.debug(f"{request.path} {request.method} - Response: File response")
                    else:
                        response_summary = response.get_data(as_text=True)
                        if 'settings' in request.path:
                            response_summary = "*** Settings are not logged ***"
                        app_logger.debug(f"{request.path} {request.method} - Response: {response_summary}")
            except Exception as e:
                app_logger.exception(f"{request.path} {request.method} - {e})")
            return response
        return wrapper
    return decorator