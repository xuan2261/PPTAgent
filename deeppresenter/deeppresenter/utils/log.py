import atexit
import functools
import inspect
import logging
import os
import platform
import sys
import time
import traceback
from collections.abc import Callable, Coroutine
from contextvars import ContextVar
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, ParamSpec, TypeVar, overload

import colorlog
from openai import (
    APIConnectionError,
    APIError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    ContentFilterFinishReasonError,
    InternalServerError,
    InvalidWebhookSignatureError,
    LengthFinishReasonError,
    NotFoundError,
    OpenAIError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
)
from pydantic import ValidationError

from deeppresenter.utils.constants import LOGGING_LEVEL

_context_logger: ContextVar[logging.Logger | None] = ContextVar(
    "_context_logger", default=None
)
P = ParamSpec("P")
R = TypeVar("R")

# Global file handler singleton
_global_file_handler: logging.Handler | None = None


def get_global_file_handler() -> logging.Handler:
    """Get or create the global file handler for unified logging."""
    global _global_file_handler
    if _global_file_handler is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"pptagent-{datetime.now().strftime('%Y%m%d')}.log"

        _global_file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        _global_file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(levelname)-4s %(asctime)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        _global_file_handler.setFormatter(formatter)
    return _global_file_handler


def log_startup(app_name: str = "PPTAgent") -> None:
    """Log application startup information."""
    logger = get_logger()
    logger.info("=" * 60)
    logger.info(f"{app_name} Starting")
    logger.info("=" * 60)
    logger.info(f"Python: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Working Dir: {Path.cwd()}")

    # Log key environment variables
    key_vars = ["LOG_LEVEL", "DEEPPRESENTER_LOG_LEVEL", "DEEPPRESENTER_WORKSPACE_BASE"]
    for var in key_vars:
        value = os.environ.get(var, "<not set>")
        logger.info(f"ENV {var}: {value}")

    logger.info("=" * 60)

    # Register shutdown handler
    atexit.register(_log_shutdown, app_name)


def _log_shutdown(app_name: str) -> None:
    """Log application shutdown."""
    logger = get_logger()
    logger.info("=" * 60)
    logger.info(f"{app_name} Shutdown Complete")
    logger.info("=" * 60)


def create_logger(
    name: str = __name__, log_file: str | Path | None = None
) -> logging.Logger:
    """Create a new logger"""
    assert name == "default logger" or name not in logging.Logger.manager.loggerDict, (
        f"Logger '{name}' already exists."
    )
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOGGING_LEVEL)
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-4s%(reset)s %(asctime)s [%(name)s] %(blue)s%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Attach global file handler for unified logging
    logger.addHandler(get_global_file_handler())

    if log_file is not None:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(levelname)-4s %(asctime)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def set_logger(name: str = __name__, log_file: str | Path | None = None):
    """Set a new logger for the current async context"""
    logger = _context_logger.get()
    assert logger is None or logger.name == "default logger", (
        "Context logger is already set."
    )
    logger = create_logger(name, log_file)
    logger.debug("Setting new context logger with loglevel=%s", LOGGING_LEVEL)
    _context_logger.set(logger)
    return logger


def get_logger() -> logging.Logger:
    """Get the logger for the current context"""

    ctx_logger = _context_logger.get()
    if ctx_logger is None:
        ctx_logger = create_logger("default logger")
        _context_logger.set(ctx_logger)
    return ctx_logger


def debug(msg, *args, **kwargs):
    get_logger().debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    get_logger().info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    get_logger().warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    get_logger().error(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    get_logger().critical(msg, *args, **kwargs)


def exception(msg, *args, **kwargs):
    get_logger().exception(msg, *args, **kwargs)


class timer:
    """Timer context manager and decorator"""

    def __init__(self, name: str = None):
        self.name = name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = time.time() - self.start_time
        if elapsed > 1:
            debug(f"{self.name} took {elapsed:.2f} seconds")

    @overload
    def __call__(
        self, func: Callable[P, Coroutine[Any, Any, R]]
    ) -> Callable[P, Coroutine[Any, Any, R]]: ...

    @overload
    def __call__(self, func: Callable[P, R]) -> Callable[P, R]: ...

    def __call__(self, func):
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.time()
                try:
                    return await func(*args, **kwargs)
                finally:
                    elapsed = time.time() - start
                    if elapsed > 1:
                        debug(
                            f"{self.name or func.__name__} took {elapsed:.2f} seconds"
                        )

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.time()
                try:
                    return func(*args, **kwargs)
                finally:
                    elapsed = time.time() - start
                    if elapsed > 1:
                        debug(
                            f"{self.name or func.__name__} took {elapsed:.2f} seconds"
                        )

            return sync_wrapper


def logging_openai_exceptions(identifider: str | Any, exc: Exception):
    """Log OpenAI exceptions"""
    if isinstance(exc, RateLimitError):
        msg = f"RateLimitError (HTTP 429): {str(exc)}"
    elif isinstance(exc, APITimeoutError):
        msg = f"APITimeoutError: {str(exc)}"
    elif isinstance(exc, APIConnectionError):
        msg = f"APIConnectionError: {str(exc)}"
    elif isinstance(exc, AuthenticationError):
        msg = f"AuthenticationError (HTTP 401): {str(exc)}"
    elif isinstance(exc, PermissionDeniedError):
        msg = f"PermissionDeniedError (HTTP 403): {str(exc)}"
    elif isinstance(exc, NotFoundError):
        msg = f"NotFoundError (HTTP 404): {str(exc)}"
    elif isinstance(exc, ConflictError):
        msg = f"ConflictError (HTTP 409): {str(exc)}"
    elif isinstance(exc, BadRequestError):
        msg = f"BadRequestError (HTTP 400): {str(exc)}"
    elif isinstance(exc, UnprocessableEntityError):
        msg = f"UnprocessableEntityError (HTTP 422): {str(exc)}"
    elif isinstance(exc, InternalServerError):
        msg = f"InternalServerError (HTTP 500): {str(exc)}"
    elif isinstance(exc, APIStatusError):
        code = getattr(exc, "status_code", "unknown")
        msg = f"APIStatusError (HTTP {code}): {str(exc)}"
    elif isinstance(exc, APIError):
        msg = f"APIError: {str(exc)}"
    elif isinstance(exc, APIResponseValidationError):
        msg = f"APIResponseValidationError: {str(exc)}"
    elif isinstance(exc, InvalidWebhookSignatureError):
        msg = f"InvalidWebhookSignatureError: {str(exc)}"
    elif isinstance(exc, ContentFilterFinishReasonError):
        msg = f"ContentFilterFinishReasonError: {str(exc)}"
    elif isinstance(exc, LengthFinishReasonError):
        msg = f"LengthFinishReasonError: {str(exc)}"
    elif isinstance(exc, OpenAIError):
        msg = f"OpenAIError: {str(exc)}"
    elif isinstance(exc, ValidationError):
        msg = f"Pydantic ValidationError: {str(exc)}"
    elif hasattr(exc, "http_status"):
        msg = f"OpenAI API Error {exc.http_status}: {str(exc)}"
    else:
        msg = f"Exception: {str(exc)}\n{traceback.format_exc()}"

    debug(f"{identifider} encountered {msg}")
    return msg
