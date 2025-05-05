import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict

from app.core.config import settings

def setup_logging() -> None:
    """Configure logging for the application"""
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging_config = get_logging_config(settings)
    
    logging.config.dictConfig(logging_config)
    logging.captureWarnings(True)

def get_logging_config(settings: Any) -> Dict[str, Any]:
    """Generate logging configuration dictionary"""
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '''
                    asctime: %(asctime)s
                    name: %(name)s
                    levelname: %(levelname)s
                    message: %(message)s
                    pathname: %(pathname)s
                    lineno: %(lineno)d
                '''
            }
        },
        'handlers': {
            'console': {
                'level': settings.LOG_LEVEL,
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                'stream': sys.stdout
            },
            'file': {
                'level': settings.LOG_LEVEL,
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'json',
                'filename': Path(settings.LOG_DIR) / 'price_tracker.log',
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'json',
                'filename': Path(settings.LOG_DIR) / 'price_tracker_errors.log',
                'maxBytes': 10 * 1024 * 1024,
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file', 'error_file'],
                'level': settings.LOG_LEVEL,
                'propagate': True
            },
            'uvicorn.error': {
                'level': settings.LOG_LEVEL,
                'propagate': True
            },
            'uvicorn.access': {
                'level': settings.LOG_LEVEL,
                'propagate': True
            },
            'sqlalchemy.engine': {
                'level': 'INFO' if settings.DEBUG else 'WARNING',
                'propagate': False
            },
            'celery': {
                'level': 'INFO',
                'propagate': True
            }
        }
    }

class RequestIdFilter(logging.Filter):
    """Add request ID to log records"""
    def filter(self, record):
        from fastapi import Request
        from starlette_context import context
        
        request_id = context.get('request_id', 'no-request-id')
        record.request_id = request_id
        return True

def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance"""
    logger = logging.getLogger(name)
    logger.addFilter(RequestIdFilter())
    return logger