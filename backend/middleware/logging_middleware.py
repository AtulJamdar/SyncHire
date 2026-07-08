import uuid
import logging
from contextvars import ContextVar
from contextlib import contextmanager
from fastapi import Request

# Context variable for trace ID
trace_id_context_var: ContextVar[str] = ContextVar("trace_id", default="")

logger = logging.getLogger("logging_middleware")

@contextmanager
def trace_context(trace_id: str):
    token = trace_id_context_var.set(trace_id)
    try:
        yield
    finally:
        trace_id_context_var.reset(token)

async def logging_middleware(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    
    with trace_context(trace_id):
        logger.info(f"Request: {request.method} {request.url.path} - Trace ID: {trace_id}")
        response = await call_next(request)
        logger.info(f"Response: {request.method} {request.url.path} status={response.status_code} - Trace ID: {trace_id}")
        
    response.headers["X-Trace-ID"] = trace_id
    return response
