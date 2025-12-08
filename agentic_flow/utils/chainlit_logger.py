"""
Simplified logging for Chainlit with per-session logging support.

Chainlit maintains persistent WebSocket connections, so we don't need
complex thread-local storage. Each session has its own logger stored
in cl.user_session.
"""

import logging
import os
from pathlib import Path
from datetime import datetime
import chainlit as cl


class ChainlitLogger:
    """Manages session-specific logging for Chainlit applications."""

    @staticmethod
    def create_session_logger(
        session_id: str,
        log_base_dir: str = "logs",
        log_level: int = logging.INFO
    ) -> logging.Logger:
        """
        Create a session-specific logger for Chainlit.

        Args:
            session_id: Unique session identifier (from Chainlit)
            log_base_dir: Base directory for log files
            log_level: Logging level (default: INFO)

        Returns:
            logging.Logger: Session-specific logger
        """
        # Create unique logger name
        logger_name = f"chainlit_session_{session_id}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.propagate = False

        # Clear any existing handlers
        if logger.handlers:
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)

        # Create log directory structure
        timestamp = datetime.now().strftime("%Y-%m-%d")
        log_dir = Path(log_base_dir) / timestamp
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create log file path
        log_filename = f"user_{cl.user_session.get('user').identifier}_{datetime.now().strftime('%H-%M-%S')}.log"
        log_file_path = log_dir / log_filename

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - [%(levelname)s] - %(filename)s - %(funcName)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler (optional - useful for debugging)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logger.info(f"Logger initialized for session {session_id[:8]}")
        logger.info(f"Log file: {log_file_path}")

        # File handler
        file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    @staticmethod
    def get_current_logger() -> logging.Logger:
        """
        Get the logger for the current Chainlit session.

        Returns:
            logging.Logger: Current session's logger or default logger
        """
        try:
            logger = cl.user_session.get("logger")
            if logger:
                return logger
        except Exception:
            pass

        # Fallback to root logger
        return logging.getLogger("chainlit_default")


# Convenience functions that automatically use the current session's logger
def log_info(message: str, *args, **kwargs):
    """Log info message for current session."""
    logger = ChainlitLogger.get_current_logger()
    logger.info(message, stacklevel=2, *args, **kwargs)


def log_warning(message: str, *args, **kwargs):
    """Log warning message for current session."""
    logger = ChainlitLogger.get_current_logger()
    logger.warning(message, *args, **kwargs)


def log_error(message: str, *args, **kwargs):
    """Log error message for current session."""
    logger = ChainlitLogger.get_current_logger()
    logger.error(message, *args, **kwargs)


def log_debug(message: str, *args, **kwargs):
    """Log debug message for current session."""
    logger = ChainlitLogger.get_current_logger()
    logger.debug(message, *args, **kwargs)


def log_critical(message: str, *args, **kwargs):
    """Log critical message for current session."""
    logger = ChainlitLogger.get_current_logger()
    logger.critical(message, *args, **kwargs)