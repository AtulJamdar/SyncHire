import uuid
import logging
from fastapi import Request
from core.logging import trace_context

logger = logging.getLogger("logging_middleware")

async def logging_middleware(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    
    with trace_context(trace_id):
        logger.info(f"Request: {request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"Response: {request.method} {request.url.path} status={response.status_code}")
        
    response.headers["X-Trace-ID"] = trace_id
    return response
