import sys
import logging
import json
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
import os

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno
        }
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging():
    # Base configuration
    json_formatter = JsonFormatter()
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    if root_logger.handlers:
        root_logger.handlers = []
        
    root_logger.addHandler(console_handler)

    logging.info("Logging service initialized with JSON formatting (stdout only)")

def get_logger(name):
    return logging.getLogger(name)
