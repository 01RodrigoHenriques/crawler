"""
Sistema de logging estruturado
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import config


class ColoredFormatter(logging.Formatter):
    """Formatter com cores para output no terminal"""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(name: str, log_file: Optional[Path] = None) -> logging.Logger:
    """
    Configura logger com output no console e arquivo

    Args:
        name: Nome do logger
        log_file: Arquivo para guardar logs (opcional)

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    # Remover handlers existentes (evitar duplicatas)
    logger.handlers.clear()

    # Handler para console com cores
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))

    formatter: logging.Formatter
    if sys.stdout.isatty():  # Only colorize if terminal supports it
        formatter = ColoredFormatter(config.LOG_FORMAT)
    else:
        formatter = logging.Formatter(config.LOG_FORMAT)

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para arquivo (se especificado)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Sempre DEBUG em arquivo
        file_formatter = logging.Formatter(config.LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# Logger global
logger = setup_logger("crawler", config.LOG_FILE)
