"""
Logging configuration for structured JSON logging.
"""

import json
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .config import get_config


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "lineno", "funcName", "created",
                "msecs", "relativeCreated", "thread", "threadName",
                "processName", "process", "getMessage", "exc_info",
                "exc_text", "stack_info"
            }:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


def setup_logging() -> None:
    """Set up logging configuration."""
    config = get_config()
    log_config = config.get("logging", {})
    
    # Get log level
    level = getattr(logging, log_config.get("level", "INFO").upper())
    
    # Create logs directory
    log_file = Path(log_config.get("file", "logs/crypto_tax_calc.log"))
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Use simple format for console
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with JSON formatting
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=log_config.get("backup_count", 5)
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("binance").setLevel(logging.INFO)
    
    # Log configuration
    logger = logging.getLogger(__name__)
    logger.info("Logging configured", extra={
        "log_level": log_config.get("level", "INFO"),
        "log_file": str(log_file),
        "max_size": log_config.get("max_size", "10MB"),
        "backup_count": log_config.get("backup_count", 5)
    })


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


def log_task_start(task_id: str, task_name: str, **kwargs) -> None:
    """Log task start."""
    logger = get_logger("task")
    logger.info(f"Task {task_id} started: {task_name}", extra={
        "task_id": task_id,
        "task_name": task_name,
        "status": "started",
        **kwargs
    })


def log_task_complete(task_id: str, task_name: str, duration: float, **kwargs) -> None:
    """Log task completion."""
    logger = get_logger("task")
    logger.info(f"Task {task_id} completed: {task_name}", extra={
        "task_id": task_id,
        "task_name": task_name,
        "status": "completed",
        "duration_seconds": duration,
        **kwargs
    })


def log_task_error(task_id: str, task_name: str, error: Exception, **kwargs) -> None:
    """Log task error."""
    logger = get_logger("task")
    logger.error(f"Task {task_id} failed: {task_name}", extra={
        "task_id": task_id,
        "task_name": task_name,
        "status": "failed",
        "error_type": type(error).__name__,
        "error_message": str(error),
        **kwargs
    }, exc_info=True)


def log_api_call(service: str, endpoint: str, method: str, status_code: int, 
                 duration: float, **kwargs) -> None:
    """Log API call."""
    logger = get_logger("api")
    logger.info(f"API call: {method} {endpoint}", extra={
        "service": service,
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "duration_seconds": duration,
        **kwargs
    })


def log_data_operation(operation: str, table: str, count: int, **kwargs) -> None:
    """Log data operation."""
    logger = get_logger("data")
    logger.info(f"Data operation: {operation}", extra={
        "operation": operation,
        "table": table,
        "record_count": count,
        **kwargs
    })


def log_cgt_calculation(tax_year: int, total_gains: float, total_losses: float,
                       tax_due: float, **kwargs) -> None:
    """Log CGT calculation."""
    logger = get_logger("cgt")
    logger.info(f"CGT calculation for {tax_year}", extra={
        "tax_year": tax_year,
        "total_gains": total_gains,
        "total_losses": total_losses,
        "net_gains": total_gains - total_losses,
        "tax_due": tax_due,
        **kwargs
    })
