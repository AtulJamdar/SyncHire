import logging
import json
from datetime import datetime
from contextvars import ContextVar
from contextlib import contextmanager
from typing import Any
from config import settings

# Trace ID context variable, accessible from other modules
trace_id_context_var: ContextVar[str] = ContextVar("trace_id", default="")

@contextmanager
def trace_context(trace_id: str):
    """
    Context manager to set the trace ID context variable.
    """
    token = trace_id_context_var.set(trace_id)
    try:
        yield
    finally:
        trace_id_context_var.reset(token)

# Sensitive fields to redact from logs
SENSITIVE_FIELDS = {
    "password", "password_hash", "token", "access_token",
    "refresh_token", "api_key", "secret", "authorization",
    "x_telegram_bot_api_secret_token"
}

def redact_sensitive(data: Any) -> Any:
    """
    Recursively redacts sensitive fields from a dict or list.
    """
    if isinstance(data, dict):
        return {
            k: "[REDACTED]" if k.lower() in SENSITIVE_FIELDS else redact_sensitive(v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [redact_sensitive(item) for item in data]
    return data

class SensitiveFieldFilter(logging.Filter):
    """
    Filter that redacts sensitive information from log record attributes.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, "request_body"):
            record.request_body = redact_sensitive(record.request_body)
        
        # Redact any other dict or list attribute in the record
        for key in vars(record):
            if key not in ("message", "levelname", "msg", "args", "exc_info",
                           "exc_text", "stack_info", "name", "pathname",
                           "filename", "module", "lineno", "funcName",
                           "created", "msecs", "relativeCreated", "thread",
                           "threadName", "processName", "process"):
                val = getattr(record, key)
                if isinstance(val, (dict, list)):
                    setattr(record, key, redact_sensitive(val))
                    
        return True

class JSONFormatter(logging.Formatter):
    """
    Formatter that emits structured JSON logs.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "backend",
            "environment": settings.ENVIRONMENT,
            "message": record.getMessage(),
        }
        
        # Include trace_id if present in context
        trace_id = trace_id_context_var.get()
        if trace_id:
            log_data["trace_id"] = trace_id
            
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Merge any extra fields passed via logger.info("msg", extra={...})
        for key in vars(record):
            if key not in ("message", "levelname", "msg", "args", "exc_info",
                           "exc_text", "stack_info", "name", "pathname",
                           "filename", "module", "lineno", "funcName",
                           "created", "msecs", "relativeCreated", "thread",
                           "threadName", "processName", "process"):
                log_data[key] = getattr(record, key)
                
        return json.dumps(log_data)

def setup_logging():
    """
    Configures the root logger to use JSON formatting and the sensitive field filter.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    handler.addFilter(SensitiveFieldFilter())
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers to prevent duplicate logs
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
        
    root_logger.addHandler(handler)
    
    # Suppress noisy library loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
